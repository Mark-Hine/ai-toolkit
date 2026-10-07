#!/usr/bin/env python3
"""Confirm that each source anchor's quoted sentence still appears on its page. Standard library only.

An anchor pins a standards source key to its URL and one or two verbatim sentences that a rule rests
on (docs/source-anchors.md). Agents read the anchors and never fetch a page to grade a rule. This tool
does the fetching instead, at maintenance time, and reports each anchor as:

  CONFIRMED    the page text contains every quote. --write records today's date.
  DRIFTED      the page was read but a quote is gone. Re-read the page and re-anchor the rule.
  UNREACHABLE  the page text could not be read. Open it in a browser and check by hand.
  SKIPPED      the anchor has no quote, such as a house rule or a book.

Text comes from Apple's JSON endpoint for HIG and documentation pages, from headless Chrome for hosts
that render client-side (Material 3), and from the HTML for everything else. Extracted text is cached
under .cache/sources/ for maintainers and never committed.

--lint runs offline. It checks the anchor format, quote length and dates, and that every key or URL a
registry declares has an anchor. Coverage gaps fail only when the config sets enforce = true.
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from linkcheck import Checker  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'tools/source_anchors.toml'
CACHE = ROOT / '.cache/sources'
BROWSER_UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 '
              '(KHTML, like Gecko) Version/17.0 Safari/605.1.15')
CHROME_PATHS = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
HEADING = re.compile(r'^### (\S+)\s*$')
FIELD = re.compile(r'^- (URL|Quote|Confirmed|Fetch): (.*)$')
CONFIRMED = re.compile(r'^(\d{4}-\d{2}-\d{2}) \((apple-json|html|browser)\)$')
NO_QUOTE = re.compile(r'^none \((house|book|offline)\)$')
METHODS = ('apple-json', 'html', 'browser')
QUOTE_CHARS = str.maketrans({'‘': "'", '’': "'", '“': '"', '”': '"', ' ': ' '})


class Anchor:
    def __init__(self, key, path, line):
        self.key, self.path, self.line = key, path, line
        self.url, self.quotes, self.confirmed, self.fetch = None, [], None, None
        self.confirmed_line = None

    @property
    def no_quote(self):
        return len(self.quotes) == 1 and bool(NO_QUOTE.match(self.quotes[0]))


def parse(path):
    """(anchors, problems) for one anchor file."""
    anchors, problems, current = [], [], None
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if m := HEADING.match(line):
            current = Anchor(m.group(1), path, n)
            anchors.append(current)
            continue
        if current is None or not line.startswith('- '):
            continue
        if not (m := FIELD.match(line)):
            problems.append(f'{rel(path)}:{n}: unknown anchor field: {line[:40]}')
            continue
        name, value = m.group(1), m.group(2).strip()
        if name == 'URL':
            current.url = value
        elif name == 'Quote':
            current.quotes.append(value[1:-1] if len(value) > 1 and value[0] == value[-1] == '"' else value)
        elif name == 'Confirmed':
            current.confirmed, current.confirmed_line = value, n
        elif name == 'Fetch':
            current.fetch = value
    return anchors, problems


def rel(path):
    try:
        return Path(path).relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def anchor_files(config):
    files = set()
    for pattern in config['anchors']:
        files.update(p for p in ROOT.glob(pattern) if p.is_file())
    return sorted(files)


def normalise(text):
    """Text for matching: straight quotes, no whitespace, so inline markup and wrapping never matter."""
    return re.sub(r'\s+', '', html.unescape(text).translate(QUOTE_CHARS))


def sentences(quote):
    return len([s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z])', quote.strip()) if s])


# Text extraction


def html_text(markup):
    markup = re.sub(r'<(script|style|noscript|svg)\b.*?</\1>', ' ', markup, flags=re.S | re.I)
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', markup)).split())


def apple_text(payload):
    """Every text node in an Apple documentation or HIG JSON page."""
    data = json.loads(payload)
    out = []

    def walk(node):
        if isinstance(node, dict):
            if node.get('type') in ('text', 'codeVoice') and isinstance(node.get('text', node.get('code')), str):
                out.append(node.get('text', node.get('code')))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(data.get('abstract', []))
    walk(data.get('primaryContentSections', []))
    walk(data.get('sections', []))
    return ' '.join(out)


def find_chrome():
    for candidate in CHROME_PATHS:
        found = candidate if Path(candidate).is_file() else shutil.which(candidate)
        if found:
            return found
    return None


def chrome_dom(url, chrome, timeout):
    with tempfile.TemporaryDirectory() as profile:
        out = subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-sandbox', '--dump-dom',
                              '--virtual-time-budget=8000', f'--user-data-dir={profile}', url],
                             capture_output=True, text=True, timeout=timeout)
    return out.stdout


class Reader:
    """Fetches page text with the link checker's retries, host locks and policies."""

    def __init__(self, config, opener=None, chrome=None, sleep=None):
        base = opener or Checker.default_opener

        def browser_opener(url, method, headers, timeout):
            return base(url, method, dict(headers, **{'User-Agent': BROWSER_UA}), timeout)
        kwargs = {'opener': browser_opener}
        if sleep:
            kwargs['sleep'] = sleep
        self.checker = Checker(config, **kwargs)
        self.config = config
        self.chrome = chrome
        self.dom = chrome_dom

    def method_for(self, anchor):
        if anchor.fetch:
            return anchor.fetch
        host, policy = self.checker.host_policy(anchor.url)
        if policy.get('apple_json') and self.checker.apple_json_url(anchor.url):
            return 'apple-json'
        if host in self.config.get('browser_hosts', []):
            return 'browser'
        return 'html'

    def get(self, url):
        host, policy = self.checker.host_policy(url)
        last = None
        with self.checker.lock_for(host, policy):
            for attempt in range(self.config.get('retries', 3)):
                try:
                    status, _, body = self.checker.request(url, policy, 'GET')
                    return status, body
                except urllib.error.HTTPError as exc:
                    if exc.code == 429 or exc.code >= 500:
                        last = exc
                        self.checker.sleep(2 ** attempt)
                        continue
                    return exc.code, b''
                except Exception as exc:  # noqa: BLE001 - reported as UNREACHABLE
                    last = exc
                    self.checker.sleep(2 ** attempt)
        raise last

    def text(self, anchor):
        """(method, text or None, detail)."""
        method = self.method_for(anchor)
        url = anchor.url.split('#', 1)[0]
        try:
            if method == 'apple-json':
                status, body = self.get(self.checker.apple_json_url(url))
                if status >= 400:
                    return method, None, f'Apple JSON endpoint returned HTTP {status}'
                return method, apple_text(body), ''
            if method == 'browser':
                if not self.chrome:
                    return method, None, 'needs headless Chrome, which was not found'
                return method, html_text(self.dom(url, self.chrome, self.config.get('browser_timeout', 60))), ''
            status, body = self.get(url)
            if status >= 400:
                return method, None, f'HTTP {status}'
            return method, html_text(body.decode('utf-8', errors='replace')), ''
        except Exception as exc:  # noqa: BLE001
            return method, None, type(exc).__name__


