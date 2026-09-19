"""Exercise edit detection and opt-in linting for Antigravity."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'hooks/swift_lint.py'
spec = importlib.util.spec_from_file_location('swift_lint', SCRIPT)
lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)


class SwiftLintTests(unittest.TestCase):
    def test_patch_paths_include_add_update_and_move_but_not_deleted_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ('New.swift', 'Updated.swift', 'Moved.swift', 'Other.txt'):
                (root / name).touch()
            source = ('*** Add File: New.swift\n*** Update File: Updated.swift\n'
                      '*** Update File: Old.swift\n*** Move to: Moved.swift\n'
                      '*** Delete File: Deleted.swift\n*** Add File: Other.txt\n')
            expected = sorted((root / name).resolve() for name in ('New.swift', 'Updated.swift', 'Moved.swift'))
            for args in (source, {'command': source}, {'patch': source}):
                self.assertEqual(lint.changed_swift_files({'cwd': temp, 'tool_input': args}), expected)

    def test_antigravity_target_file_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            swift_file = root / 'Screen.swift'
            swift_file.touch()
            event = {
                'cwd': temp,
                'toolCall': {
                    'name': 'write_to_file',
                    'args': {'TargetFile': str(swift_file)}
                }
            }
            self.assertEqual(lint.changed_swift_files(event), [swift_file.resolve()])

    def test_lint_is_opt_in_and_does_not_fix_files(self):
        with tempfile.TemporaryDirectory(prefix='swift lint ') as temp:
            root = Path(temp)
            source = root / 'App.swift'
            source.write_text('let value = 1\n')
            event = {'toolCall': {'name': 'write_to_file', 'args': {'TargetFile': str(source)}}}

            def run(command, **kwargs):
                if command[0] == 'git':
                    return subprocess.CompletedProcess(command, 0, temp + '\n', '')
                self.assertEqual(kwargs['cwd'], root)
                self.assertNotIn('--fix', command)
                self.assertNotIn('--autocorrect', command)
                self.assertEqual(command[-1], str(source.resolve()))
                self.assertIn(str(root / ('.swiftformat' if 'swiftformat' in command[0] else '.swiftlint.yml')), command)
                return subprocess.CompletedProcess(command, 1, 'A lint finding', '')

            with patch.object(lint.subprocess, 'run', side_effect=run) as called, patch.object(lint.shutil, 'which', side_effect=lambda tool: '/bin/' + tool):
                self.assertEqual(lint.findings(event), [])
                self.assertEqual(called.call_count, 1)
                (root / '.swiftformat').touch()
                (root / '.swiftlint.yml').touch()
                self.assertEqual(len(lint.findings(event)), 2)
                self.assertEqual(source.read_text(), 'let value = 1\n')

            with patch.object(lint.subprocess, 'run', side_effect=run) as called, patch.object(lint.shutil, 'which', return_value=None):
                self.assertEqual(lint.findings(event), [])
                self.assertEqual(called.call_count, 1)

    def test_non_swift_or_deleted_file_runs_no_commands(self):
        with patch.object(lint.subprocess, 'run') as called:
            self.assertEqual(lint.findings({'toolCall': {'name': 'write_to_file', 'args': {'TargetFile': 'deleted.swift'}}}), [])
            self.assertEqual(lint.findings({'toolCall': {'name': 'write_to_file', 'args': {'TargetFile': 'README.md'}}}), [])
            called.assert_not_called()

    def test_cli_emits_empty_object_on_antigravity(self):
        result = subprocess.run([sys.executable, str(SCRIPT)],
                                input=json.dumps({'toolCall': {'name': 'write_to_file', 'args': {'TargetFile': 'README.md'}}}),
                                text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), {})


if __name__ == '__main__':
    unittest.main()
