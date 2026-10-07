#!/usr/bin/env python3
"""Validate the checked-in Antigravity assets against the documented plugin layout. Standard library only."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PLUGIN_KEYS = {'name', 'description', 'displayName', 'version', 'logo', 'suggestedPrompts', 'disabled', '$schema'}
AGENT_KEYS = {'name', 'description', 'model', 'tools', 'subagent', 'mainAgent', 'commandExecutionPolicy', 'skills', 'plugins', 'mcpServers'}
MODELS = {'flash', 'pro'}  # `inherit` is documented but the toolkit pins models
POLICIES = {'off', 'auto', 'eager', 'sandbox'}
TOOLS = {'view_file', 'list_dir', 'find_by_name', 'grep_search', 'search_web', 'read_url_content', 'run_command',
         'write_to_file', 'replace_file_content', 'multi_replace_file_content', 'view_code_item', 'browser_preview'}
WRITE_TOOLS = {'write_to_file', 'replace_file_content', 'multi_replace_file_content'}
EVENTS = {'PreToolUse', 'PostToolUse', 'PreInvocation', 'PostInvocation', 'Stop'}
GROUPED = {'PreToolUse', 'PostToolUse'}
LEAKS = ['codex exec', 'CODEX_API_KEY', '~/.codex', '$pr-review', '$android-', '$ios-', '$web-', 'define_subagent',
         'enable_write_tools', 'GEMINI_CONFIG_DIR', '.claude/rules', 'CLAUDE_PLUGIN_ROOT']
RULE_LIMIT = 24_000


def frontmatter(text):
    parts = text.split('---\n', 2)
    if len(parts) < 3:
        return None
    fields = {}
    for line in parts[1].splitlines():
        if ':' in line and not line.startswith(' '):
            key, _, value = line.partition(':')
            fields[key.strip()] = value.strip()
    return fields


def check_python(errors):
    for path in ROOT.rglob('*.py'):
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as exc:
            errors.append(f'{path}: {exc}')


def check_plugins(errors):
    expected = {p.name for p in (REPO / 'claude/plugins').iterdir() if p.is_dir()} - {'guard-kit'}
    found = {p.parent.name for p in ROOT.glob('plugins/*/plugin.json')}
    if found != expected:
        errors.append(f'plugins differ from the Claude layer: missing {sorted(expected - found)}, extra {sorted(found - expected)}')
    for path in ROOT.glob('plugins/*/plugin.json'):
        data = json.loads(path.read_text())
        unknown = set(data) - PLUGIN_KEYS
        if unknown:
            errors.append(f'{path}: undocumented keys {sorted(unknown)} (the loader drops them silently)')
        if data.get('name') != path.parent.name:
            errors.append(f'{path}: name must equal the directory name')
        if not data.get('description'):
            errors.append(f'{path}: description is required for the plugin listing')
        rules = path.parent / 'rules/AGENTS.md'
        if rules.exists() and len(rules.read_bytes()) > RULE_LIMIT:
            errors.append(f'{rules}: over the {RULE_LIMIT} byte rule limit')


def check_skills(errors):
    codex = {p.name for p in (REPO / 'codex/skills').iterdir() if (p / 'SKILL.md').is_file()}
    skills = list(ROOT.glob('plugins/*/skills/*/SKILL.md'))
    if {p.parent.name for p in skills} != codex:
        errors.append('skills differ from the Codex layer')
    for path in skills:
        fields = frontmatter(path.read_text())
        if fields is None:
            errors.append(f'{path}: missing frontmatter')
            continue
        if fields.get('name') != path.parent.name:
            errors.append(f'{path}: name must equal the directory name')
        if not fields.get('description'):
            errors.append(f'{path}: description is required')


def check_agents(errors):
    agents = list(ROOT.glob('plugins/*/agents/*.md'))
    if len(agents) != 10:
        errors.append(f'expected 10 agents, found {len(agents)}')
    for path in agents:
        fields = frontmatter(path.read_text())
        if fields is None:
            errors.append(f'{path}: missing frontmatter')
            continue
        unknown = set(fields) - AGENT_KEYS
        if unknown:
            errors.append(f'{path}: undocumented frontmatter keys {sorted(unknown)}')
        if fields.get('name') != path.stem:
            errors.append(f'{path}: name must equal the file stem')
        if fields.get('model') not in MODELS:
            errors.append(f'{path}: model must be one of {sorted(MODELS)}, not {fields.get("model")!r}')
        if fields.get('commandExecutionPolicy') not in POLICIES:
            errors.append(f'{path}: commandExecutionPolicy must be one of {sorted(POLICIES)}')
        if fields.get('mainAgent') != 'false' or fields.get('subagent') != 'true':
            errors.append(f'{path}: toolkit agents are subagents only (subagent: true, mainAgent: false)')
        tools = {t.strip() for t in fields.get('tools', '').strip('[]').split(',') if t.strip()}
        if not tools:
            errors.append(f'{path}: tools must list the allowed tools (an empty list means no tools)')
        if tools - TOOLS:
            errors.append(f'{path}: unknown tools {sorted(tools - TOOLS)} (a misspelled tool can hang the subagent)')
        if tools & WRITE_TOOLS:
            errors.append(f'{path}: specialists never get write tools')
        for skill in (s.strip() for s in fields.get('skills', '').strip('[]').split(',') if s.strip()):
            if not (path.parents[1] / skill / 'SKILL.md').exists():
                errors.append(f'{path}: skill {skill!r} does not exist in this plugin')


def check_hooks(errors):
    shared_guard = (REPO / 'shared/hooks/guard.py').read_bytes()
    shared_lint = (REPO / 'shared/hooks/swift_lint.py').read_bytes()
    for path in ROOT.glob('plugins/*/hooks.json'):
        data = json.loads(path.read_text())
        for hook_name, spec in data.items():
            if not isinstance(spec, dict):
                errors.append(f'{path}: hook {hook_name} must be an object')
                continue
            for event, handlers in spec.items():
                if event == 'enabled':
                    continue
                if event not in EVENTS:
                    errors.append(f'{path}: {hook_name} uses unknown event {event}')
                    continue
                for handler in handlers:
                    groups = handler.get('hooks') if event in GROUPED else [handler]
                    if event in GROUPED:
                        matcher = handler.get('matcher', '')
                        bad = {t for t in matcher.split('|') if t and t not in TOOLS and t != '*'}
                        if bad:
                            errors.append(f'{path}: {hook_name} matcher names unknown tools {sorted(bad)}')
                    for h in groups or []:
                        cmd = h.get('command', '')
                        parts = cmd.split()
                        script = next((p for p in parts if p.endswith('.py') or p.endswith('.sh')), None)
                        if script is None or '..' in script or not (path.parent / script).exists():
                            errors.append(f'{path}: {hook_name} command {cmd!r} must name a script inside the plugin')
                        if not isinstance(h.get('timeout', 30), int) or h.get('timeout', 30) > 60:
                            errors.append(f'{path}: {hook_name} timeout must be an integer of 60 or less')
                        if script and script.endswith('guard.py') and '--agent antigravity' not in cmd:
                            errors.append(f'{path}: guard must run with --agent antigravity')
        for name, shared in (('guard.py', shared_guard), ('swift_lint.py', shared_lint)):
            copy = path.parent / 'hooks' / name
            if copy.exists() and copy.read_bytes() != shared:
                errors.append(f'{copy}: differs from shared/hooks/{name}, run scripts/ci/check_parity.py --write')


def check_home(errors):
    allowed = {'AGENTS.md', 'machine.md.example', 'writing-style.md'}
    for path in (ROOT / 'home').iterdir():
        if path.name not in allowed:
            errors.append(f'{path}: not part of the documented layout (plugins carry rules, hooks and skills)')


def check_leaks(errors):
    for path in ROOT.rglob('*'):
        # The pr-review references are shared across layers and name every layer's paths on purpose.
        if not path.is_file() or path.suffix not in {'.md', '.json', '.py', '.sh'} or 'tests' in path.parts or 'scripts' in path.parts or 'references' in path.parts:
            continue
        text = path.read_text(errors='replace')
        for leak in LEAKS:
            if leak in text:
                errors.append(f'{path}: contains {leak!r}, which belongs to another layer or an old layout')


def check_links(errors):
    for path in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith(('#', 'mailto:')):
                continue
            link = target.split('#')[0]
            if link and not (path.parent / link).exists():
                errors.append(f'{path}: broken link {target}')


def check_generated_rules(errors):
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/sync_rules.py'), '--check'], capture_output=True, text=True)
    if result.returncode:
        errors.append('generated rules are stale: ' + result.stdout.strip())


def main():
    errors = []
    for check in (check_python, check_plugins, check_skills, check_agents, check_hooks, check_home, check_leaks, check_links, check_generated_rules):
        check(errors)
    for error in errors:
        print(f'::error::{error}')
    if errors:
        return 1
    skills = len(list(ROOT.glob('plugins/*/skills/*/SKILL.md')))
    print(f'Validated {skills} skills, 10 agents, {len(list(ROOT.glob("plugins/*/plugin.json")))} plugins, hook manifests, generated rules, home layout, local links and Python syntax.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
