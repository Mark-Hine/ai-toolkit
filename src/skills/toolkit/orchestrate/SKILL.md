---
name: orchestrate
description: "Turns the main session into a multi-agent coordinator that decomposes complex work into bounded subagent briefs, tracks progress in a compaction-safe ledger, isolates parallel file writes, and verifies evidence before reporting. Use when the user invokes orchestrate, says 'orchestrate', 'fan this out', or 'run this in parallel'."
argument_hint: "[task, status, or clean]"
invocation: manual
preamble: playbook
---

# Orchestrate: {@args}

Coordinate multi-part work by splitting it into independent tasks, dispatching bounded subagents, tracking state in a local ledger, and verifying every result before reporting. Stay in coordinator mode until the user says "stop orchestrating".

## When to dispatch vs work inline

- Answer questions that need no new work immediately.
- Do up to 3 quick file reads or searches yourself when needed to write an accurate brief. Send broad exploration across many files to {@explore}.
- Keep single-file edits and tight compile-fix loops on the main thread when spawning a subagent would cost more setup than the edit itself.
- Fan out independent research, module changes, verifications and reviews across subagents.

## How to dispatch and collect on this platform

<!-- if: target=claude -->
- **Subagents:** Call the `Agent` tool with `run_in_background: true` and a unique kebab-case `name`. Never leave `run_in_background` unset when you want non-blocking execution, because it defaults to foreground. Launch independent subagents in parallel in a single turn.
- **Long shell commands:** Pass `run_in_background: true` on `Bash` for builds, test suites, installs or servers that take more than 10 seconds.
- **Turn boundary:** End your turn after dispatching background tasks. Never poll or sleep. The harness sends a `<task-notification>` when a background agent or command finishes, which starts your next turn.
- **Follow-up and stop:** Use `SendMessage` with the agent's `name` to continue a topic with its context intact. Use `TaskStop` to cancel a running agent or background command.
- **Write isolation:** When 2 subagents write code at the same time, set `isolation: "worktree"` on each writer `Agent` call so their edits and build caches do not collide, or run them one after the other.
- **Agent Teams:** When `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is enabled and the user asks for a team or swarm, coordinate peer teammates through `SendMessage` and the shared team task list.
<!-- end -->
<!-- if: target=antigravity -->
- **Subagents:** Call `invoke_subagent` with one entry per parallel task in the `Subagents` array. Set `Model: "inherit"` unless the user requests another tier, or invoke a toolkit specialist (`android-researcher`, `android-reviewer`, `android-verifier`, `ios-*`, `web-*`, `ui-reviewer`), which already pins its own model. Use `TypeName: "research"` for read-only exploration and `TypeName: "self"` when a delegated task must edit files.
- **Long shell commands:** Call `run_command` with a bounded `WaitMsBeforeAsync` (such as `5000` to `10000` ms) so slow builds and test suites move to the background. Manage running tasks with `manage_task` (`status`, `send_input`, `kill`).
- **Turn boundary:** After launching background subagents or tasks and doing any immediate local preparation, end your turn. Never poll `manage_subagents` or `manage_task` in a loop. Antigravity wakes the session automatically when a subagent messages back or a background task completes.
- **Follow-up and stop:** Use `send_message` with `Recipient` set to the subagent's `conversationId` to send follow-up instructions (which wakes an idle subagent with its context intact). Use `manage_subagents` (`list`, `kill`, `kill_all`) to inspect or stop active subagents.
- **Write isolation:** When 2 `self` subagents write files in parallel, set `Workspace: "share"` (git worktree sharing the repo history) or `Workspace: "branch"` (isolated clone) on `invoke_subagent`. Use `Workspace: "inherit"` only when at most 1 writer touches the working tree.
<!-- end -->
<!-- if: target=codex -->
- **Subagents:** Spawn child agents with `spawn_agent`, using the installed toolkit specialist roles (`android-researcher`, `android-reviewer`, `android-verifier`, `ios-*`, `web-*`, `ui-reviewer`) where they match the task. Respect the session concurrency limit in `~/.codex/config.toml` (`max_concurrent_threads_per_session = 3` by default). Queue extra tasks in the ledger and launch them as slots free up.
- **Follow-up and stop:** Use `send_message` to queue input to an existing child agent and `followup_task` to start or resume its work so its context stays intact. Use `interrupt_agent` to stop an active child turn.
- **Synchronization:** Codex does not start a new coordinator turn automatically after your turn ends. After spawning parallel children, do any independent local preparation first, then call `wait_agent` to collect their results within the turn before reporting or launching dependent steps. Do not poll in a busy loop.
- **Write isolation:** `spawn_agent` does not create a separate git worktree automatically, and toolkit specialist hooks block specialists from running `git`. When 2 tasks would edit overlapping files or run competing builds, either serialize the writers or create detached git worktrees yourself (`git worktree add --detach`) before delegating.
<!-- end -->

## Write a self-contained brief

A subagent sees nothing of this chat. Every brief must include these 7 items:

1. **Goal:** 1 sentence stating what to achieve and why.
2. **Known facts:** Exact file paths, line numbers, error messages, branch or SHA, and build or test commands from {@project_file_full}.
3. **Owned scope:** The exact files, module or question this agent owns, plus explicit exclusions so it knows what to leave alone. For any writer agent in a shared workspace, add: "Other agents are active in this repository. Preserve all edits outside your scope and touch only the files you own."
4. **Forbidden actions:** No `git commit`, `git push`, `git merge`, branch change, PR creation, deployment, external message send or data deletion unless the user asked for that action by name.
5. **Done check and budget:** The exact verification command or check it must run, the evidence it must quote, and a tool-call budget (about 15 to 25 calls) so it reports partial progress instead of hitting its turn limit silently.
6. **Report shape:** Under 300 words. Lead with the result, then the evidence (`file:line` and command output), then open questions or exclusions.
7. **Writing style:** Plain, short sentences with no filler, no em dashes and no en dashes.

## Pick the right agent and model tier

- **Toolkit specialists first:** Route platform research to `android-researcher`, `ios-researcher` or `web-researcher`. Route diff and UI review to `android-reviewer`, `ios-reviewer`, `web-reviewer` or `ui-reviewer`. Route test, simulator, emulator and browser checks to `android-verifier`, `ios-verifier` or `web-verifier`.
- **Research tier (`{@model research}`):** Use for bounded tasks where the done check fits in 1 sentence and a wrong answer is cheap to catch, such as a targeted lookup, a single-file fix with a known test, or a checklist verification.
- **Review tier (`{@model review}`):** Use for ambiguous or multi-file work, architecture, debugging without a known root cause, and code or UI review.
- **Escalation rule:** When a research-tier agent returns thin, incomplete or wrong work, re-dispatch the task on `{@model review}` (or verify and finish it yourself). Never retry the same failing prompt on `{@model research}`.
- **No recursive sub-orchestrators:** Keep orchestration flat in this session. Do not ask a subagent to spawn its own subagents.

## The ledger and cleanup

Keep a compact ledger under a `## Orchestrator ledger` heading in {@local_notes} in the current project when coordinating 2 or more subagents or multi-turn background work. {@local_notes} stays untracked and survives context compaction. Preserve any other notes already in {@local_notes}.

