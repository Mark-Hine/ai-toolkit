# design-kit

Tiered UI design rules for Claude Code, with the sources behind them and a reviewer that grades against them.

The rules themselves live in `shared/guidance/design-standards.md`, installed as `~/.claude/rules/design-standards.md` by `claude/install.sh`. Every rule has a stable ID, a tier and a source key. `T1` rules trace to Apple HIG, Material 3, WCAG 2.2, Android developer docs or MDN and grade Blocker or Major. `T2` rules are house preference with a named origin and grade Nit unless a project opts in by ID.

## Skills

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `iterate` | `/design-kit:iterate` | The design playbook. It reads or drafts the project's `DESIGN.md` contract, classifies each change as use, extend or change, captures before and after, offers rendered options on a blind board for open requests and brand marks, stops for the user's pick, then records the decision and implements through tokens. Its references are `design-contract.md`, `capture.md`, `options.md`, `brand-marks.md` and `companions.md`. `scripts/board.py` builds the strips, sheets and board in one command, so runs read only compact strips. Pass `quick` for one round without a second opinion |
| `standards` | `/design-kit:standards` | The procedure for building or reviewing UI against the rules, plus `references/sources.md` (every source key with URL and verified date), `references/rationale.md` (why each T2 rule exists) and `references/platform-apis.md` (the Compose, SwiftUI and CSS APIs per rule) |

## Specialist subagent (`agents/`)

- `ui-reviewer`: read-only reviewer (`model: opus`, `effort: high`). Grades UI diffs, mockups, views and components against the rule file and the project's `DESIGN.md` contract, cites the rule ID and source key in every finding, and reports screen-state coverage, accessibility and contract changes. Writes no code.

## Optional companions

design-kit uses these when they are installed and never installs them. `references/companions.md` gives the install line for each agent and the reasons other skills are not recommended.

- Anthropic's `frontend-design` adds aesthetic direction for web work. The project's `DESIGN.md` wins over its advice.
- Google's `@google/design.md` CLI lints, diffs and exports `DESIGN.md` through `npx`.
- Playwright renders the capture matrix, using an installed Chrome through `--channel chrome`.

## Plugins-only installs

Without the dotfiles layer the rule file is absent. The skill and the reviewer then grade against the Tier 1 sources in `references/sources.md` and say so.

## Evals

`evals/` holds a `claude plugin eval` suite. Each case copies a small fixture from `evals/_fixtures/` into an empty workspace: a web site with a `DESIGN.md` contract and tokens, or a Compose module with a theme. The cases check two things. Open design requests should produce rendered options and stop for a pick, and smaller changes should keep to the contract's tokens and components.

| Case | Request | What passes |
| --- | --- | --- |
| `logo-audit` | Audit and improve a generic logo | The original mark is kept, three to five concepts and a rendered sheet are created, and the reply asks for a pick |
| `use-tweak` | Give the feature cards more room | More space comes from existing spacing tokens, with no literals and no token change |
| `pill-buttons` | Make all buttons pill-shaped | The radius shared with cards and inputs is untouched, and the reply asks approval of a before and after board |
| `pricing-section` | Add a pricing section | No new stylesheet, inline style, colour, font or token |
| `contract-conflict` | Make the feature card titles clay | No clay or new colour is applied, and the reply names the contract conflict and asks first |
| `trigger-header` | Tweak the header colours | The design-kit iterate skill fires |
| `compose-banner` | Add a Compose promo banner | No literal colour, sp or dp, and the theme supplies colour and type |

Run the suite from the repository root. The scaffolds are this repository's own scripts, and runs need write tools to change the fixture:

```bash
claude plugin eval claude/plugins/design-kit --scaffold --trust-plugin --allow-tools Write Edit \
  --model claude-sonnet-5-5 --judge-model claude-sonnet-5-5 --no-publish
```

Eval runs load only this plugin, without `~/.claude/rules` or any `CLAUDE.md`, so they measure the skills and agents but not the rule files. Results go to `evals/results/`, which git ignores. Recorded baselines live in `docs/evals/`.
