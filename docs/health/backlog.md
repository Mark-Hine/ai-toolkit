# Setup health backlog

Minor issues and open decisions from the doctor runs. Strike a line through when the numbers show it is fixed.

## Open decisions

- ~~Delete the 1,427 eval leftover folders under `~/.claude/projects` (2026-11-23).~~ Moved to the Trash on 2026-11-23.
- ~~Lower `cleanupPeriodDays` from 36500 to 180. This deletes older transcripts (2026-11-23).~~ Set to 120 on 2026-11-23.
- Make the trigger-eval harness run with its own config directory, or remove its project folder on exit, so new leftovers stop appearing (2026-11-23).
- ~~Bold rule: 65% of replies contain bold. Relax `writing-style.md` or add the rule to the hook (2026-11-23).~~ Relaxed in `writing-style.md` on 2026-11-23.
- Hook experiment, running since 2026-11-23: the `UserPromptSubmit` style hook is off in the local settings. The rule file still loads. Compare `dashes_per_1000_words`, `semicolons_per_1000_words`, `share_ending_in_offer` and `median_words` in the 2026-12-15 run, the first whose 14 days fall wholly inside the experiment, against the 2026-11-23 baseline. If they hold within the noise bands, remove the hook from `claude/home/settings.snippet.json`. If not, restore it from `~/.claude/health/style-hook.removed-2026-11-23.json`.
- ~~Firebase plugin: 0 calls in 14 days, 3 failed calls in all (2 Crashlytics timeouts and one before login) and a 993 MB cache. An earlier count of 79 login failures was a keyword overcount. Log in or disable it (2026-11-23).~~ Disabled on 2026-11-23. The 993 MB cache is still on disk.

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
- Reviewer agents ran out of turns in 2 of 12 judged sessions and needed a second message (2026-11-23, run 2).
- 2 of 3 judging subagents reported that the Grep tool was not available, although the brief rule tells subagents to use it (2026-11-23, run 2).
- The doctor has no rule for a second run on the same date. Run 2 used a `-run2` suffix on the scorecard and data files (2026-11-23, run 2).
- The collector does not split hook blocks by main session and subagent, or by agent role (2026-11-23, run 2).
- One session wrote a bearer token inline in a `curl` upload command after a connector upload call errored. The source of the token is not traced (2026-11-23, run 2).
- Specialist hook blocks: subagents took 23 of 27 hook blocks and 2 judged sessions lost their device check. 19 of the 21 specialist blocks predate the 13 November guard fix and the 2026-11-23 brief rule. Check in the next run that the count falls, and look at the allowlist only if it does not (2026-11-23, run 2).
