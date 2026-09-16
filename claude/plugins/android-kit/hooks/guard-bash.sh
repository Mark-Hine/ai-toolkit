#!/usr/bin/env bash
# PreToolUse(Bash) guardrail. Blocks pushes to protected branches, force pushes, destructive git and timeout wrappers. Exit 2 = block with reason on stderr.
set -u
input="$(cat)"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"
[ -z "$cmd" ] && exit 0

deny() { printf 'BLOCKED by .claude/hooks/guard-bash.sh: %s\n' "$1" >&2; exit 2; }

# Pushes to protected branches, and any force push. Each shell segment is checked on its own, so a `--force` or a
# `+name` in an unrelated segment (worktree remove --force; python -c "a+b") cannot trip the push rules.
printf '%s\n' "$cmd" | awk 'BEGIN{RS="(;|&&|\\|\\||\\|)"} {print}' | while IFS= read -r seg; do
  seg="$(printf '%s' "$seg" | sed -E 's/^[[:space:]]+//; s/^(sudo[[:space:]]+)?//')"
  printf '%s' "$seg" | grep -Eq '^git[[:space:]]+([^[:space:]]+[[:space:]]+)*push([[:space:]]|$)' || continue
  printf '%s' "$seg" | grep -Eq -- '[[:space:]](--force|--force-with-lease(=[^[:space:]]*)?|--force-if-includes|-f|-[a-zA-Z]*f[a-zA-Z]*)([[:space:]]|$)' \
    && deny "force push is not allowed from Claude sessions"
  printf '%s' "$seg" | grep -Eq '[[:space:]]\+[A-Za-z0-9_./-]+' \
    && deny "force push (leading + refspec) is not allowed from Claude sessions"
  printf '%s' "$seg" | grep -Eq '([[:space:]:])(develop|main|master|release/[^[:space:]]*)([[:space:]]|$)' \
    && deny "pushing to develop/main/release/* is not allowed; push the feature branch and open a PR"
done
# the while loop runs in a subshell; propagate a deny from inside it
[ "${PIPESTATUS[2]:-0}" -eq 2 ] && exit 2

# macOS has no `timeout` binary; wrapping any command in it fails before the command runs.
printf '%s' "$cmd" | grep -Eq '(^|[;&|(][[:space:]]*|\bsudo[[:space:]]+)timeout[[:space:]]+([^;&|]*[[:space:]])?[0-9]+(\.[0-9]+)?[smhd]?[[:space:]]+[^[:space:]]' \
  && deny "no timeout binary on macOS; use the Bash tool's timeout parameter instead"

# Destructive git on the working tree.
printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git[[:space:]]+(reset[[:space:]]+--hard|clean[[:space:]]+-[a-zA-Z]*f|checkout[[:space:]]+--[[:space:]]+\.)' \
  && deny "destructive git command; ask the user first"

exit 0
