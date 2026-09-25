#!/usr/bin/env python3
"""Validate the checked-in Antigravity assets using Python's standard library."""
import ast
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]

# 1. Python syntax
for path in root.rglob('*.py'):
    ast.parse(path.read_text(), filename=str(path))

# 2. Plugins
plugins = list(root.glob('plugins/*/plugin.json'))
assert len(plugins) == 3, f"Expected 3 plugins, found {len(plugins)}"
for path in plugins:
    data = json.loads(path.read_text())
    assert 'name' in data and data['name'] == path.parent.name, path

# 3. Skills
skills = list(root.glob('plugins/*/skills/*/SKILL.md'))
assert len(skills) == 11, f"Expected 11 skills, found {len(skills)}"
for path in skills:
    parts = path.read_text().split('---', 2)
    assert len(parts) >= 3, f"Missing frontmatter in {path}"
    frontmatter = parts[1]
    name_match = re.search(r'^name:\s*([a-z0-9-]+)\s*$', frontmatter, re.M)
    assert name_match and name_match.group(1) == path.parent.name, f"Name mismatch in {path}"
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.M)
    assert desc_match and desc_match.group(1).strip(), f"Missing description in {path}"

# 4. Agents
agents = list(root.glob('plugins/*/agents/*.md'))
assert len(agents) == 6, f"Expected 6 agents, found {len(agents)}"
for path in agents:
    parts = path.read_text().split('---', 2)
    assert len(parts) >= 3, f"Missing frontmatter in {path}"
    frontmatter = parts[1]
    name_match = re.search(r'^name:\s*([a-z0-9-]+)\s*$', frontmatter, re.M)
    assert name_match and name_match.group(1) == path.stem, f"Name mismatch in {path}"
    model_match = re.search(r'^model:\s*(\S+)\s*$', frontmatter, re.M)
    assert model_match and model_match.group(1) in {'inherit', 'flash', 'pro'}, f"Model must be inherit, flash or pro in {path}"

# 5. Local Markdown links
for path in root.rglob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' in target or target.startswith('#') or target.startswith('mailto:'):
            continue
        link_path = target.split('#')[0]
        if not link_path:
            continue
        assert (path.parent / link_path).exists(), f"Broken link in {path}: {target}"

# 6. Hooks JSON
for path in root.rglob('hooks.json'):
    hook_data = json.loads(path.read_text())
    assert isinstance(hook_data, dict), f"hooks.json must be an object: {path}"
    for hook_name, events in hook_data.items():
        assert isinstance(events, dict), f"Hook {hook_name} spec must be an object in {path}"

print(f'Validated {len(skills)} skills, {len(agents)} agents, {len(plugins)} plugins, hook manifests, local links and Python syntax.')
