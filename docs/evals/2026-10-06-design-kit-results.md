# design-kit eval results, 2026-10-06

design-kit 1.7.1 lifts the suite's mean Δ against no plugin from -0.02 to +0.41. Logo requests now produce an audit, rendered concepts and a pick. Shared changes now get a before and after board and an approval request. The baseline is in `2026-10-06-design-kit-baseline.md`.

## Setup

| Item | Value |
| --- | --- |
| Plugin | design-kit 1.7.1, after PRs #37 to #42 |
| Claude Code | 2.1.290 |
| Agent and judge model | `claude-sonnet-5-5` |
| Runs | 3 per case in each arm, with and without the plugin |
| Cost and time | $3.14 list price, 212 s at concurrency 4 |

The command matched the baseline's.

## Scores

| Case | 1.3.1 baseline, with | 1.7.0, with | 1.7.1, with | 1.7.1, without | Δ at 1.7.1 |
| --- | --- | --- | --- | --- | --- |
| `logo-audit` | 0.27 | 0.40 | 1.00 | 0.20 | +0.80 |
| `pill-buttons` | 0.40 | 0.53 | 1.00 | 0.40 | +0.60 |
| `trigger-header` | 0.00 | 1.00 | 1.00 | 0.00 | +1.00 |
| `use-tweak` | 0.87 | 0.93 | 1.00 | 0.87 | +0.13 |
| `pricing-section` | 0.86 | 0.86 | 0.81 | 0.86 | -0.05 |
| `compose-banner` | 0.83 | 0.83 | 0.83 | 0.83 | 0.00 |
| Mean Δ | -0.02 | +0.21 | | | +0.41 |

At 1.7.1, every logo run kept the original mark, drew three concepts as separate SVGs, wrote a board and asked for a pick. Every pill-button run left the shared radius alone, read `DESIGN.md`, built the board and asked for approval.

PR #42 changed two `logo-audit` graders between the 1.7.0 and 1.7.1 runs.
- `asks-pick` had failed a run that correctly kept its blind board undescribed.
- `not-too-many` had counted reversed versions as extra concepts.

The change did not inflate the no-plugin score. The 1.7.1 no-plugin arm, graded the new way, scores 0.20, close to the baseline's 0.27, because no run without the plugin offers options.

## What changed between the runs

The 1.7.0 rerun showed two gaps, and #42 fixed both.
- **Logo requests.** The skill fired and audited, but stopped to ask "refine or redesign" before drawing. An open request now puts a refinement and redesign concepts on one board.
- **Shared changes.** "Make all buttons pill-shaped" did not trigger the skill. The trigger text now names shared changes. A specified change now builds its board before asking for approval.
- **Stalled runs.** Runs that lacked anchors, consent, a reference file or a renderer stopped to ask. They now carry on and report what they could not check.

## A short-turn comparison

A temporary case, not committed, asked "Make the accent warmer." of the same fixture, three runs in each arm.
- **Without the plugin: 0.00.** Every run rewrote the shared accent token, with no board and no question. This reproduces the continuity failure that started this work.
- **With 1.7.1: 1.00.** The skill fired, the token stayed unchanged, a before and after board was written, and the user was asked to approve.

## Pilots in a real install

Two pilots ran `claude -p --plugin-dir claude/plugins/design-kit` on copies of the web fixture with Sonnet 5.5 and design-kit 1.7.0. Each used:
- the user's own configuration, with the new rule file, the new routing and `design-assets.md` linked
- a project `CLAUDE.md` that imports `DESIGN.md`
- Bash allowed for Playwright, Node and the Antigravity CLI

**Logo, 40 turns, $0.81:**
1. Rendered the current mark on a test sheet and audited it from the image. The audit found a generic letter tile, a live Arial `<text>` element, a mark that turns into a solid block in one colour, and a tile that crosses the Android safe zone.
2. Drew three concepts tied to the product: a drawn serif L matching the wordmark, a tile with an accountant's double rule, and a disc with a decimal dot. Each concept had a reversed version.
3. Checked B at 16 px, found its rules merging, and thickened them.
4. Rendered a blind board and got a second opinion from Gemini 3.1 Pro through `agy`.
5. Checked the second opinion's defects against the images and rejected one it could not confirm. Its preference stayed closed until the pick.
6. Changed no project file.

