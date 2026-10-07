# web-kit

Claude Code plugin for React, Next.js and TypeScript web work. Install with `/plugin marketplace add Mark-Hine/ai-toolkit` then `/plugin install web-kit@ai-toolkit`.

| Component | Use |
| --- | --- |
| `/web-kit:feature PROJ-123 <summary>` | Feature or feature-change playbook: intake, pattern discovery, plan, implement, tests, browser check, review, commit |
| `/web-kit:bugfix PROJ-123 <symptom>` | Reproduce (test or browser), root cause, minimal fix, regression test, review, commit |
| `/web-kit:run-app <route>` | Start the dev server, wait for it, and screenshot routes with Playwright at phone and desktop widths |
| `standards` skill | Index of React, Next.js, TypeScript, Testing Library, Playwright and MDN docs, source anchors, companions and a per-repo `CLAUDE.md` template, preloaded into the researcher and verifier |
| `web-reviewer` agent | Read-only diff review, runs the type check, lint and targeted tests, grades Blocker/Major/Nit, checks effective config (lockfile versions, variables that reach the browser) |
| `web-researcher` agent | Read-only research on framework guidance and package versions. Its shell is limited by guard-kit to package queries such as `npm view` and `npm outdated` |
| `web-verifier` agent | Runs tests, type checks, lint and Playwright specs and screenshots. Its shell is limited by guard-kit to those commands, without autofix or snapshot-update flags |
| guard-kit dependency | The PreToolUse guard lives in the `guard-kit` plugin, which this plugin depends on |

Playbooks read repo facts (package manager, router, scripts, test runners, dev URL) from the project's `CLAUDE.md`. Start one from `skills/standards/references/project-claude-md-template.md`. Machine facts come from `~/.claude/machine.md`. Path-scoped TypeScript, React and testing rules install separately with `claude/install.sh`. Playwright drives the captures through the installed Chrome. Optional companions are listed in `skills/standards/references/companions.md`.
