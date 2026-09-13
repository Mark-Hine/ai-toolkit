#!/usr/bin/env bash
# PreToolUse(Bash) guardrail. Blocks pushes to protected branches, force pushes, destructive git and timeout wrappers. Exit 2 = block with reason on stderr.
set -u
input="$(cat)"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"
[ -z "$cmd" ] && exit 0

deny() { printf 'BLOCKED by .claude/hooks/guard-bash.sh: %s\n' "$1" >&2; exit 2; }

# Pushes to protected branches, and any force push.
if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git[[:space:]]+push([[:space:]]|$)'; then
  printf '%s' "$cmd" | grep -Eq -- '(--force|--force-with-lease|-f([[:space:]]|$))' \
    && deny "force push is not allowed from Claude sessions"
  printf '%s' "$cmd" | grep -Eq -- 'git[[:space:]]+push[[:space:]]+(-[a-zA-Z-]+[[:space:]]+)*([^[:space:]]+[[:space:]]+)?\+[A-Za-z0-9_./-]+' \
    && deny "force push (leading + refspec) is not allowed from Claude sessions"
  printf '%s' "$cmd" | grep -Eq '([[:space:]:])(develop|main|master|release/[^[:space:]]*)([[:space:]]|$)' \
    && deny "pushing to develop/main/release/* is not allowed; push the feature branch and open a PR"
fi

# macOS has no `timeout` binary; wrapping any command in it fails before the command runs.
printf '%s' "$cmd" | grep -Eq '(^|[;&|(][[:space:]]*|\bsudo[[:space:]]+)timeout[[:space:]]+([^;&|]*[[:space:]])?[0-9]+(\.[0-9]+)?[smhd]?[[:space:]]+[^[:space:]]' \
  && deny "no timeout binary on macOS; use the Bash tool's timeout parameter instead"

# Destructive git on the working tree.
printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git[[:space:]]+(reset[[:space:]]+--hard|clean[[:space:]]+-[a-zA-Z]*f|checkout[[:space:]]+--[[:space:]]+\.)' \
  && deny "destructive git command; ask the user first"

exit 0
