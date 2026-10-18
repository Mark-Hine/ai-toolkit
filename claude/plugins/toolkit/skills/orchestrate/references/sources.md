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


