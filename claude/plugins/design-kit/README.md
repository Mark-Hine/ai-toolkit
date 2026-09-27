# design-kit

UI/UX design standards and anti-slop review plugin for Claude Code. Packages anti-slop guidelines, spatial and typographic standards, the 5-state completeness law, accessibility requirements, platform fidelity rules, and the `ui-reviewer` specialist subagent.

## Skill

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `standards` | `/design-kit:standards` | Interactive UI/UX design standards: anti-slop directives, 8-point spatial grid, typographic scale, 5 states, accessibility, and platform fidelity |

## Specialist Subagent (`agents/`)

- `ui-reviewer`: Read-only UI/UX reviewer (`model: opus`, `effort: high`). Audits UI diffs, mockups, views, and components against anti-slop directives, Apple HIG, Android Material Design 3, accessibility (WCAG 2.1 AA/AAA), and state completeness without writing code.
