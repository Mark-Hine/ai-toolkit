# design-kit eval baseline, 2026-10-06

This is the score of design-kit 1.3.1 on its eval suite before the contract, `iterate` and second-opinion work. Later runs compare against it.

## Setup

| Item | Value |
| --- | --- |
| Plugin | design-kit 1.3.1 (the `standards` skill and `ui-reviewer`) |
| Claude Code | 2.1.290 |
| Agent and judge model | `claude-sonnet-5-5` |
| Runs | 3 per case in each arm, with and without the plugin |
| Cost and time | $2.24 list price, 149 s at concurrency 4 |

The command was:

```bash
claude plugin eval claude/plugins/design-kit --scaffold --trust-plugin --allow-tools Write Edit \
  --model claude-sonnet-5-5 --judge-model claude-sonnet-5-5 --no-publish -j 4 --threshold 0
```

## Scores

| Case | With | Without | Δ | Failing graders with the plugin |
| --- | --- | --- | --- | --- |
| `logo-audit` | 0.27 | 0.27 | 0.00 | no concepts, no rendered sheet and no pick in 3 of 3 runs. The original mark was overwritten in 2 of 3 |
| `pill-buttons` | 0.40 | 0.47 | -0.07 | no before and after board and no approval request in 3 of 3. `DESIGN.md` unread in 3 of 3 |
| `use-tweak` | 0.87 | 0.93 | -0.07 | `DESIGN.md` unread in 2 of 3 |
| `pricing-section` | 0.86 | 0.86 | 0.00 | `DESIGN.md` unread in 3 of 3 |
| `compose-banner` | 0.83 | 0.83 | 0.00 | `DESIGN.md` unread in 3 of 3 |
| `trigger-header` | 0.00 | 0.00 | 0.00 | no design skill fired |

The mean Δ is -0.02, so design-kit 1.3.1 does not change behaviour on these requests. `trigger-header` scores 0 because the `iterate` skill it looks for does not exist yet.

## Findings

The logo request reproduces the reported failure. The agent edits or replaces the mark directly, with no render of the current state, no alternatives and no question to the user.

Shared changes go unannounced. Asked for pill-shaped buttons, no run showed a comparison or asked before changing every button, and none read the contract that reserves the full radius for avatars and status dots.

The small fixtures keep their tokens even without the plugin. Every run used existing spacing tokens, added no literals and left the token files intact. These cases guard against regressions, and the contract and approval graders carry the measurement.

## Limits

Eval runs load only the plugin, with no `~/.claude/rules`, home `CLAUDE.md` or project instructions. So these scores cannot show the effect of the rule file, the path-scoped rule, the home routing or a project's `@DESIGN.md` import. A manual comparison with `claude -p` measures those after the feature work lands.

Three runs per arm give a coarse signal. A difference of one run moves a case by 0.33 on a single grader.
