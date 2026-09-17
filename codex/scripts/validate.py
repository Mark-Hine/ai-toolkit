#!/usr/bin/env python3
"""Validate the checked-in Codex assets using Python's standard library."""
import ast
import json
from pathlib import Path
import re
import tomllib

root = Path(__file__).resolve().parents[1]
for path in root.rglob('*.toml'):
    tomllib.loads(path.read_text())
for path in root.rglob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
for path in (root / 'skills').glob('*/SKILL.md'):
    frontmatter = path.read_text().split('---', 2)[1]
    name = re.search(r'^name: ([a-z0-9-]+)$', frontmatter, re.M)
    assert name and name[1] == path.parent.name, path
    description = re.search(r'^description: (.+)$', frontmatter, re.M)
    assert description and json.loads(description[1]), path
for path in (root / 'skills').rglob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' in target or target.startswith('#'):
            continue
        assert (path.parent / target.split('#')[0]).exists(), (path, target)
for path in (root / 'agents').glob('*.toml'):
    config = tomllib.loads(path.read_text())
    assert all(config.get(key) for key in ('name', 'description', 'developer_instructions', 'model', 'model_reasoning_effort'))
print(f'Validated {len(list((root / "skills").glob("*/SKILL.md")))} skills, agent/config TOML, local skill links and Python syntax.')
