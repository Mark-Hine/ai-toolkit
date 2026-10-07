#!/usr/bin/env bash
# Installs the Claude Code layer: dotfiles (CLAUDE.md, rules, settings) by symlink, plugins via the marketplace.
# Idempotent. Requires: claude, git, jq. Re-run after `git pull`. Dotfile edits are live through the symlinks.
# Plugin edits are live at the next session (or /reload-plugins) when the marketplace points at this checkout,
# which is the default. Set MARKETPLACE_SOURCE=Mark-Hine/ai-toolkit to install from GitHub instead.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
CFG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MARKET="${MARKETPLACE_SOURCE:-$REPO_ROOT}"
PLUGINS=(guard-kit android-kit ios-kit pr-review design-kit toolkit)
for bin in claude git jq; do command -v "$bin" >/dev/null || { echo "missing: $bin"; exit 1; }; done
mkdir -p "$CFG/rules"

link() { # link <src> <dst>
  if [ -e "$2" ] && [ ! -L "$2" ]; then mv "$2" "$2.bak.$(date +%s)"; echo "backed up $2"; fi
  ln -sfn "$1" "$2"; echo "linked $2"
}
link "$HERE/home/CLAUDE.md" "$CFG/CLAUDE.md"
link "$REPO_ROOT/shared/guidance/common.md" "$CFG/rules/common.md"
link "$REPO_ROOT/shared/guidance/kotlin.md" "$CFG/rules/kotlin.md"
link "$REPO_ROOT/shared/guidance/design-standards.md" "$CFG/rules/design-standards.md"
link "$REPO_ROOT/shared/guidance/design-assets.md" "$CFG/rules/design-assets.md"
link "$HERE/home/rules/writing-style.md" "$CFG/rules/writing-style.md"
link "$HERE/home/rules/android" "$CFG/rules/android"
link "$HERE/home/rules/ios" "$CFG/rules/ios"
[ -f "$CFG/machine.md" ] || { cp "$HERE/home/machine.md.example" "$CFG/machine.md"; echo "created $CFG/machine.md (edit it)"; }

# Merge settings: existing keys win for scalars; permissions.allow is unioned; hooks and skillOverrides merged.
# An existing hook is replaced when it is one the snippet manages: same command, a statusMessage starting
# "ai-toolkit: ", or the style echo from before that marker existed. So a reworded hook never runs twice.
# includeCoAuthoredBy is deprecated in favour of attribution and is dropped when attribution is present.
S="$CFG/settings.json"; [ -f "$S" ] || echo '{}' > "$S"
cp "$S" "$S.bak.$(date +%s)"
jq -s '
  .[0] as $cur | .[1] as $new |
  [$new.hooks[]? | .[]? | .hooks[]? | .command] as $managed_commands |
  $new * $cur
  | .permissions.allow = ((($cur.permissions.allow // []) + ($new.permissions.allow // [])) | unique)
  | .skillOverrides = (($new.skillOverrides // {}) + ($cur.skillOverrides // {}))
  | if .attribution then del(.includeCoAuthoredBy) else . end
  | .hooks = (reduce (((($cur.hooks // {}) | keys) + (($new.hooks // {}) | keys)) | unique)[] as $event ({};
      .[$event] = ([
        (($cur.hooks[$event] // [])[]
          | .hooks = [.hooks[] | select(
              (.command as $command | ($managed_commands | index($command)) == null)
              and ((.statusMessage // "") | startswith("ai-toolkit: ") | not)
              and ((.command // "") | startswith("echo '\''Style: follow ~/.claude/rules/writing-style.md") | not))]
          | select(.hooks | length > 0)),
        ($new.hooks[$event] // [])[]
      ] | unique)))
' "$S" "$HERE/home/settings.snippet.json" > "$S.tmp" && mv "$S.tmp" "$S"
echo "merged settings into $S"

# Marketplace: add once, update afterwards. Never remove a marketplace that points somewhere else.
failures=()
existing="$(claude plugin marketplace list --json 2>/dev/null | jq -r '.[]? | select(.name == "ai-toolkit") | (.path // .repo // .url // "")' 2>/dev/null | head -1 || true)"
if [ -z "$existing" ]; then
  claude plugin marketplace add "$MARKET" || failures+=("marketplace add $MARKET")
elif [ "$existing" = "$MARKET" ] || [ "$(cd "$existing" 2>/dev/null && pwd)" = "$MARKET" ]; then
  claude plugin marketplace update ai-toolkit || failures+=("marketplace update")
else
  echo "marketplace ai-toolkit already points at '$existing', not '$MARKET'."
  echo "To switch: claude plugin marketplace remove ai-toolkit, then re-run this script."
  claude plugin marketplace update ai-toolkit || failures+=("marketplace update")
fi
installed="$(claude plugin list --json 2>/dev/null | jq -r '.[]? | .id // empty' 2>/dev/null || true)"
for p in "${PLUGINS[@]}"; do
  if printf '%s\n' "$installed" | grep -qx "$p@ai-toolkit"; then
    claude plugin update "$p@ai-toolkit" || failures+=("update $p")
  else
    claude plugin install "$p@ai-toolkit" --scope user || failures+=("install $p")
  fi
done

if [ "${#failures[@]}" -gt 0 ]; then
  printf 'FAILED: %s\n' "${failures[@]}"
  echo "Fix the failures above, or run the equivalent /plugin commands inside Claude Code."
  exit 1
fi

cat <<MSG

Done. Start a new Claude Code session and check:
  /memory   -> CLAUDE.md, rules/common.md, rules/writing-style.md, rules/design-standards.md
               (rules/kotlin.md, rules/design-assets.md, rules/android/* and rules/ios/* load on matching files)
  /agents   -> android-reviewer, android-researcher, android-verifier, ios-reviewer, ios-researcher, ios-verifier, ui-reviewer
  /skills   -> android-kit:*, ios-kit:*, pr-review:pr-review, design-kit:iterate, design-kit:standards
Edit $CFG/machine.md with your AVD names, simulator, CLI paths and ticket prefix.
Plugin edits take effect at the next session or /reload-plugins when the marketplace is this checkout.
When it is GitHub, bump the plugin version and run: claude plugin update <name>@ai-toolkit
MSG
