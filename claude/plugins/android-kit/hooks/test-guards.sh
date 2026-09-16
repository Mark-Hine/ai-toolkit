#!/usr/bin/env bash
# Regression suite for guard-bash.sh and guard-edit.sh. Run from anywhere: bash hooks/test-guards.sh
cd "$(dirname "$0")"; fail=0
t(){ # t <script> <want-exit> <label> <command-or-path>
  if [ "$1" = guard-edit.sh ]; then j=$(printf '{"tool_input":{"file_path":"%s"}}' "$4"); else j=$(printf '{"tool_input":{"command":"%s"}}' "$4"); fi
  printf '%s' "$j" | ./$1 >/dev/null 2>&1; got=$?
  if [ "$got" -eq "$2" ]; then echo "ok   [$3]"; else echo "FAIL [$3] want $2 got $got"; fail=1; fi
}
t guard-bash.sh 2 "push develop"                 "git push origin develop"
t guard-bash.sh 2 "push main after cd"           "cd x && git push -u origin main"
t guard-bash.sh 2 "--force"                      "git push --force origin feature/x"
t guard-bash.sh 2 "--force-with-lease=main"      "git push --force-with-lease=main origin feature/x"
t guard-bash.sh 2 "-f"                           "git push -f origin feature/x"
t guard-bash.sh 2 "-uf combined"                 "git push -uf origin feature/x"
t guard-bash.sh 2 "+refspec"                     "git push origin +feature/x"
t guard-bash.sh 2 "sudo push develop"            "sudo git push origin develop"
t guard-bash.sh 2 "git -C repo push main"        "git -C ~/x push origin main"
t guard-bash.sh 0 "feature push"                 "git push -u origin feature/PROJ-1"
t guard-bash.sh 0 "delete remote branch"         "git push -q origin --delete feature/old"
t guard-bash.sh 0 "worktree --force then push"   "git worktree remove --force .claude/wt && git push origin --delete feature/old"
t guard-bash.sh 0 "python +expr then push"       "python3 -c \\\"s=a+new+b\\\"; git push origin feature/x"
t guard-bash.sh 0 "grep main without push"       "grep -n main README.md"
t guard-bash.sh 0 "git log main"                 "git log origin/main..HEAD"
t guard-bash.sh 0 "push text inside echo"        "echo 'run: git push origin main later'"
t guard-bash.sh 2 "timeout any command"          "timeout 300 xcodebuild -scheme App test"
t guard-bash.sh 2 "timeout with flags"           "timeout -s KILL 5 ./gradlew help"
t guard-bash.sh 0 "--timeout flag"               "adb shell am start --timeout 1000 com.x/.Main"
t guard-bash.sh 0 "timeout word in text"         "echo timeout 30 seconds"
t guard-bash.sh 2 "reset --hard"                 "git reset --hard HEAD~1"
t guard-bash.sh 2 "clean -fd"                    "git clean -fd"
t guard-bash.sh 0 "plain gradle"                 "./gradlew :app:compileDevDebugKotlin"
t guard-edit.sh 2 "google-services.json"         "/x/app/src/dev/google-services.json"
t guard-edit.sh 2 "GoogleService-Info.plist"     "/x/App/GoogleService-Info.plist"
t guard-edit.sh 2 "network_security_config"      "/x/app/src/main/res/xml/network_security_config.xml"
t guard-edit.sh 2 "keystore"                     "/x/release.jks"
t guard-edit.sh 2 "Podfile.lock"                 "/x/ios/Podfile.lock"
t guard-edit.sh 2 ".env"                         "/x/.env"
t guard-edit.sh 0 "kotlin source"                "/x/app/src/main/java/Foo.kt"
t guard-edit.sh 0 "swift source"                 "/x/App/Foo.swift"
exit $fail
