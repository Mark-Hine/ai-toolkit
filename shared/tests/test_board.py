"""Tests for the design-kit iterate board builder. Rendering is mocked, so no browser is needed."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('board', ROOT / 'claude/plugins/design-kit/skills/iterate/scripts/board.py')
board = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(board)

SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10" fill="#00563f"/></svg>'


class BoardTest(unittest.TestCase):
    def run_board(self, *extra):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for name in ('A', 'B', 'C', 'current'):
            (root / f'{name}.svg').write_text(SVG)
        out = root / 'out'
        with mock.patch.object(board, 'render', return_value='mocked') as render:
            board.main(['--out', str(out), '--before', str(root / 'current.svg'), '--seed', '3', *extra,
                        str(root / 'A.svg'), str(root / 'B.svg'), str(root / 'C.svg')])
        return out, render

    def test_writes_reversed_variants_strips_and_board(self):
        out, render = self.run_board()
        for stem in ('before', 'A', 'B', 'C'):
            self.assertIn('#FFFFFF', (out / f'{stem}-reversed.svg').read_text())
            self.assertTrue((out / f'strip-{stem}.html').exists())
        self.assertTrue((out / 'board.html').exists())
        self.assertFalse(list(out.glob('sheet-*')), 'full sheets wait for the pick')
        self.assertEqual(render.call_count, 4, 'one strip render per mark, no board render by default')

    def test_sheets_only_for_requested_labels(self):
        out, _ = self.run_board('--sheets', 'B')
        self.assertEqual(sorted(p.name for p in out.glob('sheet-*.html')), ['sheet-B.html'])

    def test_board_keeps_current_first_and_shuffles_options_blind(self):
        out, _ = self.run_board()
        text = (out / 'board.html').read_text()
        self.assertLess(text.index('<th>Current</th>'), text.index('<th>Option'))
        self.assertNotIn('rank', text.lower().replace('no ranking', ''))

    def test_render_reports_unverified_when_turned_off(self):
        self.assertTrue(board.render(Path('x.html'), Path('x.png'), (10, 10), True).startswith('Unverified'))


if __name__ == '__main__':
    unittest.main()
