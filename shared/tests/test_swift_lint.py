"""Exercise edit detection and opt-in linting of the shared Swift lint hook without Xcode or linters."""
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

    def test_antigravity_target_file_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'View.swift'
            source.touch()
            event = {'cwd': temp, 'toolCall': {'name': 'write_to_file', 'args': {'TargetFile': str(source)}}}
            self.assertEqual(lint.changed_swift_files(event), [source.resolve()])

    def test_lint_is_opt_in_and_does_not_fix_files(self):
        with tempfile.TemporaryDirectory(prefix='swift lint ') as temp:
            root = Path(temp)
            source = root / 'App.swift'
            source.write_text('let value = 1\n')
            event = {'tool_input': {'file_path': str(source)}}

            def run(command, **kwargs):
                if command[0] == 'git':
                    return subprocess.CompletedProcess(command, 0, temp + '\n', '')
                self.assertEqual(Path(kwargs['cwd']).resolve(), root.resolve())
                self.assertNotIn('--fix', command)
                self.assertNotIn('--autocorrect', command)
                self.assertEqual(command[-1], str(source.resolve()))
                self.assertIn(str((root / ('.swiftformat' if 'swiftformat' in command[0] else '.swiftlint.yml')).resolve()), command)
                return subprocess.CompletedProcess(command, 1, 'A lint finding', '')
            with patch.object(lint.subprocess, 'run', side_effect=run) as called, \
                    patch.object(lint.shutil, 'which', side_effect=lambda tool: '/bin/' + tool):
                self.assertEqual(lint.findings(event), ([], []))
                self.assertEqual(called.call_count, 1)
                (root / '.swiftformat').touch()
                (root / '.swiftlint.yml').touch()
                errors, warnings = lint.findings(event)
                self.assertEqual(len(errors), 2)
                self.assertEqual(warnings, [])
                self.assertEqual(source.read_text(), 'let value = 1\n')
            with patch.object(lint.subprocess, 'run', side_effect=run) as called, \
                    patch.object(lint.shutil, 'which', return_value=None):
                self.assertEqual(lint.findings(event), ([], []))
                self.assertEqual(called.call_count, 1)

    def test_nearest_config_wins_over_root_config(self):
        with tempfile.TemporaryDirectory(prefix='swift lint ') as temp:
            root = Path(temp)
            module = root / 'Modules/Feature'
            module.mkdir(parents=True)
            source = module / 'View.swift'
            source.write_text('let value = 1\n')
            (root / '.swiftlint.yml').touch()
            (module / '.swiftlint.yml').touch()
            seen = []

            def run(command, **kwargs):
                if command[0] == 'git':
                    return subprocess.CompletedProcess(command, 0, temp + '\n', '')
                seen.append((command, kwargs['cwd']))
                return subprocess.CompletedProcess(command, 0, '', '')
            with patch.object(lint.subprocess, 'run', side_effect=run), \
                    patch.object(lint.shutil, 'which', side_effect=lambda tool: '/bin/' + tool if tool == 'swiftlint' else None):
                self.assertEqual(lint.findings({'tool_input': {'file_path': str(source)}}), ([], []))
            self.assertEqual(1, len(seen))
            self.assertIn(str((module / '.swiftlint.yml').resolve()), seen[0][0])
            self.assertEqual(module.resolve(), Path(seen[0][1]).resolve())

    def test_warnings_are_context_and_errors_block(self):
        errors, warnings = lint.classify('A.swift:1:1: warning: line_length\nA.swift:2:1: error: force_cast')
        self.assertEqual(['A.swift:2:1: error: force_cast'], errors)
        self.assertEqual(['A.swift:1:1: warning: line_length'], warnings)
        only_warning = json.loads(lint.render('claude', [], ['w']))
        self.assertNotIn('decision', only_warning)
        self.assertIn('w', only_warning['hookSpecificOutput']['additionalContext'])
        blocked = json.loads(lint.render('claude', ['e'], ['w']))
        self.assertEqual('block', blocked['decision'])
        self.assertEqual('', lint.render('codex', [], []))
        self.assertEqual({}, json.loads(lint.render('antigravity', ['e'], [])))

    def test_non_swift_or_deleted_file_runs_no_commands(self):
        with patch.object(lint.subprocess, 'run') as called:
            self.assertEqual(lint.findings({'tool_input': {'file_path': 'deleted.swift'}}), ([], []))
            self.assertEqual(lint.findings({'tool_input': {'file_path': 'README.md'}}), ([], []))
            called.assert_not_called()

    def test_cli_emits_post_tool_feedback_on_bad_payload(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], input='invalid json',
                                text=True, capture_output=True, check=True)
        output = json.loads(result.stdout)['hookSpecificOutput']
        self.assertEqual(output['hookEventName'], 'PostToolUse')
        self.assertIn('could not inspect', output['additionalContext'])


if __name__ == '__main__':
    unittest.main()
