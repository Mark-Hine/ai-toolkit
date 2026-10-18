---
verified: 2026-10-18
sources:
  - https://code.claude.com/docs/en/sub-agents
  - https://code.claude.com/docs/en/agent-teams
  - https://code.claude.com/docs/en/tools-reference
  - https://code.claude.com/docs/en/memory
  - https://code.claude.com/docs/en/skills
  - https://learn.chatgpt.com/docs/agent-configuration/subagents
  - https://learn.chatgpt.com/docs/build-skills
  - https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_spec.rs
  - https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json
  - https://antigravity.google/docs/subagents/
---

# Orchestrate platform sources

The dispatch rules in this skill name platform tools and parameters that change between releases. This file records where each one comes from, so the audit can re-check them. Re-verify every row when a platform ships a new subagent or task tool.

<!-- if: target=claude -->
## Claude Code

| Fact the skill relies on | Source |
| --- | --- |
| Subagents run in the background by default, and results arrive as a completion notification in a later turn | sub-agents |
| The `Agent` call takes `name`, `model` and `isolation: "worktree"`, and `SendMessage` resumes an agent by ID or name | sub-agents |
| A subagent can spawn its own subagents up to 3 layers deep by default | sub-agents |
| `TaskStop` stops a background task, and `Bash` takes `run_in_background: true` | tools-reference |
| Agent Teams need `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and share a team task list | agent-teams |
| A `CLAUDE.local.md` counts as a `CLAUDE.md`, so creating one stops Claude reading `AGENTS.md` under the default `claude-md-or-agents-md` setting | memory |
| With `disable-model-invocation: true` the description is not in context | skills |
<!-- end -->

<!-- if: target=codex -->
## OpenAI Codex

| Fact the skill relies on | Source |
| --- | --- |
| The V2 tools are `spawn_agent`, `send_message`, `followup_task`, `wait_agent`, `interrupt_agent` and `list_agents` | multi_agents_spec.rs |
| The V1 tools are `spawn_agent`, `send_input`, `resume_agent`, `wait_agent` and `close_agent`, selected by `features.multi_agent_v2` | multi_agents_spec.rs, config.schema.json |
| `send_message` does not start a turn, and `followup_task` starts one when the child is idle | multi_agents_spec.rs |
| V2 `wait_agent` reports which agents have mailbox updates and does not return their content | multi_agents_spec.rs |
| A child's final answer is delivered to the parent when it finishes | multi_agents_spec.rs |
| `spawn_agent` takes `agent_type` for a custom agent role | multi_agents_spec.rs, subagents |
| `agents.max_concurrent_threads_per_session` falls back to the backend default when unset. The toolkit sets 3 in `codex/home/config.defaults.toml` | config.schema.json |
| `agents/openai.yaml` with `allow_implicit_invocation: false` stops implicit skill use | build-skills |
<!-- end -->

<!-- if: target=antigravity -->
## Google Antigravity

| Fact the skill relies on | Source |
| --- | --- |
| `invoke_subagent` starts a concurrent session with a role and an initial prompt | subagents |
| `Workspace` is `inherit` (the parent's), `branch` (an isolated Git worktree) or `share` (shared directory storage) | subagents |
| Agents message each other by conversation ID, an idle agent wakes on a message, and a stopped one cannot be woken | subagents |
| A finished subagent sends its result to the parent and pauses | subagents |
| Agent frontmatter `model` takes `inherit`, `flash` or `pro` | subagents |
| Nesting is capped at 10 levels | subagents |
| `run_command` takes `WaitMsBeforeAsync` | Observed in `agy` session transcripts, not in the public docs |

The public Antigravity docs name no call parameters for `invoke_subagent` beyond `Workspace`, and no tools for listing or stopping subagents or background tasks. The skill describes that behaviour without naming tools until a source does.
<!-- end -->
