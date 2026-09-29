#!/usr/bin/env python3
"""Detect drift between the Claude, Codex and Antigravity copies of mirrored files.

The three layers adapt wording on purpose (project file name, home path, skill invocation syntax,
tool names), so the copies are compared after replacing those adaptations with neutral tokens and
reflowing whitespace. A pair passes when its similarity ratio is at or above the threshold in
tools/mirrors.toml, or a still-valid exception in tools/mirror-exceptions.toml. Standard library only.
"""
import argparse
import difflib
import itertools
import re
import sys
import tomllib
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stamps import frontmatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LAYERS = ('claude', 'codex', 'antigravity')


def codex_instructions(text):
    """The developer_instructions string of a Codex agent TOML, decoded."""
    data = tomllib.loads(text)
    return data.get('developer_instructions', '')


def normalise(text, layer, substitutions):
    if layer == 'codex' and text.lstrip().startswith('name ='):
        text = codex_instructions(text)
    else:
        _, text = frontmatter(text)
    for sub in substitutions:
        for token in sorted(sub.get(layer, []), key=len, reverse=True):
            text = text.replace(token, sub['neutral'])
    text = re.sub(r'`[^`]*`', lambda m: m.group(0).replace(' ', ' '), text)  # keep code spans whole
    words = re.sub(r'\s+', ' ', text).strip().lower()
    return words.split(' ')


def pairs(config):
    for group in config['groups']:
        for item in group['items']:
            keys = {}
            if group['name'] == 'agents':
                keys = {'p': item[0], 'a': item[1]}
            elif len(item) == 2:
                keys = {'p': item[0], 's': item[1], 'f': item[1]}
            paths = {layer: group[layer].format(**keys) for layer in LAYERS if layer in group}
            yield group['name'], paths


def threshold_for(claude_path, config, exceptions, today):
    for exc in exceptions.get('exceptions', []):
        if exc['path'] == claude_path:
            if date.fromisoformat(str(exc['until'])) < today:
                return None, f'exception expired on {exc["until"]}: {exc["reason"]}'
            return float(exc['threshold']), exc['reason']
    return float(config.get('threshold', 0.85)), None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diff', action='store_true', help='print the normalised diff for each drifting pair')
    parser.add_argument('--today', default=None)
    args = parser.parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()
    config = tomllib.loads((ROOT / 'tools/mirrors.toml').read_text())
    exceptions = tomllib.loads((ROOT / 'tools/mirror-exceptions.toml').read_text())
    subs = config.get('substitutions', [])
    failures, rows = [], []
    for group, paths in pairs(config):
        missing = [p for p in paths.values() if not (ROOT / p).exists()]
        if missing:
            failures.append(f'{group}: missing {", ".join(missing)}')
            continue
        threshold, note = threshold_for(paths['claude'], config, exceptions, today)
        if threshold is None:
            failures.append(f'{paths["claude"]}: {note}')
            continue
        tokens = {layer: normalise((ROOT / p).read_text(errors='replace'), layer, subs) for layer, p in paths.items()}
        worst = 1.0
        for a, b in itertools.combinations(tokens, 2):
            ratio = difflib.SequenceMatcher(None, tokens[a], tokens[b], autojunk=False).ratio()
            worst = min(worst, ratio)
            if ratio < threshold:
                failures.append(f'{paths["claude"]}: {a} vs {b} similarity {ratio:.2f} below {threshold:.2f}')
                if args.diff:
                    print('\n'.join(difflib.unified_diff(tokens[a], tokens[b], a, b, lineterm='', n=2)))
        rows.append((paths['claude'], worst, threshold, 'exception' if note else ''))
    width = max(len(r[0]) for r in rows) if rows else 10
    for path, worst, threshold, flag in rows:
        print(f'{path:{width}}  {worst:.2f}  (min {threshold:.2f}) {flag}')
    for failure in failures:
        print(f'::error::{failure}')
    print(f'mirror_parity: {len(rows)} pairs, {len(failures)} failures')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
