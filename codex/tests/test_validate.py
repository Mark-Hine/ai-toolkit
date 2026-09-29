"""The Codex validator rejects the mistakes it exists to catch."""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('codex_validate', REPO_ROOT / 'codex/scripts/validate.py')
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


class ValidateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.codex = self.tmp / 'codex'
        shutil.copytree(REPO_ROOT / 'codex', self.codex, ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(REPO_ROOT / 'claude', self.tmp / 'claude', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(REPO_ROOT / 'shared', self.tmp / 'shared')

    def errors(self):
        return validate.main(self.codex, self.tmp)

    def rewrite(self, rel, old, new):
        path = self.codex / rel
        text = path.read_text()
        self.assertIn(old, text, f'{rel} lacks {old!r}')
        path.write_text(text.replace(old, new, 1))

    def test_clean_tree_passes(self):
        self.assertEqual([], self.errors())

    def test_agent_name_must_match_filename(self):
        self.rewrite('agents/ui-reviewer.toml', 'name = "ui-reviewer"', 'name = "ui-review"')
        self.assertTrue(any('must equal the file stem' in e for e in self.errors()))

    def test_agent_model_cannot_inherit(self):
        self.rewrite('agents/ios-researcher.toml', 'model = "', 'model = "inherit" # "')
        self.assertTrue(any('not inherit' in e for e in self.errors()))

    def test_reviewer_sandbox_must_be_read_only(self):
        self.rewrite('agents/android-reviewer.toml', 'sandbox_mode = "read-only"', 'sandbox_mode = "workspace-write"')
        self.assertTrue(any('sandbox_mode must be read-only' in e for e in self.errors()))

    def test_manual_skill_needs_openai_policy(self):
        (self.codex / 'skills/android-run-app/agents/openai.yaml').unlink()
        self.assertTrue(any('allow_implicit_invocation' in e for e in self.errors()))

    def test_bad_rules_line_is_rejected(self):
        with (self.codex / 'home/toolkit.rules').open('a') as handle:
            handle.write('prefix_rule(pattern = [], decision = "maybe")\n')
        problems = self.errors()
        self.assertTrue(any('non-empty list' in e for e in problems))
        self.assertTrue(any('decision must be' in e for e in problems))

    def test_dangling_guidance_reference(self):
        with (self.codex / 'home/AGENTS.md').open('a') as handle:
            handle.write('\nSee guidance/android/missing.md.\n')
        self.assertTrue(any('guidance/android/missing.md' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
