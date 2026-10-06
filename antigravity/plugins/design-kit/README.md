# design-kit

Tiered UI design rules for Google Antigravity, with the sources behind them and a reviewer that grades against them.

The rules live in `shared/guidance/design-standards.md`, installed as `~/.gemini/config/guidance/design-standards.md`. Every rule has a stable ID, a tier and a source key. `T1` rules trace to Apple HIG, Material 3, WCAG 2.2, Android developer docs or MDN and grade Blocker or Major. `T2` rules are house preference with a named origin and grade Nit unless a project opts in by ID.

## Skills

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `design-iterate` | `/design-iterate` | The design playbook. It reads or drafts the project's `DESIGN.md` contract, classifies each change as use, extend or change, captures before and after, offers rendered options on a blind board for open requests and brand marks, stops for the user's pick, then records the decision and implements through tokens. Its references are `design-contract.md`, `capture.md`, `options.md`, `brand-marks.md` and `companions.md` |
| `design-standards` | `/design-standards` | The procedure for building or reviewing UI against the rules, plus `references/sources.md`, `references/rationale.md` and `references/platform-apis.md` |

## Optional companions

design-kit uses these when they are installed and never installs them. `references/companions.md` gives the install line for each agent and the reasons other skills are not recommended.

- Anthropic's `frontend-design` adds aesthetic direction for web work. The project's `DESIGN.md` wins over its advice.
- Google's `@google/design.md` CLI lints, diffs and exports `DESIGN.md` through `npx`.
- Playwright renders the capture matrix, using an installed Chrome through `--channel chrome`.

## Rules (`rules/AGENTS.md`)

Points at the installed rule file and names the reviewer to delegate to.

## Specialist subagent (`agents/`)

- `ui-reviewer`: read-only reviewer (`model: pro`). Grades UI diffs, mockups, views and components against the rule file and the project's `DESIGN.md` contract, cites the rule ID and source key in every finding, and reports screen-state coverage, accessibility and contract changes. Writes no code.
