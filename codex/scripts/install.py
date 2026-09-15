#!/usr/bin/env python3
"""Install the portable Codex setup, preserving unrelated user configuration."""
import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'ai-toolkit'


def merge_defaults(text, defaults):
    """Add absent keys to ordinary TOML tables without rewriting existing text."""
    current = tomllib.loads(text)
    for section, values in [('', {k: v for k, v in defaults.items() if not isinstance(v, dict)})] + [
            (k, v) for k, v in defaults.items() if isinstance(v, dict)]:
        present = current.get(section, {}) if section else current
        if not isinstance(present, dict):
            raise ValueError(f'Cannot merge non-table {section}')
        missing = {k: v for k, v in values.items() if k not in present}
        if not missing:
            continue
        additions = '\n'.join(f'{k} = {json.dumps(v)}' for k, v in missing.items()) + '\n'
        if not section:
            text = '# ai-toolkit defaults; existing personal values are preserved.\n' + additions + text
        else:
            match = re.search(r'^\[' + re.escape(section) + r'\]\s*(?:#.*)?$', text, re.M)
            if match:
                text = text[:match.end()] + '\n' + additions + text[match.end():]
            elif section in current:
                raise ValueError(f'Convert inline/dotted {section} configuration to a [{section}] table before merging')
            else:
                text = text.rstrip() + f'\n\n[{section}]\n' + additions
    expected = copy.deepcopy(current)
    for key, value in defaults.items():
        if isinstance(value, dict) and isinstance(expected.get(key, {}), dict):
            table = expected.setdefault(key, {})
            for child, default in value.items():
                table.setdefault(child, default)
        else:
            expected.setdefault(key, value)
    if tomllib.loads(text) != expected:
        raise ValueError('Cannot merge this TOML layout without changing existing values. Use ordinary top-level tables.')
    return text


def merged_guidance(existing, guidance):
    start, end = '<!-- ai-toolkit:start -->', '<!-- ai-toolkit:end -->'
    block = start + '\n' + guidance.rstrip() + '\n' + end
    if start in existing or end in existing:
        if existing.count(start) != 1 or existing.count(end) != 1 or existing.index(start) > existing.index(end):
            raise ValueError('Malformed ai-toolkit instruction markers')
        return existing[:existing.index(start)] + block + existing[existing.index(end) + len(end):]
    return (existing.rstrip() + '\n\n' if existing.strip() else '') + block + '\n'


def hook_group(command, label, matcher=None):
    group = {'hooks': [{'type': 'command', 'command': command, 'timeout': 10,
                        'statusMessage': 'ai-toolkit: ' + label}]}
    if matcher:
        group['matcher'] = matcher
    return group


def merged_hooks(existing, command, style_command):
    result = json.loads(json.dumps(existing))
    hooks = result.setdefault('hooks', {})
    for event in list(hooks):
        groups = []
        for group in hooks[event]:
            keep = [h for h in group.get('hooks', []) if not h.get('statusMessage', '').startswith('ai-toolkit: ')]
            if keep:
                groups.append({**group, 'hooks': keep})
        hooks[event] = groups
    hooks.setdefault('PreToolUse', []).append(hook_group(command, 'Check commands and protected files',
                                                        'Bash|apply_patch|Edit|Write|NotebookEdit|exec_command|shell_command|shell'))
    hooks.setdefault('UserPromptSubmit', []).append(hook_group(style_command, 'Refresh writing preferences'))
    return result


