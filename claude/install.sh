#!/usr/bin/env bash
# Installs the Claude Code layer: dotfiles (CLAUDE.md, rules, settings) by symlink, plugins via the marketplace.
# Idempotent. Requires: claude, git, jq. Re-run after `git pull` to pick up changes (symlinks make most edits live).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
CFG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MARKET="${MARKETPLACE_SOURCE:-Mark-Hine/ai-toolkit}"   # or a local path for testing
for bin in claude git jq; do command -v "$bin" >/dev/null || { echo "missing: $bin"; exit 1; }; done
mkdir -p "$CFG/rules"

link() { # link <src> <dst>
  if [ -e "$2" ] && [ ! -L "$2" ]; then mv "$2" "$2.bak.$(date +%s)"; echo "backed up $2"; fi
  ln -sfn "$1" "$2"; echo "linked $2"
}
link "$HERE/home/CLAUDE.md" "$CFG/CLAUDE.md"
link "$REPO_ROOT/shared/guidance/common.md" "$CFG/rules/common.md"
link "$HERE/home/rules/writing-style.md" "$CFG/rules/writing-style.md"
link "$HERE/home/rules/android" "$CFG/rules/android"
link "$HERE/home/rules/ios" "$CFG/rules/ios"
[ -f "$CFG/machine.md" ] || { cp "$HERE/home/machine.md.example" "$CFG/machine.md"; echo "created $CFG/machine.md (edit it)"; }

# Merge settings: existing keys win for scalars; permissions.allow is unioned; hooks and skillOverrides merged.
S="$CFG/settings.json"; [ -f "$S" ] || echo '{}' > "$S"
cp "$S" "$S.bak.$(date +%s)"
jq -s '
  .[0] as $cur | .[1] as $new |
  [$new.hooks[]? | .[]? | .hooks[]? | .command] as $managed_commands |
  $new * $cur
  | .permissions.allow = ((($cur.permissions.allow // []) + ($new.permissions.allow // [])) | unique)
  | .skillOverrides = (($new.skillOverrides // {}) + ($cur.skillOverrides // {}))
  | .hooks = (reduce (((($cur.hooks // {}) | keys) + (($new.hooks // {}) | keys)) | unique)[] as $event ({};
      .[$event] = ([
        (($cur.hooks[$event] // [])[]
          | .hooks = [.hooks[] | select(.command as $command | ($managed_commands | index($command)) == null)]
          | select(.hooks | length > 0)),
        ($new.hooks[$event] // [])[]
      ] | unique)))
' "$S" "$HERE/home/settings.snippet.json" > "$S.tmp" && mv "$S.tmp" "$S"
echo "merged settings into $S"

claude plugin marketplace add "$MARKET" 2>/dev/null || claude plugin marketplace update 2>/dev/null || true
for p in android-kit ios-kit pr-review; do claude plugin install "$p@ai-toolkit" --scope user 2>/dev/null || echo "install $p manually: /plugin install $p@ai-toolkit"; done

cat <<MSG

Done. Start a new Claude Code session and check:
  /context   -> CLAUDE.md, rules/writing-style.md, rules/android/* under Memory files; android-reviewer, android-researcher under agents
  /skills    -> android-kit:*, ios-kit:*, pr-review:pr-review
Edit $CFG/machine.md with your AVD names and ticket prefix.
MSG
