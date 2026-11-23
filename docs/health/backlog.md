# Setup health backlog

Minor issues and open decisions from the doctor runs. Strike a line through when the numbers show it is fixed.

## Open decisions

- Delete the 1,427 eval leftover folders under `~/.claude/projects` (2026-11-23).
- Lower `cleanupPeriodDays` from 36500 to 180. This deletes older transcripts (2026-11-23).
- Make the trigger-eval harness run with its own config directory, or remove its project folder on exit, so new leftovers stop appearing (2026-11-23).
- Bold rule: 65% of replies contain bold. Relax `writing-style.md` or add the rule to the hook (2026-11-23).
- Hook experiment: turn the `UserPromptSubmit` style hook off for one fortnight and compare the style rates in the next run (2026-11-23).
- Firebase plugin: 0 calls in 14 days, 79 login failures over 60 days and a 993 MB cache. Log in or disable it (2026-11-23).

## Minor issues

- 26 skill folders in `~/.claude/skills` are byte-identical copies of `~/.agents/skills`. The skills installer manages them, so they stay until it offers symlinks (2026-11-23).
- 4 stale plugin versions and an orphaned guard-kit 1.4.0 sit in the plugin cache (2026-11-23).
- `autoMode.environment` in the home settings carries 11 "None configured" lines, 2,590 characters (2026-11-23).
- `swift_lint.py` skips silently when swiftlint is missing (2026-11-23).
- Reviewer agents cap reports at 500 words and the brief template caps them at 300 (2026-11-23).
- `common.md` says to ask about network-security changes and `guard.py` hard-denies them (2026-11-23).
- The harness adds a recap box to each turn, which the no-recap rule cannot change. The rule should exempt it (2026-11-23).
- One 680 KB file was read 3 times in one session, and tool search repeated identical queries 116 times over 60 days (2026-11-23).
- 8 offered MCP servers were never called over 60 days (2026-11-23).
- One memory says never to create Jira issues, and the ticket-drafting skills still offer to create them on a typed confirmation (2026-11-23).
- 3 memories restate rules that already load: the personal commit email, a project writing-style note and a commit-message note (2026-11-23).
- 63 old plan files and 35 MB of file history sit under the home config (2026-11-23).
- Android plugin evals: add 2 or 3 `claude plugin eval` cases for the bugfix playbook, one regression test and a filtered run, and read the with-without delta (2026-11-23).
- The source of the worktree-isolation block and the stale agent-type names in playbooks are not yet traced (2026-11-23).
