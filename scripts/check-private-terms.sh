#!/usr/bin/env bash
# Fails if any private, personal or employer-specific term appears in tracked files.
# Add terms here as you discover them. Case-insensitive.
set -u
TERMS='humm|cofi|flexigroup|flexirent|hummloan|group-ib|gibsdk|MBS-[0-9]|DE-[0-9]{4}|mark\.hine|/Users/|Kingshuk|Deloitte|converge[^d]|Pixel_|channels-mobile|visualstudio|@humm'
cd "$(git rev-parse --show-toplevel)"
hits=$(git ls-files -z | xargs -0 grep -n -i -E "$TERMS" -- 2>/dev/null | grep -v '^scripts/check-private-terms.sh:' || true)
if [ -n "$hits" ]; then
  echo "Private terms found:"; echo "$hits"; exit 1
fi
echo "No private terms found."
