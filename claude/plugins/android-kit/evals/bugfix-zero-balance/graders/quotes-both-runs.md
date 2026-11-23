---
type: llm
focus: last_message
---

PASS if the final message states the root cause in plain words and reports both a failing test run before the fix and a passing run after it.
FAIL if the message claims the fix works without reporting a test run, or reports only a passing run.
