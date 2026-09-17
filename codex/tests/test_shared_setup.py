"""Verify the shared preferences and Claude installer without network calls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which('jq'), 'Claude installer requires jq')
class SharedSetupTests(unittest.TestCase):
    def test_claude_reinstall_preserves_custom_hooks_without_duplicates(self):
        with tempfile.TemporaryDirectory(prefix='claude install ') as temp:
            temp = Path(temp)
            home = temp / 'config'
            home.mkdir()
            binaries = temp / 'bin'
            binaries.mkdir()
            fake_cli = binaries / 'claude'
            fake_cli.write_text('#!/bin/sh\nexit 0\n')
            fake_cli.chmod(0o755)
            custom = {'hooks': [{'type': 'command', 'command': 'custom-prompt'}]}
            lint = {'hooks': [{'type': 'command', 'command': 'custom-lint'}]}
            original = {'model': 'personal-model', 'hooks': {'UserPromptSubmit': [custom], 'PostToolUse': [lint]},
                        'permissions': {'allow': ['Read(example)']}}
            (home / 'settings.json').write_text(json.dumps(original))
            (home / 'machine.md').write_text('Private machine facts.\n')
            env = dict(os.environ, CLAUDE_CONFIG_DIR=str(home), MARKETPLACE_SOURCE=str(ROOT),
                       PATH=str(binaries) + os.pathsep + os.environ['PATH'])
            snapshots = []
            for _ in range(2):
                subprocess.run(['bash', str(ROOT / 'claude/install.sh')], env=env,
                               text=True, capture_output=True, check=True)
                snapshots.append(json.loads((home / 'settings.json').read_text()))
            self.assertEqual(snapshots[0], snapshots[1])
            self.assertEqual(snapshots[1]['model'], 'personal-model')
            self.assertIn(custom, snapshots[1]['hooks']['UserPromptSubmit'])
            self.assertEqual(len(snapshots[1]['hooks']['UserPromptSubmit']), 2)
            self.assertEqual(snapshots[1]['hooks']['PostToolUse'], [lint])
            self.assertIn('Read(example)', snapshots[1]['permissions']['allow'])
            self.assertEqual((home / 'rules/common.md').resolve(), ROOT / 'shared/guidance/common.md')
            self.assertEqual((home / 'machine.md').read_text(), 'Private machine facts.\n')


if __name__ == '__main__':
    unittest.main()
