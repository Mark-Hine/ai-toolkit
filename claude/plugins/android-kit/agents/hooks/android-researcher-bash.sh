#!/usr/bin/env bash
# PreToolUse(Bash) inside android-researcher: allow only read-only android docs / sdk list commands.
set -u
cmd="$(cat | jq -r '.tool_input.command // empty')"
if printf '%s' "$cmd" | grep -Eq '^[[:space:]]*android[[:space:]]+(docs[[:space:]]+(search|fetch)|sdk[[:space:]]+list)([[:space:]]|$)'; then
  exit 0
fi
printf 'android-researcher may only run `android docs search|fetch` and `android sdk list`. Blocked: %s\n' "$cmd" >&2
exit 2
