#!/usr/bin/env bash
# PreToolUse(Bash) inside android-verifier: allow gradle test tasks, the Android CLI, adb and sleep. Block the rest.
set -u
cmd="$(cat | jq -r '.tool_input.command // empty')"
base="$(printf '%s' "$cmd" | sed -E 's/^[[:space:]]+//')"
# no chaining, redirection or substitution so the allowlist cannot be bypassed
if printf '%s' "$base" | grep -Eq '[;&|<>`]|\$\('; then
  printf 'android-verifier: chained or redirected commands are not allowed. Blocked: %s\n' "$cmd" >&2; exit 2
fi
allow='^(\./gradlew[[:space:]]+(-q[[:space:]]+)?(:[A-Za-z0-9_-]+:)?(test|connected)[A-Za-z0-9]*(UnitTest|AndroidTest)?([[:space:]]|$)|android[[:space:]]+(layout|screen|emulator[[:space:]]+list|info|docs)([[:space:]]|$)|adb([[:space:]]+-s[[:space:]]+[^[:space:]]+)?[[:space:]]+(shell[[:space:]]+(input|dumpsys|am[[:space:]]+start|monkey|pm[[:space:]]+list)|logcat|devices)([[:space:]]|$)|sleep[[:space:]]+[0-9.]+$|ls([[:space:]]|$)|cat[[:space:]]+[^[:space:]]+\.(xml|json|txt)$)'
if printf '%s' "$base" | grep -Eq "$allow"; then exit 0; fi
printf 'android-verifier may only run gradle test tasks, android layout/screen/emulator list/info/docs, adb shell input|dumpsys|am start|monkey|pm list, adb logcat/devices, sleep, ls, cat of xml/json/txt. Blocked: %s\n' "$cmd" >&2
exit 2
