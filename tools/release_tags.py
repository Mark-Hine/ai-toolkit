#!/usr/bin/env python3
"""Tag and release each Claude plugin whose version on main has no release yet.

For every claude/plugins/<name>/.claude-plugin/plugin.json, the release tag is `<name>--v<version>`.
A tag that already exists is left alone. A new one gets a GitHub Release whose notes list the commits
that touched that plugin since its previous tag. The release workflow runs this on every push to main,
so a version bump that lands on main is tagged without anyone doing it by hand.

  python3 tools/release_tags.py --dry-run          print what would be released
  python3 tools/release_tags.py --target <sha>     create the releases with the gh CLI
Standard library only. Creating releases needs `gh` and a token with contents: write.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(root, *args):
    return subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, check=True).stdout


def semver(version):
    return tuple(int(part) for part in version.split('-')[0].split('.'))


def tag_name(plugin, version):
    return f'{plugin}--v{version}'


def plugins(root):
    """(name, version) for every Claude plugin, sorted by name."""
    found = []
    for manifest in sorted((root / 'claude/plugins').glob('*/.claude-plugin/plugin.json')):
        data = json.loads(manifest.read_text())
        found.append((data['name'], data['version']))
    return found


def previous_tag(plugin, version, tags):
    """The newest existing tag of this plugin with a lower version, or None."""
    prefix = f'{plugin}--v'
    older = []
    for tag in tags:
        if tag.startswith(prefix):
            try:
                number = semver(tag[len(prefix):])
            except ValueError:
                continue
            if number < semver(version):
                older.append((number, tag))
    return max(older)[1] if older else None


def notes(root, plugin, since, target):
    if since is None:
        return (f'First tagged release of `{plugin}`. Earlier changes are in the git history of '
                f'`claude/plugins/{plugin}/`.\n')
    log = git(root, 'log', '--no-merges', '--format=- %s (%h)', f'{since}..{target}', '--', f'claude/plugins/{plugin}')
    lines = log.strip() or '- No commits touched this plugin. The version changed with a shared file.'
    return f'Changes since `{since}`:\n\n{lines}\n'


def plan(root, target='HEAD'):
    """The releases to create, as (tag, title, notes) tuples."""
    tags = set(git(root, 'tag', '--list').split())
    releases = []
    for plugin, version in plugins(root):
        tag = tag_name(plugin, version)
        if tag in tags:
            continue
        since = previous_tag(plugin, version, tags)
        releases.append((tag, f'{plugin} {version}', notes(root, plugin, since, target)))
    return releases


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--target', default='HEAD', help='commit to tag, a full SHA in CI')
    parser.add_argument('--dry-run', action='store_true', help='print the releases instead of creating them')
    args = parser.parse_args(argv)
    releases = plan(ROOT, args.target)
    if not releases:
        print('release_tags: every plugin version is already tagged')
        return 0
    for tag, title, body in releases:
        if args.dry_run:
            print(f'would release {tag}: {title}\n{body}')
            continue
        # Per-plugin releases are not ordered against each other, so none is marked as the repo's latest.
        subprocess.run(['gh', 'release', 'create', tag, '--target', args.target, '--title', title,
                        '--notes-file', '-', '--latest=false'], input=body, text=True, cwd=ROOT, check=True)
        print(f'released {tag}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
