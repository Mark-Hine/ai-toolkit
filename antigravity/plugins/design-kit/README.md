# design-kit

UI/UX design standards and anti-slop review plugin for Google Antigravity. Packages anti-slop guidelines, spatial and typographic standards, the 5-state completeness law, accessibility requirements, platform fidelity rules, and the `ui-reviewer` specialist subagent.

## Skill

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `design-standards` | `/design-standards` | Interactive UI/UX design standards: anti-slop directives, 8-point spatial grid, typographic scale, 5 states, accessibility, and platform fidelity |

## Rules (`rules/AGENTS.md`)

Consolidated UI/UX design, anti-slop, accessibility, and reviewer delegation guidelines automatically loaded when this plugin is enabled.

## Specialist Subagent (`agents/`)

- `ui-reviewer`: Read-only UI/UX reviewer (`model: pro`). Audits UI diffs, mockups, views, and components against anti-slop directives, Apple HIG, Android Material Design 3, accessibility (WCAG 2.1 AA/AAA), and state completeness without writing code.
