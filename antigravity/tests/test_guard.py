"""Behavioral checks for Antigravity guards; no tested shell command is executed."""
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
        return guard.check({'toolCall': {'name': 'run_command', 'args': {'CommandLine': command}}}, role)

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

    def test_push_flags_are_scoped_to_the_push_segment(self):
        safe = ('git worktree remove --force scratch && git push origin feature/x',
                'git push origin feature/x; tool --force',
                'python3 -c "s=a+new+b"; git push origin feature/x',
                'echo +main | cat; git push origin feature/x',
                "echo 'run: git push origin main later'")
        for command in safe:
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command))
        for command in ('git push -uf origin feature/x', 'git push -fu origin feature/x',
                        'git push --force-if-includes origin feature/x',
                        'git push --force-with-lease=main origin feature/x',
                        'sudo git push origin develop', 'git -C repo push origin main',
                        'git status; git push origin +feature/x'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command))

    def test_timeout_wrappers(self):
        for command in ('timeout 10 git status', '/usr/bin/timeout 5 ./gradlew test',
                        'sudo timeout 10 git status', 'env timeout 10 git status',
                        'git status && timeout 5 ls', 'VAR=1 timeout 5 ls'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command))

    def test_protected_patch_operations(self):
        protected_paths = (
            'google-services.json', 'app/google-services.json',
            'GoogleService-Info.plist', 'ios/GoogleService-Info.plist',
            'secrets.properties', 'local.properties', '.env', '.env.production',
            'app/src/main/res/xml/network_security_config.xml',
            'release.keystore', 'app/release.jks', 'cert.p12', 'key.pem', 'deploy.key',
            'profile.mobileprovision', 'cert.cer', 'App.entitlements',
            'ExportOptions.plist', 'Podfile.lock', 'Package.resolved',
            'Secrets.swift', 'AppSecrets.plist', 'Secrets.xcconfig',
            'app/libs/custom.aar', 'app/libs/custom.jar',
            'gradle/wrapper/gradle-wrapper.jar'
        )
        for path in protected_paths:
            with self.subTest(path=path):
                self.assertIsNotNone(guard.check({
                    'toolCall': {
                        'name': 'write_to_file',
                        'args': {'TargetFile': path, 'CodeContent': 'test'}
                    }
                }))
                self.assertIsNotNone(guard.check({
                    'toolCall': {
                        'name': 'replace_file_content',
                        'args': {'TargetFile': path, 'ReplacementContent': 'test'}
                    }
                }))

    def test_patch_role_boundaries(self):
        event = {
            'toolCall': {
                'name': 'write_to_file',
                'args': {'TargetFile': 'app/src/main/Main.kt', 'CodeContent': 'package app'}
            }
        }
        self.assertIsNone(guard.check(event))
        for role in ('android-researcher', 'android-reviewer', 'android-verifier',
                     'ios-researcher', 'ios-reviewer', 'ios-verifier'):
            self.assertIsNotNone(guard.check(event, role))

    def test_antigravity_wire_response(self):
        # Denied command
        denied = subprocess.run([sys.executable, str(GUARD)], text=True, capture_output=True,
                                input=json.dumps({
                                    'toolCall': {
                                        'name': 'run_command',
                                        'args': {'CommandLine': 'git reset --hard; git status'}
                                    }
                                }), check=True)
        out = json.loads(denied.stdout)
        self.assertEqual('deny', out['decision'])
        self.assertTrue(len(out.get('reason', '')) > 0)

        # Allowed command
        allowed = subprocess.run([sys.executable, str(GUARD)], text=True, capture_output=True,
                                 input=json.dumps({
                                     'toolCall': {
                                         'name': 'run_command',
                                         'args': {'CommandLine': 'git status'}
                                     }
                                 }), check=True)
        out = json.loads(allowed.stdout)
        self.assertEqual('allow', out['decision'])

        # Denied file write
        denied_write = subprocess.run([sys.executable, str(GUARD)], text=True, capture_output=True,
                                      input=json.dumps({
                                          'toolCall': {
                                              'name': 'write_to_file',
                                              'args': {'TargetFile': 'app/release.keystore', 'CodeContent': ''}
                                          }
                                      }), check=True)
        out = json.loads(denied_write.stdout)
        self.assertEqual('deny', out['decision'])

    def test_codex_backward_compatibility(self):
        denied = subprocess.run([sys.executable, str(GUARD)], text=True, capture_output=True,
                                input=json.dumps({
                                    'tool_name': 'exec_command',
                                    'tool_input': {'cmd': 'git reset --hard'}
                                }), check=True)
        out = json.loads(denied.stdout)['hookSpecificOutput']
        self.assertEqual('PreToolUse', out['hookEventName'])
        self.assertEqual('deny', out['permissionDecision'])


if __name__ == '__main__':
    unittest.main()