Write 1 line per task using colons and commas (never em dashes or en dashes):

```markdown
## Orchestrator ledger
- [running] audit-auth ({@model review}): find routes skipping session check, started 14:02
- [done] fix-billing ({@model review}): unit tests pass in BillingViewModelTest, finished 14:20
- [failed] repro-upload ({@model research}): no repro on debug build, needs server log, finished 14:31
```

- **Update and keep for reference:** Refresh the ledger when you dispatch, when an agent finishes or fails, and when an agent is stopped. Keep `[done]` and `[failed]` lines in place so the user and future turns can refer back to what ran and what passed.
- **Status check:** When the user passes `status` or asks for status, read {@local_notes} and summarize the `## Orchestrator ledger` section.
- **Clean up on command:** Only clear the ledger when the user passes `clean` or asks to "clean up", "clear ledger", or "stop orchestrating". Remove the `## Orchestrator ledger` section from {@local_notes} (and delete {@local_notes} if no other notes remain), and remove any leftover temporary git worktrees created for subagents.

## Each turn

1. If the argument or message is `status`, read and report `## Orchestrator ledger` from {@local_notes}. If it is `clean` or "stop orchestrating", run the ledger and worktree cleanup and confirm.
2. Otherwise, split the request into independent tasks and check the ledger for running or reusable agents.
3. Dispatch new tasks in parallel (within the platform's concurrency cap) or send follow-ups to existing agents on the same topic.
4. Update the ledger in {@local_notes}.
5. When results return, verify each claim and `file:line` citation before accepting it. Reject or follow up on weak work.
6. Report in 3 lines or fewer when only dispatching (what started, which agent or ID, and what happens next), or lead with the verified outcome when reporting completed work.
7. Batch any questions for the user into 1 short list while unaffected tasks continue. Never halt unrelated work for 1 open question.
