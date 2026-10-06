#!/usr/bin/env python3
"""Builds design-kit brand mark boards from option SVGs, so an agent never hand-writes the HTML.

For each option it writes a reversed SVG, a compact screening strip (16, 32 and 64 px, reversed,
one colour and blurred) and, on request, a full test sheet. It then writes one blind board.html
with the options in shuffled order beside the current mark, at their real tab, header and footer
sizes. PNGs come from the Playwright CLI driving an installed Chrome, then headless Chrome, and
otherwise are reported as Unverified.

Usage: board.py --out DIR [--before current.svg] [--sheets A,B|all] A.svg B.svg C.svg
The script prints one line per file it wrote, so the caller needs no screenshots to know the result.
"""
import argparse
import html
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHROME_PATHS = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'google-chrome',
                'google-chrome-stable', 'chromium', 'chromium-browser']

STYLE = '''body { margin: 20px; font: 13px system-ui, sans-serif; color: #222; background: #fff; }
h1 { font-size: 18px; margin: 0 0 12px; } h2 { font-size: 13px; margin: 18px 0 8px; color: #555; }
.row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.tile { display: grid; place-items: center; width: 100px; height: 100px; border: 1px solid #ddd; }
.tile img { width: 60px; height: 60px; }
.dark { background: #111; } .brand { background: var(--brand); } .footer { background: var(--footer); }
.photo { background: linear-gradient(135deg, #b08968, #3e5c4a 60%, #1d2b2f); }
.black img { filter: brightness(0); } .white img { filter: brightness(0) invert(1); } .blur img { filter: blur(2px); }
.mask { display: grid; place-items: center; width: 108px; height: 108px; background: #e9e9e9; overflow: hidden; position: relative; }
.mask img { width: 66px; height: 66px; } .circle { border-radius: 50%; } .squircle { border-radius: 24px; }
.safe::after { content: ""; position: absolute; inset: 21px; border: 1px dashed #d33; border-radius: 50%; }
.tab { display: flex; align-items: center; gap: 8px; width: 200px; padding: 8px 12px; border-radius: 8px 8px 0 0; background: #dee1e6; }'''


def parse(argv):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('options', nargs='+', help='option SVGs, labelled by file stem such as A.svg')
    parser.add_argument('--out', required=True, help='iteration folder that receives every output')
    parser.add_argument('--before', help='SVG of the current mark, shown first on the board')
    parser.add_argument('--mark-colour', default='#00563F', help='mark colour that the reversed version replaces')
    parser.add_argument('--reverse-colour', default='#FFFFFF', help='colour used for reversed versions')
    parser.add_argument('--brand', default=None, help='brand background for tiles, defaults to the mark colour')
    parser.add_argument('--footer', default='#003E2E', help='dark ground for the footer row')
    parser.add_argument('--wordmark', default='', help='name shown beside the mark in tab, header and footer rows')
    parser.add_argument('--font', help='font file for the wordmark, such as the project Sora file')
    parser.add_argument('--weight', default='800', help='wordmark font weight')
    parser.add_argument('--title', default='Brand mark options', help='board heading')
    parser.add_argument('--sheets', default='', help='comma list of labels, or all, that also get full test sheets')
    parser.add_argument('--seed', type=int, default=None, help='shuffle seed for the blind order')
    parser.add_argument('--no-render', action='store_true', help='write HTML only and report PNGs as Unverified')
    parser.add_argument('--board-png', action='store_true', help='also render board.png, which is for people')
    return parser.parse_args(argv)


def reversed_svg(text, mark, reverse):
    return re.sub(re.escape(mark), reverse, text, flags=re.I)


