#!/usr/bin/env python3
"""Check that files mirrored byte-for-byte across the three agent layers are identical.

The first path in each group is canonical. `--write` copies it over the others.
"""
import argparse
import filecmp
import re
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
    'references/pci-dss.md',
    'references/source-anchors.md',
    'references/protocol.md',
    'references/template.md',
    'references/platforms/android.md',
    'references/platforms/ios.md',
    'references/platforms/generic.md',
    'references/platforms/spring-boot.md',
    'references/platforms/react-nextjs.md',
    'scripts/post_azdo.py',
    'scripts/check_ancestry.py',
]
# Hook modules. shared/hooks is canonical; the plugin and Codex copies must be byte-identical.
HOOK_GROUPS = [
    ['shared/hooks/guard.py', 'claude/plugins/guard-kit/hooks/guard.py', 'codex/hooks/guard.py',
     'antigravity/plugins/android-kit/hooks/guard.py', 'antigravity/plugins/ios-kit/hooks/guard.py'],
    ['shared/hooks/swift_lint.py', 'claude/plugins/ios-kit/hooks/swift_lint.py', 'codex/hooks/swift_lint.py',
     'antigravity/plugins/ios-kit/hooks/swift_lint.py'],
]
DESIGN_REFERENCES = {
    'claude': 'claude/plugins/design-kit/skills/standards/references',
    'codex': 'codex/skills/design-standards/references',
    'antigravity': 'antigravity/plugins/design-kit/skills/design-standards/references',
}
DESIGN_REFERENCE_FILES = ['sources.md', 'source-anchors.md', 'rationale.md', 'platform-apis.md', 'design-contract.md', 'capture.md',
                          'options.md', 'brand-marks.md', 'companions.md']
ITERATE_SCRIPTS = {
    'claude': 'claude/plugins/design-kit/skills/iterate/scripts',
    'codex': 'codex/skills/design-iterate/scripts',
    'antigravity': 'antigravity/plugins/design-kit/skills/design-iterate/scripts',
}
ITERATE_SCRIPT_FILES = ['board.py', 'capture.mjs', 'second-opinion.schema.json']
AUDIT_REFERENCES = {
    'claude': 'claude/plugins/toolkit/skills/audit/references',
    'codex': 'codex/skills/toolkit-audit/references',
    'antigravity': 'antigravity/plugins/toolkit/skills/toolkit-audit/references',
}
AUDIT_REFERENCE_FILES = ['sources.md', 'rubric.md', 'register-template.md']
# Files whose text must match outside `<!-- layer-specific:start/end -->` blocks. Never written by --write.
PR_REVIEW_MARKED = ['references/ci.md']
LAYER_BLOCK = re.compile(r'<!-- layer-specific:start -->.*?<!-- layer-specific:end -->\n?', re.S)


def groups():
    for rel in PR_REVIEW_SHARED:
        yield [f'{base}/{rel}' for base in PR_REVIEW.values()]
    yield ['shared/guidance/references/kotlin-rationale.md'] + [
        f'{base}/references/languages/kotlin.md' for base in PR_REVIEW.values()]
    yield from HOOK_GROUPS
    # Source anchors are rewritten by tools/source_anchors.py --write, so the kit copies stay byte-identical.
    for kit in ('android', 'ios'):
        yield [f'claude/plugins/{kit}-kit/skills/standards/references/source-anchors.md',
               f'codex/skills/{kit}-standards/references/source-anchors.md',
               f'antigravity/plugins/{kit}-kit/skills/{kit}-standards/references/source-anchors.md']
    yield ['claude/plugins/android-kit/skills/standards/references/companions.md',
           'codex/skills/android-standards/references/companions.md',
           'antigravity/plugins/android-kit/skills/android-standards/references/companions.md']
    for rel in DESIGN_REFERENCE_FILES:
        yield [f'{base}/{rel}' for base in DESIGN_REFERENCES.values()]
    for rel in ITERATE_SCRIPT_FILES:
        yield [f'{base}/{rel}' for base in ITERATE_SCRIPTS.values()]
    for rel in AUDIT_REFERENCE_FILES:
        yield [f'{base}/{rel}' for base in AUDIT_REFERENCES.values()]


def marked_groups():
    for rel in PR_REVIEW_MARKED:
        yield [f'{base}/{rel}' for base in PR_REVIEW.values()]


def shared_text(path):
    return LAYER_BLOCK.sub('', path.read_text())


def check_marked(errors):
    for group in marked_groups():
        canonical = ROOT / group[0]
        if not canonical.exists():
            errors.append(f'{group[0]}: canonical file missing')
            continue
        expected = shared_text(canonical)
        for mirror in group[1:]:
            target = ROOT / mirror
            if not target.exists():
                errors.append(f'{mirror}: missing (canonical {group[0]})')
            elif shared_text(target) != expected:
                errors.append(f'{mirror}: text outside layer-specific blocks differs from {group[0]}')


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
    if not args.write:
        check_marked(errors)
    for error in errors:
        print(f'::error::{error}')
    if errors:
        return 1
    if args.write:
        print('check_parity: mirrors written')
    else:
        print(f'check_parity: {sum(1 for _ in groups())} mirrored groups identical, {sum(1 for _ in marked_groups())} marked groups match')
    return 0


if __name__ == '__main__':
    sys.exit(main())
