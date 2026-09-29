#!/usr/bin/env python3
"""Report and enforce the age of every `verified:` stamp in the canonical standards files.

Exit 1 when a stamp is missing, malformed, in the future, has no usable `sources:`, or is
fail_days old or older. Warn from warn_days. `--today` (or FRESHNESS_TODAY) overrides the date.
"""
import argparse
import fnmatch
import json
import os
import sys
import tomllib
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stamps import stamp  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'tools/freshness.toml'


def in_scope(config):
    files = set()
    for pattern in config['include']:
        files.update(p for p in ROOT.glob(pattern) if p.is_file())
    for pattern in config.get('exclude', []):
        files = {p for p in files if not fnmatch.fnmatch(p.relative_to(ROOT).as_posix(), pattern)}
    return sorted(files)


def assess(path, today, config):
    rel = path.relative_to(ROOT).as_posix()
    verified, sources = stamp(path)
    row = {'file': rel, 'verified': verified.isoformat() if verified else None, 'age': None, 'status': 'ok', 'sources': sources, 'problem': None}
    if verified is None:
        row.update(status='error', problem='missing or malformed verified stamp')
        return row
    if verified > today:
        row.update(status='error', problem='verified date is in the future')
        return row
    ok_sources = sources in ('inline', 'house') or (isinstance(sources, list) and sources and all(s.startswith('https://') for s in sources))
    if not ok_sources:
        row.update(status='error', problem='sources must be https URLs, inline or house')
        return row
    age = (today - verified).days
    row['age'] = age
    if age >= config['fail_days']:
        row.update(status='error', problem=f'{age} days old, over the {config["fail_days"]} day limit')
    elif age >= config['warn_days']:
        row.update(status='warn', problem=f'{age} days old, re-verify before {config["fail_days"]}')
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--today', default=os.environ.get('FRESHNESS_TODAY'))
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--config', type=Path, default=CONFIG)
    args = parser.parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()
    config = tomllib.loads(args.config.read_text())
    rows = [assess(p, today, config) for p in in_scope(config)]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        width = max(len(r['file']) for r in rows) if rows else 10
        print(f'{"File":{width}}  Verified    Age  Status  Sources')
        for r in rows:
            src = r['sources'] if isinstance(r['sources'], str) else len(r['sources'])
            print(f'{r["file"]:{width}}  {r["verified"] or "-":10}  {str(r["age"] if r["age"] is not None else "-"):>4}  {r["status"]:6}  {src}')
    for r in rows:
        if r['status'] == 'warn':
            print(f'::warning file={r["file"]}::{r["problem"]}')
        elif r['status'] == 'error':
            print(f'::error file={r["file"]}::{r["problem"]}')
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as handle:
            handle.write('| File | Verified | Age | Status |\n|---|---|---|---|\n')
            for r in rows:
                handle.write(f'| {r["file"]} | {r["verified"] or "-"} | {r["age"] if r["age"] is not None else "-"} | {r["status"]} |\n')
    errors = sum(1 for r in rows if r['status'] == 'error')
    warnings = sum(1 for r in rows if r['status'] == 'warn')
    print(f'freshness: {len(rows)} files, {warnings} warnings, {errors} errors')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