def strip_html(label, svg, rev, brand, footer):
    return f'''<!doctype html><meta charset="utf-8"><style>:root {{ --brand: {brand}; --footer: {footer}; }}
{STYLE} body {{ margin: 8px; }}</style>
<div class="row"><strong>{html.escape(label)}</strong><img src="{svg}" width="16"><img src="{svg}" width="32"><img src="{svg}" width="64">
<div class="tile footer"><img src="{rev}"></div><div class="tile"><img class="black" src="{svg}" style="filter:brightness(0)"></div>
<div class="tile blur"><img src="{svg}"></div></div>'''


def sheet_html(label, svg, rev, brand, footer):
    sizes = ''.join(f'<img src="{svg}" width="{s}">' for s in (16, 24, 32, 48, 64, 128, 180))
    return f'''<!doctype html><meta charset="utf-8"><title>{html.escape(label)} test sheet</title>
<style>:root {{ --brand: {brand}; --footer: {footer}; }} {STYLE}</style><h1>{html.escape(label)}</h1>
<h2>Sizes 16, 24, 32, 48, 64, 128 and 180 px</h2><div class="row">{sizes}</div>
<h2>Light, dark, brand, footer, photo, one colour black, one colour white, blurred</h2><div class="row">
<div class="tile"><img src="{svg}"></div><div class="tile dark"><img src="{rev}"></div><div class="tile brand"><img src="{rev}"></div>
<div class="tile footer"><img src="{rev}"></div><div class="tile photo"><img src="{rev}"></div><div class="tile black"><img src="{svg}"></div>
<div class="tile dark white"><img src="{svg}"></div><div class="tile blur"><img src="{svg}"></div></div>
<h2>Android circle and squircle with the 66 dp safe zone, iOS rounded square, maskable circle</h2><div class="row">
<div class="mask circle safe"><img src="{svg}"></div><div class="mask squircle safe"><img src="{svg}"></div>
<div class="mask squircle"><img src="{svg}" style="width:96px;height:96px"></div><div class="mask circle"><img src="{svg}" style="width:80px;height:80px"></div></div>
<h2>In a browser tab</h2><div class="row"><div class="tab"><img src="{svg}" width="16"> Tab</div></div>'''


def board_html(args, columns):
    font = ''
    family = 'system-ui, sans-serif'
    if args.font:
        font = f"@font-face {{ font-family: Wordmark; src: url('{Path(args.font).name}'); font-weight: 100 900; }}"
        family = 'Wordmark, system-ui, sans-serif'
    word = html.escape(args.wordmark)
    head = ''.join(f'<th>{html.escape(name)}</th>' for name, _, _ in columns)

    def row(title, cell):
        return f'<tr><th>{title}</th>' + ''.join(f'<td>{cell(svg, rev)}</td>' for _, svg, rev in columns) + '</tr>'

    rows = (row('Tab, 16 px', lambda s, r: f'<div class="tab"><img src="{s}" width="16"> {word}</div>')
            + row('Header, 40 px', lambda s, r: f'<div class="hdr"><img src="{s}" width="40"><span>{word}</span></div>')
            + row('Phone header, 32 px', lambda s, r: f'<div class="hdr sm"><img src="{s}" width="32"><span>{word}</span></div>')
            + row('Footer, reversed', lambda s, r: f'<div class="hdr ftr"><img src="{r}" width="40"><span>{word}</span></div>'))
    strips = ''.join(f'<img class="strip" src="strip-{label}.png" alt="{html.escape(name)} screening strip">'
                     for name, svg, _ in columns for label in [Path(svg).stem])
    return f'''<!doctype html><meta charset="utf-8"><title>{html.escape(args.title)}</title><style>{font}
body {{ margin: 24px; font: 15px system-ui, sans-serif; color: #172A3A; }} table {{ border-collapse: collapse; }}
th {{ text-align: left; padding: 6px 10px; }} td {{ padding: 6px 10px; }}
.hdr {{ display: flex; align-items: center; gap: 12px; padding: 12px 14px; border: 1px solid #D8DDE2; background: #fff; width: 220px; }}
.hdr span {{ font-family: {family}; font-weight: {args.weight}; font-size: 1.22rem; letter-spacing: -.04em; }}
.hdr.sm span {{ font-size: 1.05rem; }} .ftr {{ background: {args.footer}; color: #fff; border-color: {args.footer}; }}
.tab {{ display: flex; align-items: center; gap: 8px; width: 190px; padding: 8px 12px; border-radius: 8px 8px 0 0; background: #dee1e6; font-size: 13px; }}
.strip {{ display: block; max-width: 100%; margin: 8px 0; border: 1px solid #eee; }} details {{ margin-top: 24px; }}
</style><h1>{html.escape(args.title)}</h1><p>Options appear in random order with no ranking.</p>
<table><tr><th></th>{head}</tr>{rows}</table><h2>Screening strips</h2>{strips}
<details><summary>Notes and second opinion, opened after the pick</summary><p>See notes.md and second-opinion.md.</p></details>'''


