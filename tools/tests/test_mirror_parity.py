"""Normalisation and thresholds of the mirror parity check."""
import importlib.util
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('mirror_parity', REPO / 'tools/mirror_parity.py')
mp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mp)
SUBS = [{'neutral': '{PROJECT_FILE}', 'claude': ['CLAUDE.md'], 'codex': ['AGENTS.md'], 'antigravity': ['AGENTS.md']},
        {'neutral': '{INVOKE}', 'claude': ['/android-kit:'], 'codex': ['$android-'], 'antigravity': ['/android-']}]


class MirrorParityTest(unittest.TestCase):
    def test_layer_wording_normalises_to_the_same_tokens(self):
        a = mp.normalise('---\nname: x\n---\nRead `CLAUDE.md`, then run /android-kit:feature.', 'claude', SUBS)
        b = mp.normalise('---\nname: y\n---\nRead `AGENTS.md`, then run $android-feature.', 'codex', SUBS)
        c = mp.normalise('Read `AGENTS.md`, then run /android-feature.', 'antigravity', SUBS)
        self.assertEqual(a, b)
        self.assertEqual(b, c)

    def test_codex_toml_instructions_are_extracted(self):
        toml = 'name = "x"\ndescription = "d"\ndeveloper_instructions = "# Title\\n\\nBody text here."\n'
        self.assertEqual(['#', 'title', 'body', 'text', 'here.'], mp.normalise(toml, 'codex', []))

    def test_exceptions_and_expiry(self):
        config = {'threshold': 0.9}
        exc = {'exceptions': [{'path': 'a.md', 'threshold': 0.5, 'reason': 'r', 'until': '2027-01-01'}]}
        self.assertEqual((0.5, 'r'), mp.threshold_for('a.md', config, exc, date(2026, 9, 29)))
        self.assertEqual((0.9, None), mp.threshold_for('b.md', config, exc, date(2026, 9, 29)))
        threshold, note = mp.threshold_for('a.md', config, exc, date(2027, 6, 1))
        self.assertIsNone(threshold)
        self.assertIn('expired', note)


if __name__ == '__main__':
    unittest.main()
