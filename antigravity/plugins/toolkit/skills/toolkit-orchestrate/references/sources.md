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
