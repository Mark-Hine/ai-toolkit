"""Unit tests for the Antigravity installer."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
PLUGINS = sorted(p.name for p in (ROOT / 'plugins').iterdir() if (p / 'plugin.json').is_file())


def run(home, dry_run=False):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        installer.Installer(home, dry_run=dry_run).run()
    return out.getvalue()


class InstallTests(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory(prefix='antigravity dry ') as temp:
            home = Path(temp) / 'config'
            run(home, dry_run=True)
            self.assertFalse(home.exists())

    def test_installs_documented_layout_and_nothing_else(self):
        with tempfile.TemporaryDirectory(prefix='antigravity install ') as temp:
            home = Path(temp) / 'config'
            run(home)
            for name in PLUGINS:
                link = home / 'plugins' / name
                self.assertTrue(link.is_symlink(), name)
                self.assertEqual((ROOT / 'plugins' / name).resolve(), link.resolve())
            for name in ('common.md', 'design-standards.md', 'writing-style.md'):
                self.assertTrue((home / 'guidance' / name).is_symlink(), name)
            self.assertIn('<!-- ai-toolkit:start -->', (home / 'AGENTS.md').read_text())
            self.assertTrue((home / 'machine.md').is_file())
            for absent in ('config.json', 'hooks.json', 'plugins.json', 'skills.json', 'GEMINI.md', 'skills', 'guidance/android', 'guidance/ios'):
                self.assertFalse(os.path.lexists(home / absent), absent)

    def test_preserves_user_files_and_is_idempotent(self):
        with tempfile.TemporaryDirectory(prefix='antigravity install ') as temp:
            home = Path(temp) / 'config'
            home.mkdir()
            (home / 'config.json').write_text('{"theme": "dark"}')
            (home / 'AGENTS.md').write_text('# My Custom Rules\nAlways be polite.\n')
            (home / 'machine.md').write_text('Private device facts.\n')
            custom = {'custom-guard': {'PreToolUse': [{'matcher': 'run_command', 'hooks': [{'type': 'command', 'command': 'my-check'}]}]}}
            (home / 'hooks.json').write_text(json.dumps(custom))
            run(home)
            snapshot = {p: os.readlink(p) if p.is_symlink() else p.read_text() for p in home.rglob('*') if p.is_symlink() or p.is_file()}
            run(home)
            after = {p: os.readlink(p) if p.is_symlink() else p.read_text() for p in home.rglob('*') if p.is_symlink() or p.is_file()}
            self.assertEqual({k: v for k, v in snapshot.items() if 'backups' not in str(k)}, {k: v for k, v in after.items() if 'backups' not in str(k)})
            self.assertEqual('{"theme": "dark"}', (home / 'config.json').read_text())
            self.assertIn('Always be polite.', (home / 'AGENTS.md').read_text())
            self.assertEqual('Private device facts.\n', (home / 'machine.md').read_text())
            self.assertEqual(custom, json.loads((home / 'hooks.json').read_text()))

    def test_legacy_layout_is_cleaned_up_but_foreign_links_survive(self):
        with tempfile.TemporaryDirectory(prefix='antigravity legacy ') as temp:
            home = Path(temp) / 'config'
            (home / 'guidance').mkdir(parents=True)
            (home / 'skills').mkdir()
            foreign = Path(temp) / 'elsewhere/skills/other-skill'
            foreign.mkdir(parents=True)
            hooks = {'custom-guard': {'PreToolUse': []}, 'ai-toolkit-guard': {'PreToolUse': []}, 'ai-toolkit-swift-lint': {'PostToolUse': []}}
            (home / 'hooks.json').write_text(json.dumps(hooks))
            (home / 'plugins.json').write_text(installer.LEGACY_JSON['plugins.json'])
            (home / 'skills.json').write_text('{"entries": [{"path": "~/my-skills"}]}')
            (home / 'guidance/android').symlink_to(ROOT / 'plugins', target_is_directory=True)  # any path inside antigravity/
            (home / 'skills/android-feature').symlink_to(ROOT / 'plugins/android-kit/skills/android-feature', target_is_directory=True)
            (home / 'skills/other-skill').symlink_to(foreign, target_is_directory=True)
            (home / 'AGENTS.md').write_text('# mine\n')
            (home / 'GEMINI.md').symlink_to('AGENTS.md')
            with unittest.mock.patch.object(installer.Path, 'home', return_value=Path(temp) / 'nohome'):
                output = run(home)
            self.assertEqual({'custom-guard': {'PreToolUse': []}}, json.loads((home / 'hooks.json').read_text()))
            self.assertFalse((home / 'plugins.json').exists())
            self.assertTrue((home / 'skills.json').exists(), 'a user-written skills.json is kept')
            self.assertFalse(os.path.lexists(home / 'guidance/android'))
            self.assertFalse(os.path.lexists(home / 'skills/android-feature'))
            self.assertTrue((home / 'skills/other-skill').is_symlink(), 'links into other repos are kept')
            self.assertFalse(os.path.lexists(home / 'GEMINI.md'))
            self.assertIn('Note:', output)

    def test_invalid_markers_fail_before_mutation(self):
        with tempfile.TemporaryDirectory(prefix='antigravity bad ') as temp:
            home = Path(temp) / 'config'
            home.mkdir()
            (home / 'AGENTS.md').write_text('<!-- ai-toolkit:end -->\n<!-- ai-toolkit:start -->\n')
            with self.assertRaises(ValueError):
                run(home)
            self.assertFalse((home / 'plugins').exists())


import unittest.mock  # noqa: E402

if __name__ == '__main__':
    unittest.main()