def verify(anchor, reader, cache=None):
    """Result dict for one anchor."""
    base = {'key': anchor.key, 'url': anchor.url, 'file': rel(anchor.path), 'anchor': anchor}
    if anchor.no_quote:
        return dict(base, status='SKIPPED', detail=anchor.quotes[0], method=None)
    method, text, detail = reader.text(anchor)
    if text and cache is not None:
        cache.mkdir(parents=True, exist_ok=True)
        name = hashlib.sha1(anchor.url.split('#', 1)[0].encode()).hexdigest()[:16]
        (cache / f'{name}.txt').write_text(f'{anchor.url}\n\n{text}\n', encoding='utf-8')
    if not text or len(text) < 200:
        return dict(base, status='UNREACHABLE', detail=detail or 'no readable text', method=method)
    page = normalise(text)
    missing = [q for q in anchor.quotes if normalise(q) not in page]
    if missing:
        return dict(base, status='DRIFTED', detail=f'quote not found: "{missing[0][:80]}"', method=method)
    return dict(base, status='CONFIRMED', detail='', method=method)


def write_confirmed(results, today):
    """Record today's date on every confirmed anchor, and bump each touched file's verified stamp."""
    touched = {}
    for r in results:
        if r['status'] != 'CONFIRMED':
            continue
        anchor = r['anchor']
        touched.setdefault(anchor.path, []).append((anchor, f'- Confirmed: {today.isoformat()} ({r["method"]})'))
    for path, edits in touched.items():
        lines = path.read_text(encoding='utf-8').splitlines()
        for anchor, new in sorted(edits, key=lambda e: -(e[0].confirmed_line or e[0].line)):
            if anchor.confirmed_line:
                lines[anchor.confirmed_line - 1] = new
            else:
                at = anchor.line
                while at < len(lines) and lines[at].startswith('- '):
                    at += 1
                lines.insert(at, new)
        text = '\n'.join(lines) + '\n'
        text = re.sub(r'^verified: \d{4}-\d{2}-\d{2}$', f'verified: {today.isoformat()}', text, count=1, flags=re.M)
        path.write_text(text, encoding='utf-8')


# Offline lint


def declared(config):
    """{(registry file, key or URL)} that a registry declares and an anchor must cover."""
    wanted = set()
    for reg in config.get('registries', []):
        pattern = re.compile(reg['pattern'], re.M)
        for glob in reg['files']:
            for path in ROOT.glob(glob):
                for m in pattern.finditer(path.read_text(encoding='utf-8')):
                    wanted.add((rel(path), reg.get('mode', 'key'), m.group(1)))
    return wanted


