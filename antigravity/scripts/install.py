#!/usr/bin/env python3
"""Install the portable Antigravity setup, preserving unrelated user configuration."""
import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'ai-toolkit'


def merge_json_defaults(existing_obj, defaults_obj):
    """Deep merge defaults into existing dictionary without overwriting existing keys."""
    merged = copy.deepcopy(existing_obj)
    for key, value in defaults_obj.items():
        if key not in merged:
            merged[key] = copy.deepcopy(value)
        elif isinstance(value, dict) and isinstance(merged[key], dict):
            merged[key] = merge_json_defaults(merged[key], value)
    return merged


def merged_guidance(existing, guidance):
    """Replace or append managed ai-toolkit instruction block."""
    start, end = '<!-- ai-toolkit:start -->', '<!-- ai-toolkit:end -->'
    block = start + '\n' + guidance.rstrip() + '\n' + end
    if start in existing or end in existing:
        if existing.count(start) != 1 or existing.count(end) != 1 or existing.index(start) > existing.index(end):
            raise ValueError('Malformed ai-toolkit instruction markers')
        return existing[:existing.index(start)] + block + existing[existing.index(end) + len(end):]
    return (existing.rstrip() + '\n\n' if existing.strip() else '') + block + '\n'


def merged_hooks(existing_hooks, guard_cmd, lint_cmd):
    """Merge Antigravity hooks, updating ai-toolkit hooks while preserving custom hooks."""
    hooks = copy.deepcopy(existing_hooks) if isinstance(existing_hooks, dict) else {}
    hooks['ai-toolkit-guard'] = {
        'PreToolUse': [
            {
                'matcher': 'run_command|write_to_file|replace_file_content',
                'hooks': [
                    {
                        'type': 'command',
                        'command': guard_cmd,
                        'timeout': 10
                    }
                ]
            }
        ]
    }
    hooks['ai-toolkit-swift-lint'] = {
        'PostToolUse': [
            {
                'matcher': 'write_to_file|replace_file_content',
                'hooks': [
                    {
                        'type': 'command',
                        'command': lint_cmd,
                        'timeout': 60
                    }
                ]
            }
        ]
    }
    return hooks


class Installer:
    def __init__(self, config_home, skills_home, dry_run=False):
        self.config_home = Path(config_home)
        self.skills_home = Path(skills_home)
        self.dry_run = dry_run
        self.stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        self.backup_root = self.config_home / 'backups' / ('ai-toolkit-' + self.stamp)
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
        source = Path(source)
        target = Path(target)
        if target.is_symlink() and target.resolve() == source.resolve():
            return
        print(('Would link ' if self.dry_run else 'Link ') + str(target))
        if self.dry_run:
            return
        self.backup(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_dir() and not target.is_symlink():
            displaced = self.backup_root / ('displaced-' + target.name)
            target.rename(displaced)
        elif os.path.lexists(target):
            target.unlink()
        target.symlink_to(source, target_is_directory=source.is_dir())

    def run(self):
        cfg = self.config_home
        if not self.dry_run:
            cfg.mkdir(parents=True, exist_ok=True)
            self.skills_home.mkdir(parents=True, exist_ok=True)

        # 1. Config defaults (plugins enabled)
        config_file = cfg / 'config.json'
        old_config = json.loads(config_file.read_text()) if config_file.exists() else {}
        defaults = json.loads((ROOT / 'home/config.defaults.json').read_text())
        merged_cfg = merge_json_defaults(old_config, defaults)
        self.write(config_file, json.dumps(merged_cfg, indent=2) + '\n')

        # 2. Managed instructions block (AGENTS.md & GEMINI.md)
        agents_file = cfg / 'AGENTS.md'
        existing_agents = agents_file.read_text() if agents_file.exists() else ''
        new_guidance = merged_guidance(existing_agents, (ROOT / 'home/AGENTS.md').read_text())
        self.write(agents_file, new_guidance)

        gemini_file = cfg / 'GEMINI.md'
        if not gemini_file.exists():
            self.link(agents_file, gemini_file)

        # 3. Lifecycle hooks
        hook_file = cfg / 'hooks.json'
        old_hooks = json.loads(hook_file.read_text()) if hook_file.exists() else {}
        guard_cmd = shlex.join([sys.executable, str(ROOT / 'hooks/guard.py')])
        lint_cmd = shlex.join([sys.executable, str(ROOT / 'hooks/swift_lint.py')])
        hooks = merged_hooks(old_hooks, guard_cmd, lint_cmd)
        self.write(hook_file, json.dumps(hooks, indent=2) + '\n')

        # 4. Machine facts template
        machine_file = cfg / 'machine.md'
        if not machine_file.exists():
            self.write(machine_file, (ROOT / 'home/machine.md.example').read_text())

        # 5. Guidance links
        self.link(ROOT / 'home/guidance/writing-style.md', cfg / 'guidance/writing-style.md')
        self.link(ROOT.parent / 'shared/guidance/common.md', cfg / 'guidance/common.md')
        self.link(ROOT / 'home/guidance/android', cfg / 'guidance/android')
        self.link(ROOT / 'home/guidance/ios', cfg / 'guidance/ios')

        # 6. Plugins link
        for plugin_dir in sorted((ROOT / 'plugins').iterdir()):
            if plugin_dir.is_dir() and (plugin_dir / 'plugin.json').is_file():
                self.link(plugin_dir, cfg / 'plugins' / plugin_dir.name)

        # 7. JSON configs
        self.write(cfg / 'plugins.json', (ROOT / 'home/plugins.json').read_text())
        self.write(cfg / 'skills.json', (ROOT / 'home/skills.json').read_text())

        # 8. Skills linked to config_home/skills and skills_home for flat discovery
        for skill_dir in sorted((ROOT / 'skills').iterdir()):
            if (skill_dir / 'SKILL.md').is_file():
                self.link(skill_dir, cfg / 'skills' / skill_dir.name)
                self.link(skill_dir, self.skills_home / skill_dir.name)

        if self.backups:
            print('Backups: ' + str(self.backup_root))

        print('Installed Antigravity configuration to: ' + str(cfg))
        print('Skills linked to: ' + str(self.skills_home))
        print('Start a new Antigravity session to verify discovered skills and plugins.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--gemini-home', type=Path,
                        default=Path(os.environ.get('ANTIGRAVITY_HOME',
                                     os.environ.get('GEMINI_CONFIG_DIR',
                                     Path.home() / '.gemini/config'))),
                        help='Antigravity global configuration directory')
    parser.add_argument('--skills-home', type=Path,
                        default=Path(os.environ.get('SKILLS_HOME', Path.home() / '.agents/skills')),
                        help='Directory for portable skill discovery')
    args = parser.parse_args()
    Installer(args.gemini_home.expanduser().absolute(),
              args.skills_home.expanduser().absolute(),
              args.dry_run).run()


if __name__ == '__main__':
    main()
