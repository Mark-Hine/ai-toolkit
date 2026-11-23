---
description: A small behaviour change. The agent should add a few distinct tests for the new rule, run them filtered and keep the existing tests.
tags: [android, tests]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Edit, Write, Bash, Skill, Agent, TodoWrite]
---

Change the rewards label so a balance above 9,999 shows "9,999+ points". Balances up to 9,999 keep the current label.
