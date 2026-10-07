#!/usr/bin/env bash
# Runs the real hooks.json commands of guard-kit and ios-kit against sample payloads, the way Claude Code invokes them.
# Unit coverage of the policy itself lives in shared/tests. Run from anywhere: bash claude/tests/test-guards.sh
set -u
cd "$(dirname "$0")/.." || exit 1
fail=0
command_of() { jq -r ".hooks.$1[0].hooks[0].command" "$2"; }
GUARD_CMD="$(command_of PreToolUse plugins/guard-kit/hooks/hooks.json)"
LINT_CMD="$(command_of PostToolUse plugins/ios-kit/hooks/hooks.json)"
run() { # run <plugin-root> <command> <payload> -> prints "exit stdout"
  local out; out="$(printf '%s' "$3" | CLAUDE_PLUGIN_ROOT="$1" bash -c "$2" 2>/dev/null)"; printf '%s %s' "$?" "$out"
}
expect() { # expect <label> <want: allow|deny|ask> <payload> [role]
  local payload="$3"
  [ -n "${4:-}" ] && payload="$(printf '%s' "$payload" | jq -c --arg r "$4" '. + {agent_type: $r}')"
  local got; got="$(run plugins/guard-kit "$GUARD_CMD" "$payload")"
  local code="${got%% *}" body="${got#* }"
  local decision="allow"
  [ "$code" != 0 ] && decision="blocked-exit-$code"
  [ "$code" = 0 ] && [ -n "$body" ] && decision="$(printf '%s' "$body" | jq -r '.hookSpecificOutput.permissionDecision // "unknown"')"
  if [ "$decision" = "$2" ]; then echo "ok   [$1]"; else echo "FAIL [$1] want $2 got $decision"; fail=1; fi
}
bash_payload() { jq -nc --arg c "$1" '{tool_name:"Bash", tool_input:{command:$c}}'; }
edit_payload() { jq -nc --arg p "$1" '{tool_name:"Edit", tool_input:{file_path:$p}}'; }

expect "push develop"            deny  "$(bash_payload 'git push origin develop')"
expect "push main after cd"      deny  "$(bash_payload 'cd x && git push -u origin main')"
expect "push HEAD:refs/heads/main" deny "$(bash_payload 'git push origin HEAD:refs/heads/main')"
expect "bare push"               deny  "$(bash_payload 'git push')"
expect "push HEAD"               deny  "$(bash_payload 'git push origin HEAD')"
expect "delete remote branch"    deny  "$(bash_payload 'git push origin --delete feature/old')"
expect "nested shell push"       deny  "$(bash_payload 'bash -c "git push origin main"')"
expect "env prefix push"         deny  "$(bash_payload 'FOO=1 git push origin main')"
expect "--force"                 deny  "$(bash_payload 'git push --force origin feature/x')"
expect "-uf combined"            deny  "$(bash_payload 'git push -uf origin feature/x')"
expect "+refspec"                deny  "$(bash_payload 'git push origin +feature/x')"
expect "feature push"            allow "$(bash_payload 'git push -u origin feat/MBS-1-slug')"
expect "python +expr then push"  allow "$(bash_payload 'python3 -c "s=a+new+b"; git push origin feature/x')"
expect "grep main without push"  allow "$(bash_payload 'grep -n main README.md')"
expect "push text inside echo"   allow "$(bash_payload "echo 'run: git push origin main later'")"
expect "timeout any command"     deny  "$(bash_payload 'timeout 300 xcodebuild -scheme App test')"
expect "time timeout"            deny  "$(bash_payload 'time timeout 5 ls')"
expect "--timeout flag"          allow "$(bash_payload 'adb shell am start --timeout 1000 com.x/.Main')"
expect "timeout word in text"    allow "$(bash_payload 'echo timeout 30 seconds')"
expect "reset --hard"            deny  "$(bash_payload 'git reset --hard HEAD~1')"
expect "git restore ."           deny  "$(bash_payload 'git restore .')"
expect "git restore --staged ."  allow "$(bash_payload 'git restore --staged .')"
expect "plain gradle"            allow "$(bash_payload './gradlew :app:compileDevDebugKotlin')"
expect "google-services.json"    deny  "$(edit_payload '/x/app/src/dev/google-services.json')"
expect "AuthKey p8"              deny  "$(edit_payload '/x/AuthKey_ABC.p8')"
expect "keystore.properties"     deny  "$(edit_payload '/x/keystore.properties')"
expect ".git/config"             deny  "$(edit_payload '/x/.git/config')"
expect ".env"                    deny  "$(edit_payload '/x/.env')"
expect ".env.example"            allow "$(edit_payload '/x/.env.example')"
expect "workflow asks"           ask   "$(edit_payload '/x/.github/workflows/ci.yml')"
expect "kotlin source"           allow "$(edit_payload '/x/app/src/main/java/Foo.kt')"
expect "researcher docs"         allow "$(bash_payload 'android docs search compose')"     android-kit:android-researcher
expect "researcher gradle"       deny  "$(bash_payload './gradlew test')"                  android-kit:android-researcher
expect "verifier test task"      allow "$(bash_payload './gradlew :app:testDevDebugUnitTest')" android-kit:android-verifier
expect "verifier install"        deny  "$(bash_payload './gradlew installDebug')"          android-kit:android-verifier
expect "verifier init script"    deny  "$(bash_payload './gradlew test -I x.gradle')"      android-kit:android-verifier
expect "verifier edit"           deny  "$(edit_payload '/x/journeys/a.xml')"               android-kit:android-verifier
expect "ios researcher version"  allow "$(bash_payload 'xcodebuild -version')"             ios-kit:ios-researcher
expect "ios researcher build"    deny  "$(bash_payload 'xcodebuild build')"                ios-kit:ios-researcher
expect "ios verifier test"       allow "$(bash_payload 'xcodebuild test -scheme App')"     ios-kit:ios-verifier
expect "web verifier test"       allow "$(bash_payload 'npx vitest run src/cart.test.ts')" web-kit:web-verifier
expect "web verifier install"    deny  "$(bash_payload 'npm install left-pad')"           web-kit:web-verifier
expect "web researcher view"     allow "$(bash_payload 'npm view next version')"          web-kit:web-researcher
expect "ios verifier erase"      deny  "$(bash_payload 'xcrun simctl erase all')"          ios-kit:ios-verifier
expect "Explore keeps bash"      allow "$(bash_payload './gradlew installDebug')"          Explore

# Without python3 on PATH the hook must block (exit 2), not fail open.
got="$(printf '%s' "$(bash_payload 'git status')" | CLAUDE_PLUGIN_ROOT=plugins/guard-kit PATH=/usr/bin/nonexistent /bin/bash -c "$GUARD_CMD" 2>/dev/null; echo "exit=$?")"
case "$got" in *"exit=2"*) echo "ok   [no python3 blocks]";; *) echo "FAIL [no python3 blocks] got $got"; fail=1;; esac

# Swift lint hook: a non-swift edit produces no output and exits 0.
got="$(printf '%s' "$(edit_payload '/x/README.md')" | CLAUDE_PLUGIN_ROOT=plugins/ios-kit bash -c "$LINT_CMD" 2>/dev/null; echo "exit=$?")"
case "$got" in "exit=0") echo "ok   [lint ignores non-swift]";; *) echo "FAIL [lint ignores non-swift] got $got"; fail=1;; esac
exit $fail
