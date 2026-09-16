# Personal defaults

Read `~/.codex/machine.md` for local tool and device facts. If CODEX_HOME is set, use that directory instead of `~/.codex` for these personal files. Read `guidance/writing-style.md` there for responses, documents, PR text and commit bodies. These are explicit file-reading instructions, not automatic imports.

## Git

- Follow the repository's documented Git contribution, branch naming and commit message conventions. When these are absent, use the defaults below.
- Use Conventional Commits with the ticket as scope when available, such as `fix(PROJ-123): handle expired sessions`. Use a lowercase imperative subject of at most 72 characters. Add a short body only when needed to explain what changed and why.
- Keep each commit to one logical change. Stage only the intended files or hunks, inspect the staged diff and exclude unrelated changes, secrets and unintended generated files. Run checks appropriate to the change before committing and report any failed or unavailable checks.
- Before committing, check the current branch. If it is `develop`, `main`, `master`, `release/*` or another branch protected by the project, create and switch to a suitably named feature or task branch before committing.
- Commit and push only when asked. Never push directly to a protected branch. Do not amend commits, rewrite history or force-push without explicit authorization.
- Do not add AI attribution, a generated-by footer or a Co-Authored-By trailer.

## Work

- When changing the ai-toolkit setup, mirror shared changes between `codex/` and `claude/` in the same task, adapting paths and mechanisms for each agent. Preserve intentional agent-specific differences, including the separate writing styles. State any change that is not mirrored and why.
- Before changing multiple files or dependency versions, state a concise implementation plan. Proceed with work already authorized by the user. Use `/plan` when the user wants a planning-only session. Small clear fixes need no separate plan.
- Keep diffs focused. Avoid unrelated refactors, renames and reformatting.
- Decide routine matters and state useful assumptions. Ask about unresolved scope, destructive work, secrets, signing or network-security changes when existing authorization does not cover the action.
- Support build, test and rendering claims with the command and observed result. Cite code as `file:line`. Mark skipped or unavailable checks Unverified and explain failures.
- A hook block is final for that invocation. Do not change tools, encode a command or disable a guard to bypass it.

## Android and Kotlin

- Read matching guidance before editing. `guidance/android/kotlin-style.md` applies to Android `.kt` and `.kts` files. `compose.md` applies to Compose screens and components. `ui-events.md` applies to ViewModels and UI event collectors. `testing.md` applies to tests and journeys. The `paths` headers document scope and are not automatically loaded by Codex.
- Use `$android-feature`, `$android-bugfix`, `$android-uplift-deps`, `$android-run-app` and `$android-standards` when relevant. Use `$pr-review` for the formal JSON and Markdown PR-review deliverable.
- Project AGENTS.md and applicable personal rules take precedence over skills, subject to the user's current instructions. Read a project's CLAUDE.md if AGENTS.md is absent during migration, and read matching project `.claude/rules` where no Codex equivalent exists.
- Discover optional skills before using them. Use `using-chrisbanes-skills`, `android-cli` and official Android skills when installed. Otherwise use bundled standards references, current official documentation and installed Android SDK tools. Do not fabricate a missing CLI or skill.
- Delegate current platform research to `android-researcher`, non-trivial Android diff review to `android-reviewer`, and build/test/device evidence collection to `android-verifier`. Give each a bounded task and re-check findings before reporting them. If custom agents are unavailable, perform the work inline and disclose the limitation.
- The reviewer pins `gpt-6-astra` with high reasoning. Researcher and verifier pin `gpt-5.6-terra` with medium reasoning. When manually spawning these roles, pass those model and effort settings explicitly and provide their installed agent instructions. Do not pass Claude model aliases.
