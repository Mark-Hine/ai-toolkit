"""Behavioral checks for the shared guard. No tested shell command is executed."""
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
import unittest.mock


GUARD = Path(__file__).resolve().parents[1] / 'hooks' / 'guard.py'
spec = importlib.util.spec_from_file_location('toolkit_guard', GUARD)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardTests(unittest.TestCase):
    def shell(self, command, role=''):
        return guard.check({'tool_name': 'exec_command', 'tool_input': {'cmd': command}}, role)

    def test_destructive_git_with_ordinary_separators(self):
        for command in ('git reset --hard', 'git checkout -- .', 'git checkout .', 'git checkout :/',
                        'git restore .', 'git restore --staged --worktree .', 'git clean -fd', 'git clean -xdf'):
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
        for ref in ('main', 'master', 'develop', 'release/1.0', 'HEAD:main', '"main"',
                    'HEAD:refs/heads/main', 'refs/heads/main', '+HEAD:feature/example'):
            with self.subTest(ref=ref):
                self.assertIsNotNone(self.shell('git push origin ' + ref))
        for command in ('git push', 'git push origin', 'git push --all origin',
                        'git push origin feature/a --force-with-lease',
                        'git push origin feature/a -f', 'git push --mirror origin',
                        'git push origin HEAD', 'git push -u origin @',
                        'git push origin --delete feature/old', 'git push -d origin feature/old',
                        'git push origin :feature/old', 'git push origin --tags feature/x',
                        'FOO=1 git push origin main', 'bash -c "git push origin main"',
                        'eval "git push origin main"', 'git push origin main; echo done'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command))

    def test_safe_git_and_feature_pushes(self):
        for command in ('git status', 'git diff --stat', 'git reset --soft HEAD~1',
                        'git push origin HEAD:feature/example', 'git push -u origin feat/MBS-1-slug',
                        'git restore --staged .', 'git restore -S .', 'git checkout -b feat/x',
                        'git branch --list', 'grep -n main README.md', 'git log origin/main..HEAD',
                        'git push origin feature/example && git status',
                        'git push origin feature/example; git status',
                        'git push origin feature/example\ngit status',
                        'git push origin feature/example 2>&1', 'git push -u origin feat/a:feat/a 2>&1 | tail -3',
                        'git push origin feature/example 2>/dev/null', 'git push origin feature/example > push.log'):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command))

    def test_redirects_do_not_hide_a_bad_push(self):
        for command in ('git push origin main 2>&1', 'git push 2>&1', 'git push origin 2>&1',
                        'git push origin HEAD 2>/dev/null', 'git push origin feature/x --force 2>&1',
                        'git push origin 2>x main'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command))

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

    def test_verifier_setup_commands_name_the_caller(self):
        for role in ('android-verifier', 'ios-verifier'):
            for command in ('git worktree add --detach /tmp/pr-1 abc123', 'pod install',
                            'swift package resolve', 'npm ci'):
                with self.subTest(role=role, command=command):
                    reason = self.shell(command, role)
                    self.assertIsNotNone(reason)
                    self.assertIn('prepare the checkout', reason)

    def test_timeout_wrappers(self):
        wrapper = 'timeout'
        for command in (f'{wrapper} 30 ./gradlew test', f'sudo {wrapper} 30 ./gradlew test',
                        f'time {wrapper} 5 ls', f'xargs {wrapper} 5 ls', f'xargs -n 1 {wrapper} 5 ls',
                        f'nice -n 5 {wrapper} 5 ls', f'caffeinate -t 60 {wrapper} 5 ls',
                        f'eval {wrapper} 5 ls', f'FOO=1 {wrapper} 5 ls',
                        f"sh -c '{wrapper} 30 ./gradlew test'",
                        wrapper, f'/usr/bin/{wrapper} 30 task',
                        f'env FLAG=1 {wrapper} 30 task', f'sudo -u example {wrapper} 30 task',
                        f'command {wrapper} 30 task', f'exec {wrapper} 30 task',
                        f'true && {wrapper} 30 task', f'true\n{wrapper} 30 task',
                        f'({wrapper} 30 task)', f'if true; then {wrapper} 30 task; fi',
                        f'echo $({wrapper} 30 task)', f'echo "$({wrapper} 30 task)"',
                        f'echo "`{wrapper} 30 task`"', f'/bin/zsh -lc "{wrapper} 30 task"'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command))

    def test_timeout_in_arguments_and_comments_is_data(self):
        wrapper = 'timeout'
        for command in (f'echo "A bridge heartbeat {wrapper} expires the lease"',
                        f'printf "%s" "{wrapper} 30 task"', f'rg {wrapper} docs',
                        f'cat {wrapper}', f'# {wrapper} 30 task\necho ready',
                        "echo 'git reset --hard'", f"python3 -c 'print(\"{wrapper} example\")'",
                        'adb shell am start --timeout 1000 com.x/.Main'):
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

    def test_verifier_configuration_capture_settings(self):
        for command in ('adb shell settings get system font_scale',
                        'adb -s emulator-5554 shell settings put system font_scale 2.0',
                        'adb shell settings put system font_scale 1', 'adb shell cmd uimode night',
                        'adb -s emulator-5556 shell cmd uimode night yes', 'adb shell cmd uimode night no'):
            with self.subTest(command=command):
                self.assertIsNone(self.shell(command, 'android-verifier'))
        for command in ('adb shell settings put global font_scale 2.0',
                        'adb shell settings delete system font_scale',
                        'adb shell settings put system screen_brightness 10',
                        'adb shell settings put system font_scale 2.0 extra',
                        'adb shell settings put secure font_scale 2.0',
                        'adb shell cmd uimode night auto', 'adb shell cmd package uninstall com.x'):
            with self.subTest(command=command):
                self.assertIsNotNone(self.shell(command, 'android-verifier'))
        self.assertIsNotNone(self.shell('adb shell settings put system font_scale 2.0', 'android-researcher'))

    def test_verifier_logcat_cannot_write_workspace_files(self):
        for prefix in ('adb logcat ', 'adb -s emulator-5554 logcat '):
            for flag in ('-f source.xml', '-fsource.xml', '--file source.xml', '--file=source.xml',
                         '--output=source.xml'):
                with self.subTest(prefix=prefix, flag=flag):
                    self.assertIsNotNone(self.shell(prefix + flag, 'android-verifier'))

    def test_protected_patch_operations(self):
        for operation in ('Add File', 'Update File', 'Delete File', 'Move to'):
            for path in ('.env', '.env.local', '.envrc', 'local.properties', 'keystore.properties',
                         'google-services.json', 'AuthKey_ABC123.p8', '.git/config', '.git/hooks/pre-commit',
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

    def test_env_templates_and_source_files_are_editable(self):
        for tool, key in (('Edit', 'file_path'), ('Write', 'file_path'), ('NotebookEdit', 'notebook_path'),
                          ('write_to_file', 'TargetFile'), ('multi_replace_file_content', 'TargetFile')):
            for path in ('.env.example', '.env.sample', 'app/src/main/Main.kt', 'App/Foo.swift', 'notes.ipynb'):
                with self.subTest(tool=tool, path=path):
                    event = {'tool_name': tool, 'tool_input': {key: path}}
                    if key == 'TargetFile':
                        event = {'toolCall': {'name': tool, 'args': {key: path}}}
                    self.assertIsNone(guard.check(event))

    def test_protected_paths_through_every_tool_shape(self):
        for tool, key in (('Edit', 'file_path'), ('Write', 'file_path'), ('NotebookEdit', 'notebook_path')):
            self.assertIsNotNone(guard.check({'tool_name': tool, 'tool_input': {key: 'app/release.jks'}}))
        for tool in ('write_to_file', 'replace_file_content', 'multi_replace_file_content'):
            self.assertIsNotNone(guard.check({'toolCall': {'name': tool, 'args': {'TargetFile': 'ios/Podfile.lock'}}}))

    def test_ci_definitions_ask_on_claude_and_deny_elsewhere(self):
        for path in ('.github/workflows/ci.yml', 'azure-pipelines.yml', 'ci/azure-pipelines-review.yaml'):
            event = {'tool_name': 'Edit', 'tool_input': {'file_path': path}}
            with self.subTest(path=path):
                self.assertEqual('ask', guard.evaluate(event)[0])
                self.assertIn('"ask"', guard.render('claude', guard.evaluate(event)))
                self.assertIn('"deny"', guard.render('codex', guard.evaluate(event)))
                self.assertIn('"ask"', guard.render('antigravity', guard.evaluate(event)))

    def test_role_comes_from_argv_then_agent_type(self):
        self.assertEqual('android-researcher', guard.resolve_role({}, 'android-researcher'))
        self.assertEqual('android-researcher', guard.resolve_role({'agent_type': 'android-kit:android-researcher'}))
        self.assertEqual('ios-verifier', guard.resolve_role({'agent_type': 'ios-kit:ios-verifier'}, ''))
        self.assertEqual('ui-reviewer', guard.resolve_role({'agent_type': 'ui-reviewer'}))
        self.assertEqual('', guard.resolve_role({'agent_type': 'Explore'}))
        self.assertEqual('', guard.resolve_role({'agent_type': 'general-purpose'}))
        self.assertEqual('android-verifier', guard.resolve_role({'agent_type': 'ios-kit:ios-verifier'}, 'android-verifier'))
        self.assertEqual('android-verifier', guard.resolve_role({'role': 'android-verifier'}))

    def test_role_from_agent_type_limits_a_subagent(self):
        event = {'tool_name': 'Bash', 'tool_input': {'command': './gradlew installDebug'},
                 'agent_type': 'android-kit:android-verifier'}
        self.assertIsNotNone(guard.check(event, guard.resolve_role(event)))
        event['agent_type'] = 'Explore'
        self.assertIsNone(guard.check(event, guard.resolve_role(event)))

    def test_render_per_host(self):
        self.assertEqual('', guard.render('claude', None))
        self.assertEqual('', guard.render('codex', None))
        self.assertEqual({'decision': 'ask'}, json.loads(guard.render('antigravity', None)))
        self.assertEqual({'decision': 'deny', 'reason': 'x'}, json.loads(guard.render('antigravity', ('deny', 'x'))))
        claude = json.loads(guard.render('claude', ('deny', 'x')))['hookSpecificOutput']
        self.assertEqual(('PreToolUse', 'deny', 'x'),
                         (claude['hookEventName'], claude['permissionDecision'], claude['permissionDecisionReason']))

    def test_main_denies_on_invalid_input_and_never_raises(self):
        for agent in ('claude', 'codex', 'antigravity'):
            out = io.StringIO()
            with unittest.mock.patch('sys.stdout', out):
                self.assertEqual(0, guard.main(['--agent', agent], stdin=io.StringIO('not json')))
            self.assertIn('deny', out.getvalue())
            out = io.StringIO()
            with unittest.mock.patch('sys.stdout', out):
                payload = json.dumps({'tool_name': 'Bash', 'tool_input': {'command': 'git status'}})
                guard.main(['--agent', agent], stdin=io.StringIO(payload))
            self.assertNotIn('deny', out.getvalue())
            if agent == 'antigravity':
                self.assertIn('ask', out.getvalue())

    def test_patch_role_boundaries(self):
        event = {'tool_name': 'apply_patch', 'tool_input':
                 '*** Begin Patch\n*** Add File: app/src/main/Main.kt\n+package app\n*** End Patch'}
        self.assertIsNone(guard.check(event))
        for role in ('android-researcher', 'android-reviewer', 'android-verifier',
                     'ios-researcher', 'ios-reviewer', 'ios-verifier'):
            self.assertIsNotNone(guard.check(event, role))

    def test_hook_wire_response(self):
        denied = subprocess.run([sys.executable, str(GUARD), '--agent', 'codex'], text=True, capture_output=True,
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
        antigravity = subprocess.run([sys.executable, str(GUARD), '--agent', 'antigravity'], text=True,
                                     capture_output=True, check=True,
                                     input=json.dumps({'toolCall': {'name': 'run_command', 'args': {'CommandLine': 'git status'}}}))
        self.assertEqual({'decision': 'ask'}, json.loads(antigravity.stdout))
        antigravity = subprocess.run([sys.executable, str(GUARD), '--agent', 'antigravity'], text=True,
                                     capture_output=True, check=True,
                                     input=json.dumps({'toolCall': {'name': 'run_command', 'args': {'CommandLine': 'git push origin main'}}}))
        self.assertEqual('deny', json.loads(antigravity.stdout)['decision'])


if __name__ == '__main__':
    unittest.main()
