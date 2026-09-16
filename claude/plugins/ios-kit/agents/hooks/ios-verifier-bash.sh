#!/usr/bin/env bash
# PreToolUse(Bash) inside ios-verifier: allow xcodebuild test, xcrun simctl/xcresulttool, sleep, ls, cat of result files. Block the rest.
set -u
cmd="$(cat | jq -r '.tool_input.command // empty')"
base="$(printf '%s' "$cmd" | sed -E 's/^[[:space:]]+//')"
if printf '%s' "$base" | grep -Eq '[;&|<>`]|\$\('; then
  printf 'ios-verifier: chained or redirected commands are not allowed. Blocked: %s\n' "$cmd" >&2; exit 2
fi
allow='^(xcodebuild[[:space:]]+test([[:space:]]|$)|xcodebuild[[:space:]]+test-without-building([[:space:]]|$)|xcrun[[:space:]]+xcresulttool[[:space:]]+get([[:space:]]|$)|xcrun[[:space:]]+simctl[[:space:]]+(launch|openurl|io|ui|list|listapps|bootstatus|spawn[[:space:]]+[^[:space:]]+[[:space:]]+log[[:space:]]+show|get_app_container)([[:space:]]|$)|sleep[[:space:]]+[0-9.]+$|ls([[:space:]]|$)|cat[[:space:]]+[^[:space:]]+\.(json|txt|log|plist)$)'
if printf '%s' "$base" | grep -Eq "$allow"; then exit 0; fi
printf 'ios-verifier may only run xcodebuild test|test-without-building, xcrun xcresulttool get, xcrun simctl launch|openurl|io|ui|list|listapps|bootstatus|spawn … log show|get_app_container, sleep, ls, cat of json/txt/log/plist. Blocked: %s\n' "$cmd" >&2
exit 2