def lint(config, today):
    """(errors, warnings)."""
    errors, warnings, anchors = [], [], []
    for path in anchor_files(config):
        found, problems = parse(path)
        errors += problems
        anchors += found
        seen = set()
        for a in found:
            where = f'{rel(path)}:{a.line}'
            if a.key in seen:
                errors.append(f'{where}: {a.key} is anchored twice in this file')
            seen.add(a.key)
            if not a.url or not a.url.startswith('https://'):
                errors.append(f'{where}: {a.key} needs an https URL')
            if not a.quotes:
                errors.append(f'{where}: {a.key} needs a Quote line, or "none (house)", "none (book)" or "none (offline)"')
            for q in a.quotes:
                if NO_QUOTE.match(q):
                    if len(a.quotes) > 1:
                        errors.append(f'{where}: {a.key} mixes "none" with quotes')
                    continue
                if 'to fetch' in q.lower():
                    errors.append(f'{where}: {a.key} still says "to fetch"')
                if len(q) > config.get('max_quote_chars', 300):
                    errors.append(f'{where}: {a.key} quote is {len(q)} characters, the cap is {config.get("max_quote_chars", 300)}')
                if sentences(q) > config.get('max_quote_sentences', 2):
                    errors.append(f'{where}: {a.key} quote has more than {config.get("max_quote_sentences", 2)} sentences')
            if a.fetch and a.fetch not in METHODS:
                errors.append(f'{where}: {a.key} Fetch must be one of {", ".join(METHODS)}')
            if a.confirmed not in (None, 'not yet'):
                m = CONFIRMED.match(a.confirmed)
                if not m:
                    errors.append(f'{where}: {a.key} Confirmed must read "YYYY-MM-DD (method)" or "not yet"')
                elif date.fromisoformat(m.group(1)) > today:
                    errors.append(f'{where}: {a.key} is confirmed on a future date')
            elif not a.no_quote:
                warnings.append(f'{where}: {a.key} is not confirmed yet')
    keys = {a.key for a in anchors}
    urls = {a.url.split('#', 1)[0].rstrip('/') for a in anchors if a.url}
    gaps = []
    for path, mode, value in sorted(declared(config)):
        covered = value in keys if mode == 'key' else value.split('#', 1)[0].rstrip('/') in urls
        if not covered:
            gaps.append(f'{path}: {value} has no source anchor')
    (errors if config.get('enforce') else warnings).extend(gaps)
    return errors, warnings


def report(results):
    counts = {}
    for r in results:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    lines = [f'# Source anchors, {len(results)} checked', '', '| Status | Count |', '|---|---|']
    lines += [f'| {k} | {v} |' for k, v in sorted(counts.items())] + ['']
    for status in ('DRIFTED', 'UNREACHABLE'):
        rows = [r for r in results if r['status'] == status]
        if rows:
            lines += [f'## {status}', '', '| Key | URL | Detail | File |', '|---|---|---|---|']
            lines += [f'| {r["key"]} | {r["url"]} | {r["detail"]} | {r["file"]} |' for r in rows]
            lines.append('')
    return '\n'.join(lines), counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--config', type=Path, default=CONFIG)
    parser.add_argument('--lint', action='store_true', help='check the anchor files offline')
    parser.add_argument('--write', action='store_true', help='record today on every confirmed anchor')
    parser.add_argument('--only', help='check only anchors whose key or URL contains this substring')
    parser.add_argument('--report', type=Path, help='write a markdown report here')
    parser.add_argument('--today', type=date.fromisoformat, default=date.today())
    args = parser.parse_args(argv)
    config = tomllib.loads(args.config.read_text())
    # Host policies (Apple JSON, tokens, concurrency) come from the link checker's config.
    config.setdefault('hosts', tomllib.loads((ROOT / 'tools/linkcheck.toml').read_text()).get('hosts', {}))

    if args.lint:
        errors, warnings = lint(config, args.today)
        for w in warnings:
            print(f'::warning::{w}')
        for e in errors:
            print(f'::error::{e}')
        mode = 'enforcing' if config.get('enforce') else 'report-only for coverage'
        print(f'source_anchors: {len(errors)} errors, {len(warnings)} warnings ({mode})')
        return 1 if errors else 0

    anchors = []
    for path in anchor_files(config):
        anchors += parse(path)[0]
    if args.only:
        anchors = [a for a in anchors if args.only in a.key or args.only in (a.url or '')]
    reader = Reader(config, chrome=find_chrome())
    with ThreadPoolExecutor(max_workers=config.get('workers', 6)) as pool:
        results = list(pool.map(lambda a: verify(a, reader, CACHE), anchors))
    text, counts = report(results)
    print(text)
    if args.report:
        args.report.write_text(text)
    if args.write:
        write_confirmed(results, args.today)
    return 1 if counts.get('DRIFTED') or counts.get('UNREACHABLE') else 0


if __name__ == '__main__':
    sys.exit(main())
