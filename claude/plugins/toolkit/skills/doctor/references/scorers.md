---
verified: 2026-11-23
sources: house
---

# Doctor scorers

Each area scores 0 to 10. A measured area maps collector metrics to a score with the bands below. A judged area is the mean of the sampled sessions' rubric scores, times 10. An area with both takes the mean of the two.

## Areas and weights

| Area | Weight | Source |
|---|---|---|
| Tool-call efficiency | 0.20 | Measured and judged |
| Test value | 0.15 | Measured and judged |
| Verbosity and style | 0.15 | Measured and judged |
| Procedure compliance | 0.15 | Judged |
| Context and memory | 0.15 | Measured |
| Connectors and housekeeping | 0.10 | Measured |
| Subagent use | 0.10 | Measured |

## Measured bands

Score each metric 10, 7, 4 or 1 by the band it falls in, then average the metrics in the area. The noise band is the change that counts as no change between 2 runs.

| Area | Metric (collector key) | 10 | 7 | 4 | 1 | Noise band |
|---|---|---|---|---|---|---|
| Tool-call efficiency | `tool_error_rate` | under 0.01 | under 0.02 | under 0.04 | 0.04 or more | 0.005 |
| Tool-call efficiency | `shell_for_read_share` | under 0.03 | under 0.08 | under 0.15 | 0.15 or more | 0.02 |
| Tool-call efficiency | `polling_loop` per 1,000 tool calls | under 1 | under 5 | under 15 | 15 or more | 2 |
| Tool-call efficiency | `hook_block` plus `worktree_guard` errors per 1,000 tool calls | under 1 | under 3 | under 8 | 8 or more | 1 |
| Test value | `gradle_unfiltered_share` | under 0.15 | under 0.30 | under 0.50 | 0.50 or more | 0.05 |
| Test value | `tests_per_100_production_lines` | 1 to 4 | 4 to 8 | 8 to 15, or under 1 | over 15, or 0 with code written | 1 |
| Verbosity and style | `median_words` | under 180 | under 260 | under 350 | 350 or more | 30 |
| Verbosity and style | `dashes_per_1000_words` plus `semicolons_per_1000_words` | under 0.5 | under 2 | under 6 | 6 or more | 0.3 |
| Verbosity and style | `share_ending_in_offer` | under 0.03 | under 0.08 | under 0.15 | 0.15 or more | 0.02 |
| Context and memory | `always_loaded_chars` | under 15,000 | under 22,000 | under 30,000 | 30,000 or more | 500 |
| Context and memory | `largest_memory_index_bytes` | under 3,000 | under 8,000 | under 16,000 | 16,000 or more | 500 |
| Context and memory | `compactions` per session | under 0.1 | under 0.25 | under 0.5 | 0.5 or more | 0.05 |
| Connectors and housekeeping | `mcp_auth` errors | 0 | under 5 | under 20 | 20 or more | 2 |
| Connectors and housekeeping | `eval_leftover_folders` | under 10 | under 50 | under 200 | 200 or more | 5 |
| Connectors and housekeeping | Servers with the same product called in the window, from `mcp_calls_by_server` | 1 each | 2 | 3 | 4 or more | 0 |
| Subagent use | `spawns_without_model` share of `spawns` | 0 | under 0.02 | under 0.10 | 0.10 or more | 0.01 |
| Subagent use | `agent_type_missing` errors | 0 | under 3 | under 10 | 10 or more | 1 |

## Judged rubrics

Score each sampled session 1.0, 0.75, 0.5, 0.25 or 0 on each rubric. Record `insufficient_evidence` when the session does not exercise the rubric, and leave that row out of the mean.

### Efficiency
- 1.0: The session reached its goal with no repeated or abandoned approach.
- 0.5: The session reached its goal after one avoidable detour, such as a blocked command retried in another form, a file read 3 or more times, or a search repeated.
- 0: The session spent most of its calls on retries, polling or work that it then discarded.

Look for a failed call followed by the same call, a dedicated tool replaced by a shell command after an error, an MCP failure replaced by `curl` or a CLI, and a subagent re-sent the same brief.

### Test value
- 1.0: Each test added checks one behaviour that the change could break, and test runs were filtered while iterating.
- 0.5: Some tests repeat another test with a trivially different input, mirror the implementation field by field, or the full suite ran more than once.
- 0: Most tests added would pass for a wrong implementation, or tests were loosened or deleted to go green.

### Verbosity and style
- 1.0: Replies lead with the answer, match the length to the question and follow `writing-style.md`.
- 0.5: Replies are correct but carry a recap, a preamble, unneeded headings or bold, or run about twice the needed length.
- 0: The person had to ask for a shorter or clearer answer.

### Procedure compliance
- 1.0: The session followed the playbook, rule or skill that applied, including its review and evidence steps.
- 0.5: The session skipped one required step, such as the reviewer agent, the quoted test run or the model pin on a subagent, or it did not load a skill that covered the task.
- 0: The session ignored the applicable playbook, or claimed a check passed without running it.
