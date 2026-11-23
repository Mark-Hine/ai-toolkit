---
description: A one-line bug. The agent should add one regression test, run it filtered, fix the bug and leave the other tests alone.
tags: [android, tests]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Edit, Write, Bash, Skill, Agent, TodoWrite]
---

Bug: the rewards tile shows "0 point" when the balance is zero. It should say "0 points". Fix it.
