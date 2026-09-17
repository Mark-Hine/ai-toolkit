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

    def test_ios_research_queries(self):
        for command in ('xcodebuild -version', 'xcodebuild -showsdks',
                        'xcodebuild -workspace App.xcworkspace -scheme App -showBuildSettings',
                        'xcodebuild -list -project App.xcodeproj -json',
                        'xcrun xcodebuild -version', 'xcrun simctl list devices available',
                        'xcrun --show-sdk-path', 'swift --version', 'swift package describe',
                        'swift package show-dependencies', 'pod outdated'):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command, 'ios-researcher'))
        for command in ('xcodebuild build', 'xcodebuild -version build',
                        'xcodebuild -list -resolvePackageDependencies', 'swift package update',
                        'pod install', 'xcrun simctl erase all', 'xcrun simctl boot device',
                        'xcodebuild -list; touch App.swift'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command, 'ios-researcher'))

    def test_ios_verifier_evidence_commands(self):
        for command in ('xcodebuild test -workspace App.xcworkspace -scheme "App Tests" '
                        '-destination "platform=iOS Simulator,id=device" '
                        '-only-testing:AppTests/Login -resultBundlePath /tmp/tests.xcresult',
                        'xcodebuild test-without-building -scheme App',
                        'xcrun xcresulttool get test-results summary --path /tmp/tests.xcresult',
                        'xcrun simctl launch device com.example.app',
                        'xcrun simctl openurl device example://home',
                        'xcrun simctl io device screenshot /tmp/screen.png',
                        'xcrun simctl ui device content_size',
                        'xcrun simctl ui device content_size accessibility-extra-large',
                        'xcrun simctl ui device appearance dark',
                        'xcrun simctl spawn device log show --last 3m --predicate '
                        '\'processImagePath CONTAINS "App"\' --style compact',
                        'xcrun simctl listapps device', 'xcrun simctl bootstatus device -b'):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command, 'ios-verifier'))
        for command in ('xcodebuild test clean', 'xcodebuild test archive',
                        'xcodebuild test -resultBundlePath App.swift',
                        'xcodebuild test -scheme', 'xcodebuild test OTHER_SWIFT_FLAGS=-unsafe',
                        'xcrun simctl install device app.app', 'xcrun simctl erase all',
                        'xcrun simctl spawn device sh -c "touch App.swift"',
                        'xcrun simctl io device screenshot App.swift',
                        'xcrun xcresulttool export object --output-path App.swift',
                        'swift package update', 'git status'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command, 'ios-verifier'))

    def test_timeout_wrappers(self):
        for command in ('timeout 30 ./gradlew test', 'sudo timeout 30 ./gradlew test',
                        "sh -c 'timeout 30 ./gradlew test'",
                        'timeout', '/usr/bin/timeout 30 task',
                        'env FLAG=1 timeout 30 task', 'sudo -u example timeout 30 task',
                        'command timeout 30 task', 'exec timeout 30 task',
                        'true && timeout 30 task', 'true\ntimeout 30 task',
                        '(timeout 30 task)', 'if true; then timeout 30 task; fi',
                        'echo $(timeout 30 task)', 'echo "$(timeout 30 task)"',
                        'echo "`timeout 30 task`"', '/bin/zsh -lc "timeout 30 task"'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command))

    def test_timeout_in_arguments_and_comments_is_data(self):
        for command in ('echo "A bridge heartbeat timeout expires the lease"',
                        'printf "%s" "timeout 30 task"', 'rg timeout docs',
                        'cat timeout', '# timeout 30 task\necho ready',
                        "echo 'git reset --hard'", "python3 -c 'print(\"timeout example\")'"):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command))

    def test_literal_heredoc_document_content(self):
        body = "A bridge heartbeat timeout expires the lease.\ntimeout 30 task\ngit reset --hard\nAn unmatched ' quote\n"
        for header, end in (("cat > spec.md <<'SPEC'\n", 'SPEC'),
                            ('cat <<"SPEC" > spec.md\n', 'SPEC'),
                            ('cat <<\\SPEC > spec.md\n', 'SPEC'),
                            ("cat <<-'SPEC' > spec.md\n", '\tSPEC')):
            with self.subTest(header=header):
                self.assertIsNone(self.shell(header + body + end + '\n'))

    def test_heredoc_does_not_hide_surrounding_commands(self):
        document = "cat <<'SPEC' > spec.md\ntimeout is documented here\nSPEC\n"
        for command in ('timeout 30 task', 'git reset --hard', 'git push origin main'):
            for source in (command + '\n' + document, document + command,
                           "cat <<'SPEC'; " + command + '\ntext\nSPEC\n'):
                with self.subTest(source=source):
                    self.assertIsNotNone(self.shell(source))

    def test_multiple_heredocs_and_nested_shell(self):
        self.assertIsNone(self.shell("cat <<'ONE' <<'TWO'\ntimeout 1 task\nONE\ngit reset --hard\nTWO\n"))
        self.assertIsNotNone(self.shell("cat <<'ONE' <<'TWO'\ntext\nONE\ntext\nTWO\ntimeout 1 task"))
        self.assertIsNone(self.shell('sh -c "cat <<\'EOF\'\ntimeout is data\nEOF\n"'))
        self.assertIsNotNone(self.shell('sh -c "cat <<\'EOF\'\ntext\nEOF\ntimeout 1 task"'))

    def test_unquoted_heredoc_expansions_remain_checked(self):
        self.assertIsNotNone(self.shell('cat <<EOF\n$(timeout 30 task)\nEOF\n'))
        self.assertIsNotNone(self.shell('cat <<EOF\n$(git reset --hard)\nEOF\n'))

    def test_multiline_arguments_do_not_create_heredocs(self):
        self.assertIsNotNone(self.shell('echo "example\ncat <<\'EOF\'\n"\ntimeout 1 task\n# EOF'))
        self.assertIsNotNone(self.shell('echo "$(git reset --hard)"'))

    def test_unterminated_heredoc_is_not_discarded(self):
        self.assertIn('timeout 1 task', guard.shell_source("cat <<'EOF'\ntext\ntimeout 1 task"))

    def test_specialists_can_read_required_files(self):
        for role in ('android-researcher', 'android-verifier', 'ios-researcher', 'ios-verifier'):
            for command in ('cat AGENTS.md', 'cat app/build.gradle.kts gradle/libs.versions.toml',
                            'cat ~/.agents/skills/android-standards/references/testing.md',
                            "cat 'journeys/login screen.xml'", 'ls -la journeys',
                            'rg --files app', 'rg -n targetSdk app/build.gradle.kts',
                            "sed -n '1,200p' AGENTS.md"):
                with self.subTest(role=role, command=command):
                    self.assertIsNone(self.shell(command, role))

    def test_specialist_read_commands_cannot_execute_or_write(self):
        for role in ('android-researcher', 'android-verifier', 'ios-researcher', 'ios-verifier'):
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
                         'App/App.entitlements', 'ExportOptions.plist',
                         'App/Secrets.swift', 'App/secrets.plist', 'Config/Secrets.Debug.xcconfig',
                         'Podfile.lock', 'Workspace/xcshareddata/swiftpm/Package.resolved',
                         'app/src/main/res/xml/network_security_config.xml'):
                patch = '*** Begin Patch\n*** ' + operation + ': ' + path + '\n*** End Patch'
                for tool_input in (patch, {'patch': patch}):
                    with self.subTest(operation=operation, path=path, tool_input=tool_input):
                        self.assertIsNotNone(guard.check({'tool_name': 'apply_patch', 'tool_input': tool_input}))

    def test_patch_role_boundaries(self):
        event = {'tool_name': 'apply_patch', 'tool_input':
                 '*** Begin Patch\n*** Add File: app/src/main/Main.kt\n+package app\n*** End Patch'}
        self.assertIsNone(guard.check(event))
        for role in ('android-researcher', 'android-reviewer', 'android-verifier',
                     'ios-researcher', 'ios-reviewer', 'ios-verifier'):
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