def find_chrome():
    for path in CHROME_PATHS:
        if os.path.isabs(path) and os.path.exists(path):
            return path
        found = shutil.which(path)
        if found:
            return found
    return None


def render(page, png, size, no_render):
    """Renders a local HTML page to PNG and returns how, or why it could not."""
    if no_render:
        return 'Unverified: rendering turned off'
    url = page.resolve().as_uri()
    width, height = size
    if shutil.which('npx'):
        result = subprocess.run(['npx', '-y', 'playwright@1', 'screenshot', '--channel', 'chrome', '--viewport-size',
                                 f'{width}, {height}', '--full-page', url, str(png)], capture_output=True, text=True)
        if result.returncode == 0 and png.exists():
            return 'playwright'
    chrome = find_chrome()
    if chrome:
        result = subprocess.run([chrome, '--headless=new', '--hide-scrollbars', f'--window-size={width},{height}',
                                 f'--screenshot={png}', url], capture_output=True, text=True)
        if result.returncode == 0 and png.exists():
            return 'headless chrome'
    return 'Unverified: no renderer available'


def main(argv=None):
    args = parse(sys.argv[1:] if argv is None else argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    brand = args.brand or args.mark_colour
    labels = [Path(p).stem for p in args.options]
    wanted = set(labels) if args.sheets == 'all' else {s.strip() for s in args.sheets.split(',') if s.strip()}
    if args.font:
        shutil.copyfile(args.font, out / Path(args.font).name)
    sources = ([('Current', args.before)] if args.before else []) + [(f'Option {l}', p) for l, p in zip(labels, args.options)]
    entries = []
    for name, source in sources:
        src = Path(source)
        stem = 'before' if name == 'Current' else src.stem
        svg = out / f'{stem}.svg'
        if src.resolve() != svg.resolve():
            shutil.copyfile(src, svg)
        rev = out / f'{stem}-reversed.svg'
        rev.write_text(reversed_svg(svg.read_text(), args.mark_colour, args.reverse_colour))
        print(f'wrote {rev.name}')
        strip = out / f'strip-{stem}.html'
        strip.write_text(strip_html(name, svg.name, rev.name, brand, args.footer))
        print(f'wrote strip-{stem}.png ({render(strip, out / f"strip-{stem}.png", (900, 120), args.no_render)})')
        if stem in wanted:
            sheet = out / f'sheet-{stem}.html'
            sheet.write_text(sheet_html(name, svg.name, rev.name, brand, args.footer))
            print(f'wrote sheet-{stem}.png ({render(sheet, out / f"sheet-{stem}.png", (1100, 760), args.no_render)})')
        entries.append((name, svg.name, rev.name))
    split = 1 if args.before else 0
    current, options = entries[:split], entries[split:]
    random.Random(args.seed).shuffle(options)
    board = out / 'board.html'
    board.write_text(board_html(args, current + options))
    print('wrote board.html, order: ' + ' '.join(name.split()[-1] for name, _, _ in options))
    if args.board_png:
        print(f'wrote board.png ({render(board, out / "board.png", (1500, 1000), args.no_render)})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
