# design-kit

Tiered UI design rules for Claude Code, with the sources behind them and a reviewer that grades against them.

The rules themselves live in `shared/guidance/design-standards.md`, installed as `~/.claude/rules/design-standards.md` by `claude/install.sh`. Every rule has a stable ID, a tier and a source key. `T1` rules trace to Apple HIG, Material 3, WCAG 2.2, Android developer docs or MDN and grade Blocker or Major. `T2` rules are house preference with a named origin and grade Nit unless a project opts in by ID.

## Skill

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `standards` | `/design-kit:standards` | The procedure for building or reviewing UI against the rules, plus `references/sources.md` (every source key with URL and verified date), `references/rationale.md` (why each T2 rule exists) and `references/platform-apis.md` (the Compose, SwiftUI and CSS APIs per rule) |

## Specialist subagent (`agents/`)

- `ui-reviewer`: read-only reviewer (`model: opus`, `effort: high`). Grades UI diffs, mockups, views and components against the rule file, cites the rule ID and source key in every finding, and reports screen-state coverage and accessibility. Writes no code.

## Plugins-only installs

Without the dotfiles layer the rule file is absent. The skill and the reviewer then grade against the Tier 1 sources in `references/sources.md` and say so.
