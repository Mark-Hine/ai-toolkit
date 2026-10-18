---
verified: 2026-09-29
sources: house
---

# Shared personal defaults

## Git

- Follow the repository's documented Git contribution, branch naming and commit message conventions. When these are absent, use the defaults below.
- Use Conventional Commits with the ticket as scope when available, such as `fix(PROJ-123): handle expired sessions`. Use a lowercase imperative subject of at most 72 characters. Add a short body only when needed to explain what changed and why.
- Keep each commit to one logical change. Stage only the intended files or hunks, inspect the staged diff and exclude unrelated changes, secrets and unintended generated files. Run checks appropriate to the change before committing and report any failed or unavailable checks.
- Name branches `<type>/<TICKET>-<slug>`, where `<type>` is the Conventional Commits type of the main change (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `build`, `ci`), for example `feat/MBS-123-barcode-validation`. Without a ticket use `<type>/<slug>`. Branch from the default branch.
- Before committing, check the current branch. If it is `develop`, `main`, `master`, `release/*` or another branch protected by the project, create and switch to a suitably named feature or task branch before committing. Never commit directly to `main` or `master`.
- Find the default branch in this order. The project instructions file, then `git symbolic-ref --short refs/remotes/origin/HEAD` with `origin/` removed, then `machine.md`. Otherwise ask.
- Commit and push only when asked. Never push directly to a protected branch. Do not amend commits, rewrite history or force-push without explicit authorization.
- Do not add AI attribution, a generated-by footer or a Co-Authored-By trailer.

## Work

- Before changing multiple files or dependency versions, state a concise implementation plan. Proceed with work already authorized by the user. Use plan mode when the user wants a planning-only session. Small clear fixes need no separate plan.
- Keep diffs focused. Avoid unrelated refactors, renames and reformatting.
- Model domain choices and related state explicitly when doing so protects an invariant. Keep text conversion at external boundaries and preserve public compatibility during refactors. Use existing verification tools and focused regression checks.
- Decide routine matters and state useful assumptions. Ask about unresolved scope, destructive work, secrets, signing or network-security changes when existing authorization does not cover the action.
- Support build, test and rendering claims with the command and observed result. Cite code as `file:line`. Mark skipped or unavailable checks Unverified and explain failures.
- A hook block is final for that invocation. Do not change tools, encode a command or disable a guard to bypass it.

## Subagents

- Give every subagent a self-contained brief. Include a 1-sentence goal and reason, known facts (`file:line`, error text, branch or SHA, and build or test commands), the exact files or question it owns with explicit exclusions, forbidden actions (no commit, push, merge, branch change, PR, deployment, external message send or data deletion unless requested), the done check and evidence required, a report cap (under 300 words, result first), and the writing style to use.
- When 2 or more subagents run in parallel, tell any writer agent that other agents are active and it must touch only the files it owns, or isolate each writer in its own worktree or workspace.
- Verify every subagent return against its brief and cited `file:line` before reporting it to the user or starting dependent work. When a research-tier agent returns thin or wrong work, escalate to the review tier rather than retrying the same prompt on the research tier.

