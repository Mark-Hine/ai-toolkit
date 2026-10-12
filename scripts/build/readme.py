"""The Version column of the kit table in the root README, filled from each Claude plugin's plugin.json.

Only the rows between the plugin-versions markers change. The kit names and descriptions stay
hand-written. The Claude versions are shown because Claude Code installs pin to them.
"""
import json
import re

from targets.base import Output

README = 'README.md'
START = '<!-- plugin-versions:start -->'
END = '<!-- plugin-versions:end -->'
ROW = re.compile(r'^\| `([a-z0-9-]+)` \|')


def plugin_versions(project):
    versions = {}
    for manifest in sorted((project.root / 'claude/plugins').glob('*/.claude-plugin/plugin.json')):
        data = json.loads(manifest.read_text())
        versions[data['name']] = data['version']
    return versions


def render(text, versions):
    if START not in text or END not in text:
        raise ValueError(f'{README} has no {START} ... {END} table')
    head, rest = text.split(START, 1)
    table, tail = rest.split(END, 1)
    rows, seen = [], set()
    for line in table.strip('\n').split('\n'):
        match = ROW.match(line)
        if not match:
            rows.append(line)
            continue
        kit = match.group(1)
        if kit not in versions:
            raise ValueError(f'{README}: kit `{kit}` has no claude/plugins/{kit}/.claude-plugin/plugin.json')
        description = line.split('|')[2].strip()
        rows.append(f'| `{kit}` | {description} | {versions[kit]} |')
        seen.add(kit)
    missing = sorted(set(versions) - seen)
    if missing:
        raise ValueError(f'{README}: the kit table has no row for {", ".join(missing)}')
    return head + START + '\n' + '\n'.join(rows) + '\n' + END + tail


def outputs(project):
    path = project.root / README
    if not path.is_file():
        return []
    content = render(path.read_text(), plugin_versions(project))
    return [Output(README, content.encode(), section=True)]
