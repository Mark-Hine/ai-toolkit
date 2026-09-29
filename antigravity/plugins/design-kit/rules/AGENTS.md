# Design rules

- The design rules are in `~/.gemini/config/guidance/design-standards.md`. Every rule has an ID, a tier and a source key. Read it before creating or changing UI screens, components or design systems.
- The `design-standards` skill holds the sources, the rationale for house rules and the platform APIs per rule.
- Delegate UI diffs, component audits and screen reviews to `ui-reviewer` through `invoke_subagent`. Give it a bounded task and re-check its findings before reporting them.
