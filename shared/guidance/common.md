# Shared personal defaults

## Git

- Follow the repository's documented Git contribution, branch naming and commit message conventions. When these are absent, use the defaults below.
- Use Conventional Commits with the ticket as scope when available, such as `fix(PROJ-123): handle expired sessions`. Use a lowercase imperative subject of at most 72 characters. Add a short body only when needed to explain what changed and why.
- Keep each commit to one logical change. Stage only the intended files or hunks, inspect the staged diff and exclude unrelated changes, secrets and unintended generated files. Run checks appropriate to the change before committing and report any failed or unavailable checks.
- Before committing, check the current branch. If it is `develop`, `main`, `master`, `release/*` or another branch protected by the project, create and switch to a suitably named feature or task branch before committing.
- Commit and push only when asked. Never push directly to a protected branch. Do not amend commits, rewrite history or force-push without explicit authorization.
- Do not add AI attribution, a generated-by footer or a Co-Authored-By trailer.

## Work

- Before changing multiple files or dependency versions, state a concise implementation plan. Proceed with work already authorized by the user. Use plan mode when the user wants a planning-only session. Small clear fixes need no separate plan.
- Keep diffs focused. Avoid unrelated refactors, renames and reformatting.
- Decide routine matters and state useful assumptions. Ask about unresolved scope, destructive work, secrets, signing or network-security changes when existing authorization does not cover the action.
- Support build, test and rendering claims with the command and observed result. Cite code as `file:line`. Mark skipped or unavailable checks Unverified and explain failures.
- A hook block is final for that invocation. Do not change tools, encode a command or disable a guard to bypass it.
