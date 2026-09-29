"""Cross-layer parity checks for the Antigravity port."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SharedSetupTests(unittest.TestCase):
    def test_shared_guidance_exists(self):
        common = ROOT / 'shared/guidance/common.md'
        self.assertTrue(common.is_file())
        self.assertIn('Shared personal defaults', common.read_text())

    def test_skill_parity_with_codex(self):
        codex_skills = {p.name for p in (ROOT / 'codex/skills').iterdir() if (p / 'SKILL.md').is_file()}
        agy_skills = {p.name for p in (ROOT / 'antigravity/plugins').glob('*/skills/*') if (p / 'SKILL.md').is_file()}
        self.assertEqual(codex_skills, agy_skills)

    def test_plugin_parity_with_claude(self):
        claude_plugins = {p.name for p in (ROOT / 'claude/plugins').iterdir() if p.is_dir()}
        agy_plugins = {p.name for p in (ROOT / 'antigravity/plugins').iterdir() if p.is_dir()}
        # guard-kit is Claude-only. Antigravity registers the same guard inside each kit's hooks.json.
        self.assertEqual(claude_plugins - {'guard-kit'}, agy_plugins)

    def test_generated_rules_are_current(self):
        result = subprocess.run([sys.executable, str(ROOT / 'antigravity/scripts/sync_rules.py'), '--check'], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_hooks_are_the_shared_module(self):
        shared = (ROOT / 'shared/hooks/guard.py').read_bytes()
        for kit in ('android-kit', 'ios-kit'):
            self.assertEqual(shared, (ROOT / 'antigravity/plugins' / kit / 'hooks/guard.py').read_bytes(), kit)
        self.assertEqual((ROOT / 'shared/hooks/swift_lint.py').read_bytes(), (ROOT / 'antigravity/plugins/ios-kit/hooks/swift_lint.py').read_bytes())


if __name__ == '__main__':
    unittest.main()
