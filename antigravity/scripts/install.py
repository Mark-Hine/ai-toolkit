#!/usr/bin/env python3
"""Install the portable Antigravity setup, preserving unrelated user configuration.

Layout after install (documented in the bundled agy-customizations docs and the plugin skill):
  ~/.gemini/config/AGENTS.md            managed ai-toolkit block, merged into the user's file
  ~/.gemini/config/machine.md           created from home/machine.md.example when absent
  ~/.gemini/config/guidance/*.md        symlinks to shared/guidance
  ~/.gemini/config/plugins/<name>       symlink to each plugin in this checkout
Plugins are discovered from ~/.gemini/config/plugins/*/plugin.json by both the IDE and the CLI, and
they are enabled by default. Hooks, rules and agents ship inside each plugin, so nothing is written
to config.json, hooks.json, plugins.json or skills.json.
"""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(REPO / 'shared'))

import install_common  # noqa: E402
LEGACY_HOOKS = ('ai-toolkit-guard', 'ai-toolkit-swift-lint')
LEGACY_JSON = {
    'plugins.json': '{\n  "entries": [\n    {\n      "path": "plugins"\n    }\n  ]\n}\n',
    'skills.json': '{\n  "entries": [\n    {\n      "path": "skills"\n    }\n  ]\n}\n',
}


def points_into_toolkit(path):
    """True for a symlink whose target lives inside this checkout's antigravity/ folder."""
    try:
        return path.is_symlink() and Path(os.path.realpath(path)).is_relative_to(ROOT.resolve())
    except (OSError, ValueError):
        return False


class Installer(install_common.Installer):
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
        self.write(agents_file, self.merge_instructions(agents_file, ROOT / 'home/AGENTS.md'))
        self.create_machine_file(ROOT / 'home/machine.md.example')
        self.link_shared_guidance()
        for plugin_dir in sorted((ROOT / 'plugins').iterdir()):
            if plugin_dir.is_dir() and (plugin_dir / 'plugin.json').is_file():
                self.link(plugin_dir, cfg / 'plugins' / plugin_dir.name)
        self.migrate(cfg)
        self.report()
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
