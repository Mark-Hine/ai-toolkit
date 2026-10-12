"""The release job tags each new plugin version once, with notes since that plugin's previous tag."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('release_tags', REPO / 'tools/release_tags.py')
release_tags = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_tags)


def git(root, *args):
    subprocess.run(['git', *args], cwd=root, check=True, capture_output=True)


def set_version(root, plugin, version):
    manifest = root / 'claude/plugins' / plugin / '.claude-plugin/plugin.json'
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({'name': plugin, 'version': version}))


def commit(root, message):
    git(root, 'add', '-A')
    git(root, '-c', 'user.name=t', '-c', 'user.email=t@example.com', 'commit', '-q', '-m', message)


class ReleaseTagTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        git(self.root, 'init', '-q', '-b', 'main')
        set_version(self.root, 'web-kit', '1.0.0')
        set_version(self.root, 'toolkit', '2.0.0')
        commit(self.root, 'feat: first plugins')

    def tearDown(self):
        self.temp.cleanup()

    def test_untagged_versions_get_a_first_release(self):
        releases = release_tags.plan(self.root)
        self.assertEqual([r[0] for r in releases], ['toolkit--v2.0.0', 'web-kit--v1.0.0'])
        self.assertEqual(releases[1][1], 'web-kit 1.0.0')
        self.assertIn('First tagged release', releases[1][2])

    def test_existing_tags_are_skipped_and_notes_cover_only_that_plugin(self):
        git(self.root, 'tag', 'web-kit--v1.0.0')
        git(self.root, 'tag', 'toolkit--v2.0.0')
        self.assertEqual(release_tags.plan(self.root), [])
        (self.root / 'claude/plugins/web-kit/SKILL.md').write_text('new')
        set_version(self.root, 'web-kit', '1.1.0')
        commit(self.root, 'feat(web-kit): add a skill')
        (self.root / 'claude/plugins/toolkit/README.md').write_text('docs')
        commit(self.root, 'docs(toolkit): unrelated change')
        releases = release_tags.plan(self.root)
        self.assertEqual([r[0] for r in releases], ['web-kit--v1.1.0'])
        self.assertIn('Changes since `web-kit--v1.0.0`', releases[0][2])
        self.assertIn('feat(web-kit): add a skill', releases[0][2])
        self.assertNotIn('unrelated change', releases[0][2])

    def test_previous_tag_is_the_newest_lower_version(self):
        tags = ['web-kit--v1.0.0', 'web-kit--v1.10.0', 'web-kit--v1.2.0', 'web-kit--vbad', 'toolkit--v9.0.0']
        self.assertEqual(release_tags.previous_tag('web-kit', '1.11.0', tags), 'web-kit--v1.10.0')
        self.assertEqual(release_tags.previous_tag('web-kit', '1.0.0', tags), None)

    def test_repository_plugins_have_valid_versions(self):
        for name, version in release_tags.plugins(REPO):
            self.assertRegex(release_tags.tag_name(name, version), r'^[a-z0-9-]+--v\d+\.\d+\.\d+$')


if __name__ == '__main__':
    unittest.main()
