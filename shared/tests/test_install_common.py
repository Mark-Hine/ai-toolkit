"""Tests for the install helpers shared by the Codex and Antigravity installers."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import install_common  # noqa: E402

START, END = install_common.MARKERS


class Quiet(install_common.Installer):
    def say(self, verb, path):
        pass


class MergedGuidanceTests(unittest.TestCase):
    def test_appends_to_existing_text(self):
        self.assertEqual(install_common.merged_guidance('Mine\n', 'Toolkit'), f'Mine\n\n{START}\nToolkit\n{END}\n')

    def test_replaces_the_managed_block_only(self):
        existing = f'Before\n{START}\nold\n{END}\nAfter\n'
        self.assertEqual(install_common.merged_guidance(existing, 'new'), f'Before\n{START}\nnew\n{END}\nAfter\n')

    def test_malformed_markers_fail(self):
        for existing in (f'{END}\n{START}\n', f'{START}\n{START}\n{END}\n', f'{START}\n'):
            with self.assertRaises(ValueError, msg=existing):
                install_common.merged_guidance(existing, 'x')


class InstallerTests(unittest.TestCase):
    def test_write_is_atomic_private_and_backed_up(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            target = home / 'AGENTS.md'
            target.write_text('old')
            installer = Quiet(home)
            installer.write(target, 'new')
            self.assertEqual(target.read_text(), 'new')
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            manifest = json.loads((installer.backup_root / 'manifest.json').read_text())
            self.assertEqual(manifest[0]['original'], str(target))
            self.assertEqual(Path(manifest[0]['backup']).read_text(), 'old')
            installer.write(target, 'new')
            self.assertEqual(len(installer.backups), 1)

    def test_link_moves_a_real_directory_aside(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            (home / 'guidance/android').mkdir(parents=True)
            (home / 'guidance/android/mine.md').write_text('keep')
            source = home / 'source'
            source.mkdir()
            installer = Quiet(home)
            installer.link(source, home / 'guidance/android')
            self.assertTrue((home / 'guidance/android').is_symlink())
            self.assertEqual((installer.backup_root / 'displaced-android/mine.md').read_text(), 'keep')

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / 'config'
            installer = install_common.Installer(home, dry_run=True)
            with contextlib.redirect_stdout(io.StringIO()) as out:
                installer.write(home / 'AGENTS.md', 'x')
                installer.link_shared_guidance()
                installer.create_machine_file(install_common.REPO / 'codex/home/machine.md.example')
            self.assertFalse(home.exists())
            self.assertIn('Would write', out.getvalue())
            self.assertIn('Would link', out.getvalue())

    def test_shared_guidance_links_resolve(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            Quiet(home).link_shared_guidance()
            for installed, source in install_common.SHARED_GUIDANCE.items():
                self.assertEqual((home / 'guidance' / installed).resolve(), install_common.REPO / 'shared/guidance' / source)

    def test_machine_file_is_created_once(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            example = home / 'example.md'
            example.write_text('template')
            installer = Quiet(home)
            installer.create_machine_file(example)
            (home / 'machine.md').write_text('mine')
            installer.create_machine_file(example)
            self.assertEqual((home / 'machine.md').read_text(), 'mine')

    def test_remove_backs_up_and_notes(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            stale = home / 'plugins.json'
            stale.write_text('{}')
            installer = Quiet(home)
            installer.remove(stale, 'legacy')
            self.assertFalse(stale.exists())
            self.assertEqual(len(installer.backups), 1)
            self.assertIn('legacy', installer.notes[0])


if __name__ == '__main__':
    unittest.main()
