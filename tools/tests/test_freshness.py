"""The freshness job grades stamps by age and rejects malformed ones."""
import importlib.util
import unittest
from datetime import date
from pathlib import Path
import tempfile

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('freshness', REPO / 'tools/freshness.py')
freshness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freshness)
CONFIG = {'warn_days': 90, 'fail_days': 180}


def fixture(tmp, name, head):
    path = Path(tmp) / name
    path.write_text(head + '\n# Doc\n\nBody.\n')
    return path


class FreshnessTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        freshness.ROOT = Path(self.tmp)

    def tearDown(self):
        freshness.ROOT = REPO

    def status(self, head, today='2026-09-29'):
        return freshness.assess(fixture(self.tmp, 'a.md', head), date.fromisoformat(today), CONFIG)['status']

    def test_ages(self):
        head = '---\nverified: 2026-09-29\nsources:\n  - https://example.org/a\n---'
        self.assertEqual('ok', self.status(head, '2026-09-29'))
        self.assertEqual('ok', self.status(head, '2026-12-27'))   # 89 days
        self.assertEqual('warn', self.status(head, '2026-12-28'))  # 90 days
        self.assertEqual('warn', self.status(head, '2027-03-27'))  # 179 days
        self.assertEqual('error', self.status(head, '2027-03-28'))  # 180 days

    def test_missing_future_and_bad_sources(self):
        self.assertEqual('error', self.status('---\nsources: house\n---'))
        self.assertEqual('error', self.status('---\nverified: 2027-01-01\nsources: house\n---'))
        self.assertEqual('error', self.status('---\nverified: 2026-09-29\nsources:\n  - ftp://x\n---'))
        self.assertEqual('error', self.status('---\nverified: 2026-09-29\n---'))
        self.assertEqual('error', self.status('no frontmatter'))

    def test_inline_and_house_are_accepted(self):
        self.assertEqual('ok', self.status('---\nverified: 2026-09-29\nsources: inline\n---'))
        self.assertEqual('ok', self.status('---\nverified: 2026-09-29\nsources: house\n---'))

    def test_every_canonical_file_in_the_repo_is_stamped_today(self):
        freshness.ROOT = REPO
        import tomllib
        config = tomllib.loads((REPO / 'tools/freshness.toml').read_text())
        rows = [freshness.assess(p, date(2026, 9, 29), config) for p in freshness.in_scope(config)]
        self.assertTrue(rows)
        self.assertEqual([], [r for r in rows if r['status'] == 'error'], [r for r in rows if r['status'] == 'error'])


if __name__ == '__main__':
    unittest.main()
