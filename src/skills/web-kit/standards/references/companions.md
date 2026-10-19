---
verified: 2026-10-07
sources: inline
---

# Companions

Maintained tools and skills that web-kit names at a specific playbook step. web-kit never installs them. When one is missing, tell the user once how to install it, continue with the bundled standards references, and mark the check it would have made Unverified. The project instructions and the installed house rules win over any companion.

| Companion | Named in | What it adds | Install |
| --- | --- | --- | --- |
| Playwright | run-app, web-verifier | Screenshots at set viewports and colour schemes, and end-to-end tests | The project's own `@playwright/test`, or `npx playwright` with `--channel chrome` so no browser download is needed. Source: https://playwright.dev/docs/screenshots |
| Playwright CLI | web-verifier, run-app | Drives a journey in a real browser through accessibility snapshot refs, using fewer tokens than the MCP server. Needs Playwright 1.62 or later | The project's own `@playwright/test` 1.62 or later, run as `npx --no-install playwright cli` so nothing downloads. Source: https://github.com/microsoft/playwright-cli |
| Playwright Test Agents | feature follow-up | Planner, generator and healer agents that turn a journey into a Playwright spec. Adding them is its own ticket, like any new test framework | `npx playwright init-agents --loop=<agent>`, with the value for your coding agent from that page, rerun after each Playwright upgrade. Source: https://playwright.dev/docs/test-agents |
| design-kit | feature, ui-reviewer | Tiered design rules, the `DESIGN.md` contract and the capture matrix in `references/capture.md` | A dependency of web-kit, installed with it |
| pr-review | web-reviewer | The deeper React and Next.js grading pack in `references/platforms/react-nextjs.md` | Install the `pr-review` plugin from the same marketplace |
