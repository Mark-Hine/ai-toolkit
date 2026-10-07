---
verified: 2026-10-07
sources: inline
---

# Companions

Maintained tools and skills that web-kit names at a specific playbook step. web-kit never installs them. When one is missing, tell the user once how to install it, continue with the bundled standards references, and mark the check it would have made Unverified. The project instructions and the installed house rules win over any companion.

| Companion | Named in | What it adds | Install |
| --- | --- | --- | --- |
| Playwright | run-app, web-verifier | Screenshots at set viewports and colour schemes, and end-to-end tests | The project's own `@playwright/test`, or `npx playwright` with `--channel chrome` so no browser download is needed. Source: https://playwright.dev/docs/screenshots |
| design-kit | feature, ui-reviewer | Tiered design rules, the `DESIGN.md` contract and the capture matrix in `references/capture.md` | A dependency of web-kit, installed with it |
| pr-review | web-reviewer | The deeper React and Next.js grading pack in `references/platforms/react-nextjs.md` | Install the `pr-review` plugin from the same marketplace |
