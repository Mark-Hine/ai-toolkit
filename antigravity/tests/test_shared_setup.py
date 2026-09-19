"""Verify shared preferences and cross-agent parity for Antigravity."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SharedSetupTests(unittest.TestCase):
    def test_shared_guidance_exists(self):
        common = ROOT / 'shared/guidance/common.md'
        self.assertTrue(common.is_file())
        self.assertIn('Shared personal defaults', common.read_text())

    def test_skill_parity_across_agents(self):
        codex_skills = {p.name for p in (ROOT / 'codex/skills').iterdir() if (p / 'SKILL.md').is_file()}
        agy_skills = {p.name for p in (ROOT / 'antigravity/skills').iterdir() if (p / 'SKILL.md').is_file()}
        self.assertEqual(11, len(codex_skills))
        self.assertEqual(codex_skills, agy_skills)

    def test_plugin_parity_across_agents(self):
        claude_plugins = {p.name for p in (ROOT / 'claude/plugins').iterdir() if p.is_dir()}
        agy_plugins = {p.name for p in (ROOT / 'antigravity/plugins').iterdir() if p.is_dir()}
        self.assertEqual({'android-kit', 'ios-kit', 'pr-review'}, agy_plugins)
        self.assertEqual(claude_plugins, agy_plugins)

    def test_antigravity_home_symlinks(self):
        common_link = ROOT / 'antigravity/home/guidance/common.md'
        self.assertTrue(common_link.is_symlink())
        self.assertEqual(common_link.resolve(), (ROOT / 'shared/guidance/common.md').resolve())

        gemini_link = ROOT / 'antigravity/home/GEMINI.md'
        self.assertTrue(gemini_link.is_symlink())
        self.assertEqual(gemini_link.resolve(), (ROOT / 'antigravity/home/AGENTS.md').resolve())


if __name__ == '__main__':
    unittest.main()
