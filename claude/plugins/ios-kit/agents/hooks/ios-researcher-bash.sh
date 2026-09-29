#!/usr/bin/env bash
# PreToolUse(Bash) inside ios-researcher: allow only read-only Apple tooling queries.
set -u
cmd="$(cat | jq -r '.tool_input.command // empty')"

# One optional trailing read-only filter (| head/tail/grep/sort/uniq/wc) is tolerated; strip it before matching.
base="$(printf '%s' "$cmd" | sed -E 's/[[:space:]]*\|[[:space:]]*(head|tail|grep|sort|uniq|wc)([[:space:]][^;&|<>`$]*)?$//')"

# No chaining, redirection or substitution anywhere else.
if printf '%s' "$base" | grep -Eq '[;&|<>`]|\$\('; then
  printf 'ios-researcher: command chaining/redirection is not allowed. Blocked: %s\n' "$cmd" >&2
  exit 2
fi

allow='^[[:space:]]*('
allow+='xcodebuild[[:space:]]+-(version|showsdks|list|showBuildSettings|showdestinations)'
allow+='|xcrun[[:space:]]+simctl[[:space:]]+list'
allow+='|xcrun[[:space:]]+--show-sdk-(version|path|platform-version)'
allow+='|xcrun[[:space:]]+xcodebuild[[:space:]]+-(version|showsdks)'
allow+='|swift[[:space:]]+--version'
allow+='|swift[[:space:]]+package[[:space:]]+(describe|show-dependencies|dump-package)'
allow+='|pod[[:space:]]+(--version|outdated)'
allow+=')([[:space:]]|$)'

if printf '%s' "$base" | grep -Eq "$allow"; then
  exit 0
fi
printf 'ios-researcher may only run read-only tooling queries (xcodebuild -version|-showsdks|-list|-showBuildSettings|-showdestinations, xcrun simctl list, xcrun --show-sdk-*, swift --version, swift package describe|show-dependencies|dump-package, pod --version|outdated). Blocked: %s\n' "$cmd" >&2
exit 2
