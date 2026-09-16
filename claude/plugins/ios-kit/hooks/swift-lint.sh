#!/usr/bin/env bash
# PostToolUse(Edit|Write) for .swift files. Runs SwiftFormat --lint and SwiftLint only when the repo opts in
# (a .swiftformat or .swiftlint.yml exists at the repo root) and the binary is installed. Exit 2 feeds violations back to Claude.
set -u
f="$(cat | jq -r '.tool_input.file_path // empty')"
case "$f" in *.swift) ;; *) exit 0 ;; esac
[ -f "$f" ] || exit 0
root="$(cd "$(dirname "$f")" && git rev-parse --show-toplevel 2>/dev/null)" || exit 0
out=""
if [ -f "$root/.swiftformat" ] && command -v swiftformat >/dev/null; then
  r="$(swiftformat --lint --quiet "$f" 2>&1)" || out="$out"$'\n'"swiftformat: $r"
fi
if [ -f "$root/.swiftlint.yml" ] && command -v swiftlint >/dev/null; then
  r="$(cd "$root" && swiftlint lint --quiet --config .swiftlint.yml "$f" 2>&1)"; [ -n "$r" ] && out="$out"$'\n'"swiftlint: $r"
fi
if [ -n "$out" ]; then printf 'Lint findings in %s (fix them, do not disable rules):%s\n' "$f" "$out" >&2; exit 2; fi
exit 0
