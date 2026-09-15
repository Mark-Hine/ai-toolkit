"""Behavioral checks for the advisory guards; no tested shell command is executed."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


GUARD = Path(__file__).resolve().parents[1] / 'hooks' / 'guard.py'
spec = importlib.util.spec_from_file_location('toolkit_guard', GUARD)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardTests(unittest.TestCase):
    def shell(self, command, role=''):
        return guard.check({'tool_name': 'exec_command', 'tool_input': {'cmd': command}}, role)

    def test_destructive_git_with_ordinary_separators(self):
        for command in ('git reset --hard', 'git checkout -- .', 'git restore .', 'git clean -fd'):
            for suffix in ('', '; git status', '&&git status', '\ngit status', '| cat'):
                with self.subTest(command=command, suffix=suffix):
                    self.assertIsNotNone(self.shell(command + suffix))

    def test_destructive_git_in_later_or_nested_commands(self):
        for command in ('git status;git reset --hard', '(git reset --hard)',
                        "sh -c 'git reset --hard; git status'",
                        'git -C /tmp/example -c color.ui=false reset --hard'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command))

    def test_protected_pushes(self):
        for ref in ('main', 'master', 'develop', 'release/1.0', 'HEAD:main',
                    'HEAD:refs/heads/main', '+HEAD:feature/example'):
            with self.subTest(ref=ref):
                self.assertIsNotNone(self.shell('git push origin ' + ref))
        for command in ('git push', 'git push origin', 'git push --all origin',
                        'git push origin feature/a --force-with-lease',
                        'git push origin feature/a -f', 'git push --mirror origin'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command))

    def test_safe_git_and_feature_pushes(self):
        for command in ('git status', 'git diff --stat', 'git reset --soft HEAD~1',
                        'git push origin HEAD:feature/example',
                        'git push origin feature/example && git status',
                        'git push origin feature/example; git status',
                        'git push origin feature/example\ngit status'):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command))

    def test_timeout_wrappers(self):
        for command in ('timeout 30 ./gradlew test', 'sudo timeout 30 ./gradlew test',
                        "sh -c 'timeout 30 ./gradlew test'"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command))

    def test_specialists_can_read_required_files(self):
        for role in ('android-researcher', 'android-verifier'):
            for command in ('cat AGENTS.md', 'cat app/build.gradle.kts gradle/libs.versions.toml',
                            'cat ~/.agents/skills/android-standards/references/testing.md',
                            "cat 'journeys/login screen.xml'", 'ls -la journeys',
                            'rg --files app', 'rg -n targetSdk app/build.gradle.kts',
                            "sed -n '1,200p' AGENTS.md"):
                with self.subTest(role=role, command=command):
                    self.assertIsNone(self.shell(command, role))

    def test_specialist_read_commands_cannot_execute_or_write(self):
        for role in ('android-researcher', 'android-verifier'):
            for command in ('rg --pre ./rewrite.sh query app',
                            'rg --pre=./rewrite.sh query app',
                            'rg --hostname-bin=./rewrite.sh query app',
                            "sed -i '' '1p' AGENTS.md", "sed -n 'w output.txt' AGENTS.md",
                            "sed -n '1p' AGENTS.md -e 'w output.txt'",
                            'cat AGENTS.md > overwritten.txt',
                            'cat AGENTS.md; touch source.kt', 'cat $(touch source.kt)',
                            'python3 edit.py'):
                with self.subTest(role=role, command=command):
                    self.assertIsNotNone(self.shell(command, role))

    def test_researcher_documentation_queries(self):
        for command in ('android docs search Compose', 'android docs fetch kb://compose',
                        'android sdk list'):
            self.assertIsNone(self.shell(command, 'android-researcher'))
        self.assertIsNotNone(self.shell('./gradlew test', 'android-researcher'))

    def test_verifier_build_and_test_evidence(self):
        for command in ('./gradlew :app:compileDebugKotlin', './gradlew assembleDebug',
                        './gradlew :core:ui:testDebugUnitTest --tests example.SomeTest',
                        './gradlew :test --console=plain --offline',
                        './gradlew -q :app:assembleDebug :app:testDebugUnitTest --console plain',
                        './gradlew :app:connectedDebugAndroidTest --no-daemon --stacktrace'):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command, 'android-verifier'))

    def test_verifier_rejects_mutating_tasks_and_init_scripts(self):
        for command in ('./gradlew test clean', './gradlew test -I edit.gradle',
                        './gradlew test --init-script=edit.gradle', './gradlew installDebug',
                        './gradlew test --tests', './gradlew test --tests --init-script=edit.gradle',
                        './gradlew --offline', './gradlew test --console unsupported'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command, 'android-verifier'))

    def test_verifier_device_evidence(self):
        for command in ('adb logcat -d -s AndroidRuntime:E',
                        'adb -s emulator-5554 logcat -d -s AndroidRuntime:E',
                        'adb shell input tap 10 20', 'android layout --diff',
                        'android screen capture -o /tmp/journey.png', 'adb devices'):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command, 'android-verifier'))

    def test_verifier_logcat_cannot_write_workspace_files(self):
        for prefix in ('adb logcat ', 'adb -s emulator-5554 logcat '):
            for flag in ('-f source.xml', '-fsource.xml', '--file source.xml', '--file=source.xml',
                         '--output=source.xml'):
                with self.subTest(prefix=prefix, flag=flag):
                    self.assertIsNotNone(self.shell(prefix + flag, 'android-verifier'))

    def test_protected_patch_operations(self):
        for operation in ('Add File', 'Update File', 'Delete File', 'Move to'):
            for path in ('.env', '.env.local', 'local.properties', 'google-services.json',
                         'signing/private.pem', 'app/libs/vendor.aar',
                         'gradle/wrapper/gradle-wrapper.jar',
                         'app/src/main/res/xml/network_security_config.xml'):
                patch = '*** Begin Patch\n*** ' + operation + ': ' + path + '\n*** End Patch'
                for tool_input in (patch, {'patch': patch}):
                    with self.subTest(operation=operation, path=path, tool_input=tool_input):
                        self.assertIsNotNone(guard.check({'tool_name': 'apply_patch', 'tool_input': tool_input}))

    def test_patch_role_boundaries(self):
        event = {'tool_name': 'apply_patch', 'tool_input':
                 '*** Begin Patch\n*** Add File: app/src/main/Main.kt\n+package app\n*** End Patch'}
        self.assertIsNone(guard.check(event))
        for role in ('android-researcher', 'android-reviewer', 'android-verifier'):
            self.assertIsNotNone(guard.check(event, role))

    def test_hook_wire_response(self):
        denied = subprocess.run([sys.executable, str(GUARD)], text=True, capture_output=True,
                                input=json.dumps({'tool_name': 'exec_command',
                                                  'tool_input': {'cmd': 'git reset --hard; git status'}}),
                                check=True)
        output = json.loads(denied.stdout)['hookSpecificOutput']
        self.assertEqual('PreToolUse', output['hookEventName'])
        self.assertEqual('deny', output['permissionDecision'])
        allowed = subprocess.run([sys.executable, str(GUARD)], text=True, capture_output=True,
                                 input=json.dumps({'tool_name': 'exec_command',
                                                   'tool_input': {'cmd': 'git status'}}), check=True)
        self.assertEqual('', allowed.stdout)


if __name__ == '__main__':
    unittest.main()
