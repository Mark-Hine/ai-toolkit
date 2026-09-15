#!/usr/bin/env python3
"""Refresh the writing rules through the supported UserPromptSubmit hook."""
import json
from pathlib import Path
import sys

# Consume the event without copying its potentially private prompt into output.
json.load(sys.stdin)
path = Path(sys.argv[1])
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit',
    'additionalContext': 'Follow the personal writing rules at ' + str(path) + '. Use plain prose, no em dashes, and end when the content ends.'}}))
