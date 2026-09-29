#!/usr/bin/env python3
"""Fail when a plugin's files changed since the base ref but its plugin.json version did not increase."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)


def semver(value):
    parts = value.split('-')[0].split('.')
    return tuple(int(p) for p in parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True, help='base ref, for example origin/main')
    args = parser.parse_args()
    errors = []
    for plugin_dir in sorted(ROOT.glob('claude/plugins/*/')):
        rel = plugin_dir.relative_to(ROOT).as_posix().rstrip('/')
        manifest_rel = f'{rel}/.claude-plugin/plugin.json'
        changed = git('diff', '--quiet', f'{args.base}...HEAD', '--', rel).returncode != 0
        if not changed:
            continue
        at_base = git('show', f'{args.base}:{manifest_rel}')
        if at_base.returncode != 0:
            print(f'{rel}: new plugin, version check skipped')
            continue
        head_version = json.loads((ROOT / manifest_rel).read_text()).get('version')
        base_version = json.loads(at_base.stdout).get('version')
        if head_version is None:
            errors.append(f'{manifest_rel}: no version but files under {rel} changed')
            continue
        if base_version is None:
            print(f'{rel}: version added ({head_version})')
            continue
        if semver(head_version) <= semver(base_version):
            errors.append(f'{manifest_rel}: files under {rel} changed but version is {head_version} (base {base_version}); bump it')
        else:
            print(f'{rel}: {base_version} -> {head_version}')
    for error in errors:
        print(f'::error::{error}')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
