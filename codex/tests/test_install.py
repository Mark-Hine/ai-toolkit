import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def test_preserves_configuration_and_second_install_is_unchanged(self):
        with tempfile.TemporaryDirectory(prefix='toolkit install ') as temp:
            home = Path(temp) / 'config home'
            skills = Path(temp) / 'skills'
            home.mkdir()
            existing = '# personal comment\nmodel = "custom-model"\n[features]\nhooks = false\n[projects."/workspace"]\ntrust_level = "trusted"\n'
            (home / 'config.toml').write_text(existing)
            (home / 'AGENTS.md').write_text('Keep my personal instructions.\n')
            (home / 'machine.md').write_text('Private device facts.\n')
            hook = {'hooks': {
                'PreToolUse': [{'hooks': [{'type': 'command', 'command': 'custom-check'}]}],
                'PostToolUse': [{'hooks': [{'type': 'command', 'command': 'custom-lint'}]}],
                'UserPromptSubmit': [{'hooks': [
                    {'type': 'command', 'command': 'old-style', 'statusMessage': 'ai-toolkit: Refresh writing preferences'},
                    {'type': 'command', 'command': 'custom-prompt'}]}]}}
            (home / 'hooks.json').write_text(json.dumps(hook))
            with contextlib.redirect_stdout(io.StringIO()):
                installer.Installer(home, skills).run()
            config = tomllib.loads((home / 'config.toml').read_text())
            self.assertEqual(config['model'], 'custom-model')
            self.assertFalse(config['features']['hooks'])
            self.assertEqual(config['projects']['/workspace']['trust_level'], 'trusted')
            self.assertEqual(config['sandbox_mode'], 'workspace-write')
            self.assertIn('# personal comment', (home / 'config.toml').read_text())
            self.assertIn('Keep my personal instructions.', (home / 'AGENTS.md').read_text())
            self.assertEqual((home / 'machine.md').read_text(), 'Private device facts.\n')
            self.assertEqual(json.loads((home / 'hooks.json').read_text())['hooks']['PreToolUse'][0], hook['hooks']['PreToolUse'][0])
            installed_hooks = json.loads((home / 'hooks.json').read_text())['hooks']
            self.assertEqual(installed_hooks['PostToolUse'][0], hook['hooks']['PostToolUse'][0])
            self.assertEqual(installed_hooks['UserPromptSubmit'], [
                {'hooks': [{'type': 'command', 'command': 'custom-prompt'}]}])
            self.assertEqual(len(installed_hooks['PostToolUse']), 2)
            self.assertEqual(len(installed_hooks['PreToolUse']), 2)
            self.assertEqual(len(list(skills.iterdir())), 11)
            self.assertEqual((home / 'guidance/ios').resolve(), ROOT / 'home/guidance/ios')
            self.assertEqual((home / 'guidance/common.md').read_text(),
                             (ROOT.parent / 'shared/guidance/common.md').read_text())
            for role in ('ios-researcher', 'ios-reviewer', 'ios-verifier'):
                agent = tomllib.loads((home / 'agents' / (role + '.toml')).read_text())
                self.assertIn(str(home), agent['developer_instructions'])
                self.assertTrue(agent['hooks']['PreToolUse'][0]['hooks'][0]['command'].endswith(role))
                self.assertEqual(agent['sandbox_mode'], 'workspace-write' if role == 'ios-verifier' else 'read-only')
            before = {p: p.read_bytes() for p in home.rglob('*') if p.is_file()}
            with contextlib.redirect_stdout(io.StringIO()):
                installer.Installer(home, skills).run()
            after = {p: p.read_bytes() for p in home.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            manifests = list((home / 'backups').glob('*/manifest.json'))
            self.assertEqual(len(manifests), 1)
            backups = json.loads(manifests[0].read_text())
            old_config = next(item for item in backups if item['original'] == str(home / 'config.toml'))
            self.assertEqual(Path(old_config['backup']).read_text(), existing)

    def test_multiline_string_table_header_cannot_corrupt_instructions(self):
        original = 'developer_instructions = """Example:\n[features]\nKeep this.\n"""\n\n[features]\n'
        with self.assertRaises(ValueError):
            installer.merge_defaults(original, {'features': {'hooks': True}})

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            with contextlib.redirect_stdout(io.StringIO()):
                installer.Installer(Path(temp) / 'config', Path(temp) / 'skills', True).run()
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_invalid_configuration_fails_before_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            (home / 'config.toml').write_text('this is not TOML')
            with self.assertRaises(tomllib.TOMLDecodeError):
                installer.Installer(home, home / 'skills').run()
            self.assertEqual([p.name for p in home.iterdir()], ['config.toml'])

    def test_conflicting_skill_directory_is_backed_up(self):
        with tempfile.TemporaryDirectory() as temp:
            home, skills = Path(temp) / 'config', Path(temp) / 'skills'
            old = skills / 'android-feature'
            old.mkdir(parents=True)
            (old / 'notes.txt').write_text('Keep these notes')
            with contextlib.redirect_stdout(io.StringIO()):
                installer.Installer(home, skills).run()
            self.assertTrue(old.is_symlink())
            notes = list((home / 'backups').rglob('notes.txt'))
            self.assertTrue(notes)
            self.assertTrue(all(p.read_text() == 'Keep these notes' for p in notes))


if __name__ == '__main__':
    unittest.main()
