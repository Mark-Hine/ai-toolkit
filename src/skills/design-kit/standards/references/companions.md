---
verified: 2026-10-06
sources:
  - https://github.com/anthropics/skills/tree/main/skills/frontend-design
  - https://github.com/vercel-labs/skills
  - https://github.com/google-labs-code/design.md
  - https://playwright.dev/docs/screenshots
  - https://github.com/figma/mcp-server-guide
  - https://github.com/pbakaus/impeccable
  - https://github.com/vercel-labs/agent-skills
  - https://github.com/google-labs-code/stitch-skills
  - https://github.com/vercel-labs/skills/issues/488
---

# Companions

Maintained tools and skills that design-kit uses when they are present. design-kit never installs them. When one is missing, tell the user once how to install it and carry on with the bundled guidance.

## Recommended

| Companion | What it adds | Install |
| --- | --- | --- |
| Anthropic `frontend-design` | Aesthetic direction for web work: grounding in the product's subject, a plan reviewed against the brief before building, and a list of the looks models default to | Claude Code: `/plugin install frontend-design@claude-plugins-official`. Codex: `npx skills add anthropics/skills --skill frontend-design -a codex`. Antigravity: the same with `-a antigravity` |
| Google `@google/design.md` | Lints, diffs and exports `DESIGN.md` | Nothing to install. It runs through `npx @google/design.md` when Node is present |
| Playwright | Renders the capture matrix in `capture.md` | The project's own `@playwright/test`, or `npx playwright` with `--channel chrome` |

### The precedence guard for frontend-design

frontend-design tells an agent to create a compact token system and take aesthetic risk. That is right for a blank page and wrong for a product that already has a system. So in a project with a `DESIGN.md`:

- Read the token system from `DESIGN.md` instead of creating one.
- Apply its advice only where the contract leaves a choice open, such as the layout of a new section or the concept for a new mark.
- Treat any change it suggests to a shared token, component or brand asset as a change under SYS-2, which needs a before and after board and the user's approval.
- Never let it override a T1 rule.

## Optional

| Companion | Use it when | Install |
| --- | --- | --- |
| Figma | The project's tokens live in Figma variables. Read them to draft `DESIGN.md` | Claude Code: `/plugin install figma@claude-plugins-official`. Other agents connect Figma's MCP server as its guide describes |
| Anthropic `playground` | The user wants live controls to tune spacing, radius or colour before choosing | Claude Code only: `/plugin install playground@claude-plugins-official` |

## Considered and not recommended

| Skill | Why not by default |
| --- | --- |
| Impeccable | Strong web critique and a deterministic detector, but it downloads a binary engine, writes project hooks and keeps its own `DESIGN.md` convention, which would compete with the contract |
| Vercel `web-design-guidelines` | It fetches its rules from GitHub on every run, so the instructions it follows are unpinned and unreviewed |
| Google `stitch-skills` | They need the Stitch MCP server and an API key. Use them only in a project designed in Stitch |
| Paid or closed design packs | Their instructions or the services behind them cannot be reviewed |
| Logo generators that call image APIs | They send the brief to third-party services and return raster art instead of a master that can be constructed and tested |

Install counts on skills.sh come from anonymous CLI telemetry, and an open issue reports inflated counts, so they say nothing about quality.
