#!/usr/bin/env python3
"""Repo-wide structural checks that the plugin validators do not cover. Standard library only."""
import json
import re
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


AGENT_COLORS = {'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'cyan'}
PLUGIN_IGNORED_AGENT_KEYS = {'hooks', 'mcpServers', 'permissionMode'}  # Claude Code ignores these on plugin agents


def frontmatter(path):
    text = path.read_text()
    if not text.startswith('---\n'):
        return {}
    block = text.split('---\n', 2)[1]
    fields = {}
    current = None
    for line in block.splitlines():
        if line.startswith('  - ') and current:
            fields.setdefault(current, []).append(line[4:].strip())
        elif ':' in line and not line.startswith(' '):
            key, _, value = line.partition(':')
            current = key.strip()
            fields[current] = value.strip() or fields.get(current, [])
    return fields


def check_agents(errors):
    plugins = {p.name: p for p in (ROOT / 'claude/plugins').iterdir() if p.is_dir()}
    for agent in sorted(ROOT.glob('claude/plugins/*/agents/*.md')):
        rel = agent.relative_to(ROOT)
        fields = frontmatter(agent)
        for key in PLUGIN_IGNORED_AGENT_KEYS & set(fields):
            errors.append(f'{rel}: `{key}` is ignored on plugin agents, remove it')
        if fields.get('model') in ('', 'inherit', None):
            errors.append(f'{rel}: model must be pinned')
        color = fields.get('color')
        if color and color not in AGENT_COLORS:
            errors.append(f'{rel}: color {color!r} is not one of {sorted(AGENT_COLORS)}')
        if 'memory' in fields and 'disallowedTools' in fields:
            errors.append(f'{rel}: memory enables Write and Edit, which contradicts disallowedTools')
        skills = fields.get('skills') or []
        for skill in skills if isinstance(skills, list) else [skills]:
            plugin, _, name = skill.partition(':')
            if not name:
                errors.append(f'{rel}: skill {skill!r} must be plugin-scoped, such as android-kit:standards')
            elif not (plugins.get(plugin, ROOT / 'missing') / 'skills' / name / 'SKILL.md').exists():
                errors.append(f'{rel}: preloaded skill {skill!r} does not exist')


def skill_names(skills_dir):
    return sorted(p.parent.name for p in skills_dir.glob('*/SKILL.md'))


def readme_names(readme, skill, forms):
    """True when the README shows the skill in one of its invocation forms, as a code span or as a command
    that starts a line of a code block."""
    text = readme.read_text()
    for form in forms:
        name = re.escape(form.format(skill=skill))
        if re.search('`' + name + r'[`\s]', text) or (form[0] in '/$' and re.search('^' + name + r'(\s|$)', text, re.M)):
            return True
    return False


def check_readmes(errors):
    # The READMEs are hand-written, so a new skill is easy to miss. Each one must at least name every skill
    # it documents. Prose such as skill counts is not checked.
    claude_plugins = sorted(p for p in (ROOT / 'claude/plugins').iterdir() if (p / 'skills').is_dir())
    antigravity_plugins = sorted(p for p in (ROOT / 'antigravity/plugins').iterdir() if (p / 'skills').is_dir())
    checks = []
    for plugin in claude_plugins:
        forms = ('{skill}', '/' + plugin.name + ':{skill}')
        for skill in skill_names(plugin / 'skills'):
            checks.append((plugin / 'README.md', skill, ('{skill}', '/{skill}') + forms[1:]))
            checks.append((ROOT / 'claude/README.md', skill, forms))
    for plugin in antigravity_plugins:
        for skill in skill_names(plugin / 'skills'):
            checks.append((plugin / 'README.md', skill, ('{skill}', '/{skill}')))
            checks.append((ROOT / 'antigravity/README.md', skill, ('/{skill}',)))
    for skill in skill_names(ROOT / 'codex/skills'):
        checks.append((ROOT / 'codex/README.md', skill, ('${skill}',)))
    for readme, skill, forms in checks:
        if not readme.exists():
            errors.append(f'{readme.relative_to(ROOT)}: missing, expected it to list {skill}')
        elif not readme_names(readme, skill, forms):
            errors.append(f'{readme.relative_to(ROOT)}: does not list skill {skill} as `{forms[-1].format(skill=skill)}`')


def main():
    errors = []
    check_shell_modes(errors)
    check_manifests(errors)
    check_agents(errors)
    check_readmes(errors)
    for error in errors:
        print(f'::error::{error}')
    if errors:
        return 1
    print('check_repo: shell modes, plugin manifests, agent frontmatter and README skill lists OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
