"""The Antigravity validator rejects the layout mistakes it exists to catch."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('agy_validate', REPO / 'antigravity/scripts/validate.py')
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)


class ValidateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        for layer in ('antigravity', 'claude', 'codex', 'shared'):
            shutil.copytree(REPO / layer, self.tmp / layer, ignore=shutil.ignore_patterns('__pycache__'), symlinks=True)
        validate.ROOT = self.tmp / 'antigravity'
        validate.REPO = self.tmp

    def tearDown(self):
        validate.ROOT = REPO / 'antigravity'
        validate.REPO = REPO

    def errors(self):
        errors = []
        for check in (validate.check_plugins, validate.check_agents, validate.check_hooks, validate.check_home, validate.check_leaks):
            check(errors)
        return errors

    def agent(self, rel='plugins/android-kit/agents/android-verifier.md'):
        return self.tmp / 'antigravity' / rel

    def rewrite(self, path, old, new):
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def test_clean_tree_passes(self):
        self.assertEqual([], self.errors())

    def test_write_tool_on_a_specialist(self):
        self.rewrite(self.agent(), 'grep_search, run_command]', 'grep_search, run_command, write_to_file]')
        self.assertTrue(any('never get write tools' in e for e in self.errors()))

    def test_inherit_model_and_unknown_key(self):
        self.rewrite(self.agent(), 'model: flash', 'model: inherit\nenable_write_tools: true')
        problems = self.errors()
        self.assertTrue(any('model must be' in e for e in problems))
        self.assertTrue(any('undocumented frontmatter keys' in e for e in problems))

    def test_unknown_tool_name(self):
        self.rewrite(self.agent(), 'view_file,', 'view_files,')
        self.assertTrue(any('unknown tools' in e for e in self.errors()))

    def test_hook_path_must_stay_inside_the_plugin(self):
        hooks = self.tmp / 'antigravity/plugins/android-kit/hooks.json'
        self.rewrite(hooks, 'python3 hooks/guard.py --agent antigravity', 'python3 ../../hooks/guard.py --agent antigravity')
        self.assertTrue(any('inside the plugin' in e for e in self.errors()))

    def test_unknown_matcher_tool(self):
        hooks = self.tmp / 'antigravity/plugins/android-kit/hooks.json'
        self.rewrite(hooks, 'run_command|write_to_file', 'run_cmd|write_to_file')
        self.assertTrue(any('unknown tools' in e for e in self.errors()))

    def test_stray_home_file_and_undocumented_plugin_key(self):
        (self.tmp / 'antigravity/home/plugins.json').write_text('{}')
        manifest = self.tmp / 'antigravity/plugins/pr-review/plugin.json'
        data = json.loads(manifest.read_text()); data['author'] = 'x'
        manifest.write_text(json.dumps(data))
        problems = self.errors()
        self.assertTrue(any('plugins.json' in e for e in problems))
        self.assertTrue(any('undocumented keys' in e for e in problems))


if __name__ == '__main__':
    unittest.main()