class Installer:
    def __init__(self, config_home, skills_home, dry_run=False):
        self.config_home = config_home
        self.skills_home = skills_home
        self.dry_run = dry_run
        self.stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        self.backup_root = config_home / 'backups' / ('ai-toolkit-' + self.stamp)
        self.backups = []

    def backup(self, path):
        if not os.path.lexists(path):
            return
        destination = self.backup_root / str(len(self.backups)) / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            destination.symlink_to(os.readlink(path), target_is_directory=path.is_dir())
        elif path.is_dir():
            shutil.copytree(path, destination)
        else:
            shutil.copy2(path, destination)
        self.backups.append({'original': str(path), 'backup': str(destination)})
        (self.backup_root / 'manifest.json').write_text(json.dumps(self.backups, indent=2) + '\n')

    def write(self, path, content, mode=0o600):
        if path.is_file() and not path.is_symlink() and path.read_text() == content:
            return
        print(('Would write ' if self.dry_run else 'Write ') + str(path))
        if self.dry_run:
            return
        self.backup(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
            stream.write(content)
            temp = Path(stream.name)
        temp.chmod(mode)
        os.replace(temp, path)

    def link(self, source, target):
        if target.is_symlink() and target.resolve() == source.resolve():
            return
        print(('Would link ' if self.dry_run else 'Link ') + str(target))
        if self.dry_run:
            return
        self.backup(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_dir() and not target.is_symlink():
            # Preserve the complete displaced directory in the backup before replacing it.
            displaced = self.backup_root / ('displaced-' + target.name)
            target.rename(displaced)
        elif os.path.lexists(target):
            target.unlink()
        target.symlink_to(source, target_is_directory=source.is_dir())

    def run(self):
        cfg = self.config_home
        config = cfg / 'config.toml'
        original = config.read_text() if config.exists() else ''
        merged = merge_defaults(original, tomllib.loads((ROOT / 'home/config.defaults.toml').read_text()))
        instructions = cfg / 'AGENTS.md'
        guidance = merged_guidance(instructions.read_text() if instructions.exists() else '',
                                   (ROOT / 'home/AGENTS.md').read_text())
        hook_file = cfg / 'hooks.json'
        old_hooks = json.loads(hook_file.read_text()) if hook_file.exists() else {}
        command = shlex.join([sys.executable, str(ROOT / 'hooks/guard.py')])
        style_command = shlex.join([sys.executable, str(ROOT / 'hooks/style.py'), str(cfg / 'guidance/writing-style.md')])
        hooks = merged_hooks(old_hooks, command, style_command)
        # Parse all input before changing any destination.
        agents = []
        for source in sorted((ROOT / 'agents').glob('*.toml')):
            content = source.read_text()
            content = content.replace('~/.codex/', str(cfg) + '/')
            content = content.replace('~/.agents/skills/', str(self.skills_home) + '/')
            role = tomllib.loads(content)['name']
            content += '\n[[hooks.PreToolUse]]\nmatcher = "Bash|apply_patch|Edit|Write|exec_command|shell_command|shell"\n'
            content += '\n[[hooks.PreToolUse.hooks]]\ntype = "command"\ncommand = ' + json.dumps(command + ' ' + shlex.quote(role)) + '\ntimeout = 10\n'
            tomllib.loads(content)
            agents.append((cfg / 'agents' / source.name, content))
        self.write(config, merged)
        self.write(instructions, guidance)
        self.write(hook_file, json.dumps(hooks, indent=2) + '\n')
        if not (cfg / 'machine.md').exists():
            self.write(cfg / 'machine.md', (ROOT / 'home/machine.md.example').read_text())
        self.link(ROOT / 'home/guidance/writing-style.md', cfg / 'guidance/writing-style.md')
        self.link(ROOT / 'home/guidance/android', cfg / 'guidance/android')
        self.link(ROOT / 'home/toolkit.rules', cfg / 'rules/ai-toolkit.rules')
        for source in sorted((ROOT / 'skills').iterdir()):
            if (source / 'SKILL.md').is_file():
                self.link(source, self.skills_home / source.name)
        for target, content in agents:
            self.write(target, content)
        if self.backups:
            print('Backups: ' + str(self.backup_root))
        if tomllib.loads(merged).get('features', {}).get('hooks') is False:
            print('Existing features.hooks=false was preserved. Enable hooks before relying on the guards.')
        if (cfg / 'AGENTS.override.md').exists():
            print('AGENTS.override.md exists and takes precedence over AGENTS.md. Review it to activate toolkit guidance.')
        print('Start a new Codex session. Open /hooks to review and trust the installed hooks, including specialist hooks.')
        print('Use /skills to confirm android-feature, android-bugfix, android-uplift-deps, android-run-app, android-standards and pr-review.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')))
    parser.add_argument('--skills-home', type=Path, default=Path.home() / '.agents/skills')
    args = parser.parse_args()
    Installer(args.codex_home.expanduser().absolute(), args.skills_home.expanduser().absolute(), args.dry_run).run()


if __name__ == '__main__':
    main()
