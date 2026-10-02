#!/usr/bin/env python3
"""Install the portable Antigravity setup, preserving unrelated user configuration.

Layout after install (documented in the bundled agy-customizations docs and the plugin skill):
  ~/.gemini/config/AGENTS.md            managed ai-toolkit block, merged into the user's file
  ~/.gemini/config/machine.md           created from home/machine.md.example when absent
  ~/.gemini/config/guidance/*.md        symlinks to shared/guidance and home/writing-style.md
  ~/.gemini/config/plugins/<name>       symlink to each plugin in this checkout
Plugins are discovered from ~/.gemini/config/plugins/*/plugin.json by both the IDE and the CLI, and
they are enabled by default. Hooks, rules and agents ship inside each plugin, so nothing is written
to config.json, hooks.json, plugins.json or skills.json.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
LEGACY_HOOKS = ('ai-toolkit-guard', 'ai-toolkit-swift-lint')
LEGACY_JSON = {
    'plugins.json': '{\n  "entries": [\n    {\n      "path": "plugins"\n    }\n  ]\n}\n',
    'skills.json': '{\n  "entries": [\n    {\n      "path": "skills"\n    }\n  ]\n}\n',
}


def merged_guidance(existing, guidance):
    """Replace or append the managed ai-toolkit instruction block."""
    start, end = '<!-- ai-toolkit:start -->', '<!-- ai-toolkit:end -->'
    block = start + '\n' + guidance.rstrip() + '\n' + end
    if start in existing or end in existing:
        if existing.count(start) != 1 or existing.count(end) != 1 or existing.index(start) > existing.index(end):
            raise ValueError('Malformed ai-toolkit instruction markers')
        return existing[:existing.index(start)] + block + existing[existing.index(end) + len(end):]
    return (existing.rstrip() + '\n\n' if existing.strip() else '') + block + '\n'


def points_into_toolkit(path):
    """True for a symlink whose target lives inside this checkout's antigravity/ folder."""
    try:
        return path.is_symlink() and Path(os.path.realpath(path)).is_relative_to(ROOT.resolve())
    except (OSError, ValueError):
        return False


class Installer:
    def __init__(self, config_home, dry_run=False):
        self.config_home = Path(config_home)
        self.dry_run = dry_run
        self.stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        self.backup_root = self.config_home / 'backups' / ('ai-toolkit-' + self.stamp)
        self.backups = []
        self.notes = []

    def say(self, verb, path):
        print(('Would ' + verb.lower() if self.dry_run else verb) + ' ' + str(path))

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
        self.say('Write', path)
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
        source, target = Path(source), Path(target)
        if target.is_symlink() and target.resolve() == source.resolve():
            return
        self.say('Link', target)
        if self.dry_run:
            return
        self.backup(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_dir() and not target.is_symlink():
            target.rename(self.backup_root / ('displaced-' + target.name))
        elif os.path.lexists(target):
            target.unlink()
        target.symlink_to(source, target_is_directory=source.is_dir())

    def remove(self, path, reason):
        if not os.path.lexists(path):
            return
        self.say('Remove', path)
        self.notes.append(f'removed {path} ({reason})')
        if self.dry_run:
            return
        self.backup(path)
        path.unlink()

    def migrate(self, cfg):
        """Undo what earlier installers wrote outside the plugins. Only repo-owned things are touched."""
        hook_file = cfg / 'hooks.json'
        if hook_file.is_file():
            try:
                hooks = json.loads(hook_file.read_text())
            except ValueError:
                hooks = None
            if isinstance(hooks, dict) and any(name in hooks for name in LEGACY_HOOKS):
                for name in LEGACY_HOOKS:
                    hooks.pop(name, None)
                self.notes.append('removed the ai-toolkit entries from hooks.json (hooks now ship inside each plugin)')
                if hooks:
                    self.write(hook_file, json.dumps(hooks, indent=2) + '\n')
                else:
                    self.remove(hook_file, 'only ai-toolkit hooks were in it')
        for name, legacy in LEGACY_JSON.items():
            path = cfg / name
            if path.is_file() and path.read_text() == legacy:
                self.remove(path, 'written by an earlier ai-toolkit installer, its relative paths resolve against the workspace')
        for path in (cfg / 'guidance/android', cfg / 'guidance/ios', cfg / 'GEMINI.md'):
            if points_into_toolkit(path) or (path.name == 'GEMINI.md' and path.is_symlink() and Path(os.readlink(path)).name == 'AGENTS.md'):
                self.remove(path, 'the rules now ship inside the plugins')
        for skills_dir in (cfg / 'skills', Path.home() / '.agents/skills'):
            if skills_dir.is_dir():
                for entry in sorted(skills_dir.iterdir()):
                    if points_into_toolkit(entry):
                        self.remove(entry, 'skills now ship inside the plugins')

    def run(self):
        cfg = self.config_home
        if not self.dry_run:
            cfg.mkdir(parents=True, exist_ok=True)
        agents_file = cfg / 'AGENTS.md'
        existing = agents_file.read_text() if agents_file.exists() else ''
        self.write(agents_file, merged_guidance(existing, (ROOT / 'home/AGENTS.md').read_text()))
        machine_file = cfg / 'machine.md'
        if not machine_file.exists():
            self.write(machine_file, (ROOT / 'home/machine.md.example').read_text())
        self.link(REPO / 'shared/guidance/common.md', cfg / 'guidance/common.md')
        self.link(REPO / 'shared/guidance/kotlin.md', cfg / 'guidance/kotlin.md')
        self.link(REPO / 'shared/guidance/design-standards.md', cfg / 'guidance/design-standards.md')
        self.link(ROOT / 'home/writing-style.md', cfg / 'guidance/writing-style.md')
        for plugin_dir in sorted((ROOT / 'plugins').iterdir()):
            if plugin_dir.is_dir() and (plugin_dir / 'plugin.json').is_file():
                self.link(plugin_dir, cfg / 'plugins' / plugin_dir.name)
        self.migrate(cfg)
        if self.backups:
            print('Backups: ' + str(self.backup_root))
        for note in self.notes:
            print('Note: ' + note)
        print('Installed Antigravity configuration to: ' + str(cfg))
        print('Restart Antigravity (agy or the IDE). New plugin directories are discovered at startup.')
        print('Check: agy agents  ->  android-researcher, android-reviewer, android-verifier, ios-*, ui-reviewer')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--gemini-home', type=Path, default=Path(os.environ.get('ANTIGRAVITY_HOME', Path.home() / '.gemini/config')),
                        help='Antigravity global configuration directory (default ~/.gemini/config)')
    args = parser.parse_args()
    Installer(args.gemini_home.expanduser().absolute(), args.dry_run).run()


if __name__ == '__main__':
    main()
