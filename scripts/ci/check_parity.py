#!/usr/bin/env python3
"""Check that files mirrored byte-for-byte across the three agent layers are identical.

The first path in each group is canonical. `--write` copies it over the others.
"""
import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PR_REVIEW = {
    'claude': 'claude/plugins/pr-review/skills/pr-review',
    'codex': 'codex/skills/pr-review',
    'antigravity': 'antigravity/plugins/pr-review/skills/pr-review',
}
PR_REVIEW_SHARED = [
    'references/output.md',
    'references/protocol.md',
    'references/template.md',
    'references/platforms/android.md',
    'references/platforms/ios.md',
    'references/platforms/generic.md',
    'references/platforms/spring-boot.md',
    'references/platforms/react-nextjs.md',
    'scripts/post_azdo.py',
]


def groups():
    for rel in PR_REVIEW_SHARED:
        yield [f'{base}/{rel}' for base in PR_REVIEW.values()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='copy the canonical file over its mirrors')
    args = parser.parse_args()
    errors = []
    for group in groups():
        canonical = ROOT / group[0]
        if not canonical.exists():
            errors.append(f'{group[0]}: canonical file missing')
            continue
        for mirror in group[1:]:
            target = ROOT / mirror
            if args.write:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(canonical, target)
                shutil.copymode(canonical, target)
                continue
            if not target.exists():
                errors.append(f'{mirror}: missing (canonical {group[0]})')
            elif not filecmp.cmp(canonical, target, shallow=False):
                errors.append(f'{mirror}: differs from {group[0]} (run scripts/ci/check_parity.py --write)')
    for error in errors:
        print(f'::error::{error}')
    if errors:
        return 1
    print(f'check_parity: {sum(1 for _ in groups())} mirrored groups identical' if not args.write else 'check_parity: mirrors written')
    return 0


if __name__ == '__main__':
    sys.exit(main())
