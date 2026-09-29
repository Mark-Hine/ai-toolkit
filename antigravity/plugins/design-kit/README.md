# design-kit

Tiered UI design rules for Google Antigravity, with the sources behind them and a reviewer that grades against them.

The rules live in `shared/guidance/design-standards.md`, installed as `~/.gemini/config/guidance/design-standards.md`. Every rule has a stable ID, a tier and a source key. `T1` rules trace to Apple HIG, Material 3, WCAG 2.2, Android developer docs or MDN and grade Blocker or Major. `T2` rules are house preference with a named origin and grade Nit unless a project opts in by ID.

## Skill

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `design-standards` | `/design-standards` | The procedure for building or reviewing UI against the rules, plus `references/sources.md`, `references/rationale.md` and `references/platform-apis.md` |

## Rules (`rules/AGENTS.md`)

Points at the installed rule file and names the reviewer to delegate to.

## Specialist subagent (`agents/`)

- `ui-reviewer`: read-only reviewer (`model: pro`). Grades UI diffs, mockups, views and components against the rule file, cites the rule ID and source key in every finding, and reports screen-state coverage and accessibility. Writes no code.
