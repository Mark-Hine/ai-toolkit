"""Unit tests for the Antigravity installer."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory(prefix='antigravity dry ') as temp:
            home = Path(temp) / 'config'
            skills = Path(temp) / 'skills'
            with contextlib.redirect_stdout(io.StringIO()):
                installer.Installer(home, skills, dry_run=True).run()
            self.assertFalse(home.exists())
            self.assertFalse(skills.exists())

    def test_preserves_configuration_and_second_install_is_unchanged(self):
        with tempfile.TemporaryDirectory(prefix='antigravity install ') as temp:
            home = Path(temp) / 'config'
            skills = Path(temp) / 'skills'
            home.mkdir()

            # Existing user config
            existing_config = {'theme': 'dark', 'plugins': {'custom-plugin': {'enabled': True}}}
            (home / 'config.json').write_text(json.dumps(existing_config))
            (home / 'AGENTS.md').write_text('# My Custom Rules\nAlways be polite.\n')
            (home / 'machine.md').write_text('Private device facts.\n')
            custom_hook = {'matcher': 'run_command', 'hooks': [{'type': 'command', 'command': 'my-check'}]}
            (home / 'hooks.json').write_text(json.dumps({'custom-guard': {'PreToolUse': [custom_hook]}}))

            with contextlib.redirect_stdout(io.StringIO()):
                installer.Installer(home, skills).run()

            # Verify config.json
            cfg = json.loads((home / 'config.json').read_text())
            self.assertEqual('dark', cfg['theme'])
            self.assertTrue(cfg['plugins']['custom-plugin']['enabled'])
            self.assertTrue(cfg['plugins']['android-kit']['enabled'])
            self.assertTrue(cfg['plugins']['ios-kit']['enabled'])
            self.assertTrue(cfg['plugins']['pr-review']['enabled'])

            # Verify AGENTS.md & GEMINI.md
            agents_text = (home / 'AGENTS.md').read_text()
            self.assertIn('Always be polite.', agents_text)
            self.assertIn('<!-- ai-toolkit:start -->', agents_text)
            self.assertIn('<!-- ai-toolkit:end -->', agents_text)
            self.assertTrue((home / 'GEMINI.md').exists())

            # Verify machine.md preserved
            self.assertEqual('Private device facts.\n', (home / 'machine.md').read_text())

            # Verify hooks.json
            hooks = json.loads((home / 'hooks.json').read_text())
            self.assertIn('custom-guard', hooks)
            self.assertEqual(hooks['custom-guard']['PreToolUse'][0], custom_hook)
            self.assertIn('ai-toolkit-guard', hooks)
            self.assertIn('ai-toolkit-swift-lint', hooks)

            # Verify guidance links
            self.assertEqual((home / 'guidance/common.md').resolve(),
                             (ROOT.parent / 'shared/guidance/common.md').resolve())
            self.assertEqual((home / 'guidance/writing-style.md').resolve(),
                             (ROOT / 'home/guidance/writing-style.md').resolve())
            self.assertEqual((home / 'guidance/android').resolve(),
                             (ROOT / 'home/guidance/android').resolve())
            self.assertEqual((home / 'guidance/ios').resolve(),
                             (ROOT / 'home/guidance/ios').resolve())

            # Verify plugins linked
            self.assertTrue((home / 'plugins/android-kit').is_symlink())
            self.assertTrue((home / 'plugins/ios-kit').is_symlink())
            self.assertTrue((home / 'plugins/pr-review').is_symlink())

            # Verify skills linked
            self.assertEqual(11, len(list(skills.iterdir())))
            self.assertEqual(11, len(list((home / 'skills').iterdir())))
            for s in ('android-feature', 'android-bugfix', 'ios-feature', 'ios-bugfix', 'pr-review'):
                self.assertTrue((skills / s).is_symlink())
                self.assertTrue(((home / 'skills') / s).is_symlink())

            # Verify idempotence on second run
            before_files = {p: p.read_bytes() for p in home.rglob('*') if p.is_file()}
            with contextlib.redirect_stdout(io.StringIO()):
                installer.Installer(home, skills).run()
            after_files = {p: p.read_bytes() for p in home.rglob('*') if p.is_file()}
            self.assertEqual(before_files, after_files)


if __name__ == '__main__':
    unittest.main()
