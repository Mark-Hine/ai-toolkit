#!/usr/bin/env python3
"""Validate the checked-in Codex assets using Python's standard library."""
import ast
import json
import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RULE_DECISIONS = {'allow', 'prompt', 'forbidden'}
RULE_KEYWORDS = {'pattern', 'decision', 'justification', 'match', 'not_match'}
SANDBOX_BY_ROLE = {'researcher': 'read-only', 'reviewer': 'read-only', 'verifier': 'workspace-write'}


def frontmatter(path):
    return path.read_text().split('---', 2)[1]


def manual_skills_from_claude(repo_root):
    """Skills that Claude marks manual-only map to `<plugin minus -kit>-<skill>` in Codex."""
    names = set()
    for skill in repo_root.glob('claude/plugins/*/skills/*/SKILL.md'):
        if re.search(r'^disable-model-invocation:\s*true\s*$', frontmatter(skill), re.M):
            plugin = skill.parents[2].name.removesuffix('-kit')
            names.add(f'{plugin}-{skill.parent.name}')
    return names


def check_syntax(root, errors):
    for path in root.rglob('*.toml'):
        try:
            tomllib.loads(path.read_text())
        except tomllib.TOMLDecodeError as exc:
            errors.append(f'{path}: {exc}')
    for path in root.rglob('*.py'):
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as exc:
            errors.append(f'{path}: {exc}')


def check_skills(root, repo_root, errors):
    manual = manual_skills_from_claude(repo_root)
    for path in (root / 'skills').glob('*/SKILL.md'):
        fm = frontmatter(path)
        name = re.search(r'^name: ([a-z0-9-]+)$', fm, re.M)
        if not name or name[1] != path.parent.name:
            errors.append(f'{path}: name must equal the directory name')
        description = re.search(r'^description: (.+)$', fm, re.M)
        try:
            if not (description and json.loads(description[1])):
                errors.append(f'{path}: description must be a non-empty JSON-quoted string')
        except json.JSONDecodeError:
            errors.append(f'{path}: description must be a JSON-quoted string')
        policy = path.parent / 'agents/openai.yaml'
        has_manual_policy = policy.exists() and re.search(r'allow_implicit_invocation:\s*false', policy.read_text())
        if path.parent.name in manual and not has_manual_policy:
            errors.append(f'{path.parent}: Claude marks this skill manual-only, add agents/openai.yaml with allow_implicit_invocation: false')
        if path.parent.name not in manual and has_manual_policy:
            errors.append(f'{path.parent}: openai.yaml disables implicit invocation but the Claude skill does not')
    for path in (root / 'skills').rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            if not (path.parent / target.split('#')[0]).exists():
                errors.append(f'{path}: broken link {target}')


def check_agents(root, errors):
    for path in (root / 'agents').glob('*.toml'):
        config = tomllib.loads(path.read_text())
        for key in ('name', 'description', 'developer_instructions', 'model', 'model_reasoning_effort', 'sandbox_mode'):
            if not config.get(key):
                errors.append(f'{path}: missing {key}')
        if config.get('name') != path.stem:
            errors.append(f'{path}: name {config.get("name")!r} must equal the file stem')
        if config.get('model') == 'inherit':
            errors.append(f'{path}: model must be pinned, not inherit')
        role = path.stem.rsplit('-', 1)[-1]
        expected = SANDBOX_BY_ROLE.get(role)
        if expected and config.get('sandbox_mode') != expected:
            errors.append(f'{path}: sandbox_mode must be {expected} for a {role}')


def check_rules(root, errors):
    path = root / 'home/toolkit.rules'
    try:
        tree = ast.parse(path.read_text(), filename=str(path))
    except SyntaxError as exc:
        errors.append(f'{path}: {exc}')
        return
    for node in tree.body:
        call = getattr(node, 'value', None)
        if not (isinstance(node, ast.Expr) and isinstance(call, ast.Call) and getattr(call.func, 'id', None) == 'prefix_rule'):
            errors.append(f'{path}:{node.lineno}: only prefix_rule(...) statements are allowed')
            continue
        if call.args:
            errors.append(f'{path}:{node.lineno}: prefix_rule takes keyword arguments only')
        kwargs = {kw.arg: kw.value for kw in call.keywords}
        unknown = set(kwargs) - RULE_KEYWORDS
        if unknown:
            errors.append(f'{path}:{node.lineno}: unknown keywords {sorted(unknown)}')
        pattern = kwargs.get('pattern')
        if not isinstance(pattern, ast.List) or not pattern.elts:
            errors.append(f'{path}:{node.lineno}: pattern must be a non-empty list')
        decision = kwargs.get('decision')
        if decision is not None and (not isinstance(decision, ast.Constant) or decision.value not in RULE_DECISIONS):
            errors.append(f'{path}:{node.lineno}: decision must be one of {sorted(RULE_DECISIONS)}')


def check_home_references(root, repo_root, errors):
    sources = [root / 'home/AGENTS.md', *(root / 'agents').glob('*.toml')]
    guidance_roots = [root / 'home/guidance', repo_root / 'shared/guidance']
    for source in sources:
        text = source.read_text()
        for ref in set(re.findall(r'(?:~/\.codex/)?guidance/([a-z0-9/_-]+\.md)', text)):
            if not any((g / ref).exists() for g in guidance_roots):
                errors.append(f'{source}: references guidance/{ref} which does not exist')
        for ref in set(re.findall(r'~/\.agents/skills/([a-z0-9/_.-]+)', text)):
            if not (root / 'skills' / ref.rstrip('/')).exists():
                errors.append(f'{source}: references ~/.agents/skills/{ref} which does not exist under codex/skills')


def main(root=None, repo_root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    repo_root = Path(repo_root) if repo_root else root.parent
    errors = []
    check_syntax(root, errors)
    check_skills(root, repo_root, errors)
    check_agents(root, errors)
    check_rules(root, errors)
    check_home_references(root, repo_root, errors)
    return errors


if __name__ == '__main__':
    problems = main()
    for problem in problems:
        print(f'::error::{problem}')
    if problems:
        sys.exit(1)
    root = Path(__file__).resolve().parents[1]
    print(f'Validated {len(list((root / "skills").glob("*/SKILL.md")))} skills, agent and config TOML, toolkit.rules, home references, local skill links and Python syntax.')
