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

