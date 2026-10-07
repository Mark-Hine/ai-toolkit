"""Exercise the Claude installer in an isolated home without plugin network calls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which('jq'), 'Claude installer requires jq')
class InstallTests(unittest.TestCase):
    def test_shared_kotlin_rule_installs_with_loader_and_preserves_personal_settings(self):
        with tempfile.TemporaryDirectory(prefix='claude kotlin install ') as temp:
            home = Path(temp) / 'config'
            home.mkdir()
            (home / 'settings.json').write_text('{"model": "personal-model"}')
            (home / 'machine.md').write_text('Private facts.\n')
            binaries = Path(temp) / 'bin'
            binaries.mkdir()
            stub = binaries / 'claude'
            stub.write_text('#!/bin/sh\ncase "$*" in\n  "plugin marketplace list --json"|"plugin list --json") echo "[]" ;;\n  *) exit 0 ;;\nesac\n')
            stub.chmod(0o755)
            env = dict(os.environ, CLAUDE_CONFIG_DIR=str(home), MARKETPLACE_SOURCE=str(ROOT),
                       PATH=str(binaries) + os.pathsep + os.environ['PATH'])
            for _ in range(2):
                subprocess.run(['bash', str(ROOT / 'claude/install.sh')], env=env,
                               check=True, capture_output=True, text=True)
                rule = home / 'rules/kotlin.md'
                self.assertTrue(rule.is_symlink())
                self.assertEqual(rule.resolve(), ROOT / 'shared/guidance/kotlin.md')
                self.assertIn('"**/*.kt"', rule.read_text())
                self.assertIn('~/.claude/rules/kotlin.md', (home / 'CLAUDE.md').read_text())
                assets = home / 'rules/design-assets.md'
                self.assertTrue(assets.is_symlink())
                self.assertEqual(assets.resolve(), ROOT / 'shared/guidance/design-assets.md')
                self.assertIn('"**/DESIGN.md"', assets.read_text())
                self.assertIn('~/.claude/rules/design-assets.md', (home / 'CLAUDE.md').read_text())
                self.assertEqual(json.loads((home / 'settings.json').read_text())['model'], 'personal-model')
                self.assertEqual((home / 'machine.md').read_text(), 'Private facts.\n')
                self.assertFalse((home / 'rules/references').exists(), 'Rationale stays in skill references')
                web = home / 'rules/web'
                self.assertTrue(web.is_symlink())
                self.assertIn('"**/*.tsx"', (web / 'react.md').read_text())


if __name__ == '__main__':
    unittest.main()
