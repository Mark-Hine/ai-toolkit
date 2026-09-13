#!/usr/bin/env bash
# PreToolUse(Edit|Write|NotebookEdit) guardrail. Blocks edits to secrets, signing material and generated files (Android + iOS). Exit 2 = block with reason on stderr.
set -u
input="$(cat)"
path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')"
[ -z "$path" ] && exit 0

deny() { printf 'BLOCKED by .claude/hooks/guard-edit.sh: %s (%s)\n' "$1" "$path" >&2; exit 2; }

case "$path" in
  */google-services.json)            deny "Firebase config is tracked and environment-specific; never edited by Claude" ;;
  */secrets.properties|*/local.properties) deny "local secrets file" ;;
  */network_security_config.xml)     deny "cert pinning / network security config changes need explicit user approval; ask first" ;;
  */app/libs/*.aar|*/app/libs/*.jar) deny "vendored binary SDK" ;;
  */GoogleService-Info.plist)        deny "Firebase config is tracked and environment-specific; never edited by Claude" ;;
  *.jks|*.keystore|*.p12|*.pem|*.key|*.mobileprovision|*.cer) deny "signing material" ;;
  */.env|*/.env.*)                   deny "environment secrets file" ;;
  */gradle/wrapper/gradle-wrapper.jar) deny "wrapper jar is updated via ./gradlew wrapper, not edited" ;;
esac
exit 0
