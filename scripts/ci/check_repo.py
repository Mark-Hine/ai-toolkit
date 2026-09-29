#!/usr/bin/env python3
"""Repo-wide structural checks that the plugin validators do not cover. Standard library only."""
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]


def tracked_files():
    out = subprocess.run(['git', 'ls-files', '-s'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        mode, _sha, _stage, path = line.split(maxsplit=3)
        yield mode, path


def check_shell_modes(errors):
    for mode, path in tracked_files():
        if path.endswith('.sh') and mode != '100755':
            errors.append(f'{path}: mode {mode}, expected 100755 (git update-index --chmod=+x)')


def check_manifests(errors):
    market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
    entries = {p['name']: p for p in market['plugins']}
    for name, entry in entries.items():
        if 'version' in entry:
            errors.append(f'marketplace.json: entry {name} sets version; plugin.json owns the version')
        manifest_path = ROOT / entry['source'] / '.claude-plugin/plugin.json'
        if not manifest_path.exists():
            errors.append(f'marketplace.json: entry {name} source has no plugin.json at {manifest_path}')
            continue
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('keywords') != entry.get('keywords'):
            errors.append(f'{manifest_path.relative_to(ROOT)}: keywords differ from marketplace entry')
        homepage = manifest.get('homepage', '')
        parsed = urlparse(homepage)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            errors.append(f'{manifest_path.relative_to(ROOT)}: homepage is not a URL: {homepage!r}')
        for dep in manifest.get('dependencies', []):
            if dep not in entries:
                errors.append(f'{manifest_path.relative_to(ROOT)}: dependency {dep} is not in the marketplace')
    for manifest_path in ROOT.glob('claude/plugins/*/.claude-plugin/plugin.json'):
        name = json.loads(manifest_path.read_text())['name']
        if name not in entries:
            errors.append(f'{manifest_path.relative_to(ROOT)}: plugin {name} is not listed in marketplace.json')


def main():
    errors = []
    check_shell_modes(errors)
    check_manifests(errors)
    for error in errors:
        print(f'::error::{error}')
    if errors:
        return 1
    print('check_repo: shell modes and plugin manifests OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
