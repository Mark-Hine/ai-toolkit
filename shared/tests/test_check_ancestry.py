"""Verdicts of the pr-review commit-ancestry check (protocol.md §19), run against a scratch repository."""
import contextlib
import importlib.util
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'check_ancestry', REPO_ROOT / 'claude/plugins/pr-review/skills/pr-review/scripts/check_ancestry.py')
check_ancestry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_ancestry)

ENV = dict(os.environ, GIT_AUTHOR_NAME='Test', GIT_AUTHOR_EMAIL='test@example.com',
           GIT_COMMITTER_NAME='Test', GIT_COMMITTER_EMAIL='test@example.com', GIT_CONFIG_GLOBAL=os.devnull)


class AncestryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.git('init', '-q', '-b', 'main')
        self.base = self.commit('a.txt', 'base')
        self.git('checkout', '-q', '-b', 'side')
        self.side = self.commit('b.txt', 'side work')
        self.git('checkout', '-q', 'main')
        self.head = self.commit('a.txt', 'change a')
        self.git('checkout', '-q', '-b', 'doomed')
        self.orphan = self.commit('c.txt', 'rewritten away')
        self.git('checkout', '-q', 'main')
        self.git('branch', '-q', '-D', 'doomed')

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        out = subprocess.run(['git', '-c', 'commit.gpgsign=false', *args], cwd=self.repo, env=ENV,
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()

    def commit(self, name, message):
        (self.repo / name).write_text(message + '\n')
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)
        return self.git('rev-parse', 'HEAD')

    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = check_ancestry.main(['--repo', str(self.repo), *args])
        return code, out.getvalue()

    def test_each_verdict(self):
        missing = '0a1b2c3d4e'
        shas = [self.base[:8], self.side[:8], self.orphan[:8], missing]
        verdicts = dict(check_ancestry.check(str(self.repo), 'main', shas))
        self.assertEqual(verdicts, {self.base[:8]: 'ok', self.side[:8]: 'off-branch',
                                    self.orphan[:8]: 'orphaned', missing: 'missing'})

    def test_exit_status(self):
        self.assertEqual(self.run_main('--ref', 'main', self.base[:8], self.head[:8])[0], 0)
        self.assertEqual(self.run_main('--ref', 'main', self.side[:8])[0], 1)
        self.assertEqual(self.run_main('--ref', 'no-such-ref', self.base[:8])[0], 2)
        self.assertEqual(self.run_main('--ref', 'main', 'not-a-sha')[0], 2)

    def test_file_scan_skips_fenced_blocks(self):
        doc = self.repo / 'review.md'
        doc.write_text('Fixed in `%s`.\n\n```\nold `%s`\n```\n' % (self.base[:9], self.orphan[:9]))
        code, out = self.run_main('--ref', 'main', '--file', str(doc))
        self.assertEqual(code, 0)
        self.assertIn(self.base[:9], out)
        self.assertNotIn(self.orphan[:9], out)


if __name__ == '__main__':
    unittest.main()