**Accent, 5 turns, $0.21:**
1. Classified the accent as a shared token under the project's SYS-2 opt-in.
2. Noted that nothing references the accent yet.
3. Built a before and after board with two warmer options and asked for approval.

The skill did not fire. The imported `DESIGN.md`, the opt-in line and the rule file produced the right behaviour without it.

Two observations from the accent pilot:
- The path-scoped rule did not load, because the agent read `tokens.css` with `cat` through Bash. Path-scoped rules load only when the Read, Write or Edit tool touches a file.
- The board landed in the session scratchpad instead of `.design/iterations/`, because only the skill names that folder.

## Second opinion

The `gemini` CLI no longer signs in on this machine, because Google retired its free individual tier for that client. The Antigravity CLI worked instead: `agy -p` in plan mode with `--model gemini-3.1-pro-high` and a JSON schema. On a three-option board it took 77 s and found defects that Claude's own run had missed. `claude -p` in plan mode returned the same structured output from the board. Codex is not installed here, so its call stays Unverified.

## Limits

- One model and three runs per arm give a coarse signal. One run moves a single grader by 0.33.
- Eval runs have no Bash or web access and sometimes cannot read the plugin's reference files, so they exercise the fallback path. The pilots cover rendering and the second opinion.
- Eval runs load only the plugin, so they cannot measure the rule file, the routing, the path rule or a project's `@DESIGN.md` import. The pilots show those working but had no controlled arm without them.
- `pricing-section` and `compose-banner` never read `DESIGN.md`, with or without the plugin. The skill does not fire for routine additions within the system, by design, and in a real project the import supplies the contract. The -0.05 on `pricing-section` was one run that wrote a literal. Three reruns with kept transcripts showed no skill call and no literal.
- Codex and Antigravity runtime behaviour is Unverified. Their validators cover structure only.

## Follow-ups at 1.7.2

A test of `iterate` with fresh Opus agents, on a clone of a private web project, led to #44. This section scores its follow-ups and the new `contract-conflict` case. The run used three runs per arm on Sonnet 5.5 with Claude Code 2.1.291, and cost $3.48 over 227 s.

| Case | 1.7.2, with | 1.7.2, without | Δ |
| --- | --- | --- | --- |
| `contract-conflict` (new) | 1.00 | 0.25 | +0.75 |
| `logo-audit` | 1.00 | 0.20 | +0.80 |
| `pill-buttons` | 1.00 | 0.40 | +0.60 |
| `trigger-header` | 1.00 | 0.00 | +1.00 |
| `use-tweak` | 1.00 | 0.87 | +0.13 |
| `pricing-section` | 0.86 | 0.86 | 0.00 |
| `compose-banner` | 0.83 | 0.83 | 0.00 |
| Mean Δ | | | +0.47 |

`contract-conflict` behaved consistently in each arm:
- **With the plugin**, every run fired the skill, named the conflict with the contract, built a board and left the titles unchanged.
- **Without the plugin**, every run applied the reserved colour.

The wider trigger left the routine cases alone. `pricing-section` and `compose-banner` still match the no-plugin arm, as they did at 1.7.1.

The real-project test also showed two things:
- **A full logo loop on a real site.** The request went from rendered test sheets to a second opinion through `agy`, in 90 turns at $3.63 on Opus. It then stopped for the pick, with no project file changed.
- **A conflicting request refused without the skill.** The project's instructions and the rule file refused it correctly even before the trigger change, but no board was drawn.

## After merging

Run `claude/install.sh` so `~/.claude/rules/design-assets.md` is linked. Then update the installed design-kit plugin so new sessions get `iterate`. The machine file on this machine already names `agy` as the second-opinion CLI.
