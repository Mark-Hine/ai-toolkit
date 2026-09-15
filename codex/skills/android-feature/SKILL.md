---
name: android-feature
description: "Feature or feature-change playbook for Android apps: intake, pattern discovery, plan, implement, tests, emulator check, review, commit."
---

Read the project AGENTS.md and applicable global guidance first. If AGENTS.md is absent, read CLAUDE.md as migration fallback. Discover optional skills before invoking them. If `using-chrisbanes-skills`, `android-cli`, or an official Android skill is unavailable, use the bundled android-standards references and current official documentation. Do not invent commands or claim that an absent skill ran. Use installed Android SDK tools when the optional Android CLI is missing. Commit and push only when the user has requested that action.


# Feature work: the user request

Repo facts (modules, build/test commands, design-system names, app id) come from the project's `AGENTS.md`. Never guess them.

1. **Intake.** If an Atlassian MCP tool is available, fetch the Jira ticket and quote its acceptance criteria; otherwise
   restate the goal in three bullets plus an out-of-scope list. Branch `feature/<ticket>-<slug>` off the default branch.
2. **Discover the pattern.** Use an explorer subagent to find the closest existing screen or flow: its Activity/Fragment or
   Compose entry point, ViewModel, repository/use case, DI wiring, and tests. Note whether it is XML or Compose.
   For a *modify* task also map every caller of the code you will change.
3. **Consult skills and references.** Route through `using-chrisbanes-skills`; load the compose-*/kotlin-* skills it names.
   Ask `android-researcher` only where guidance may have moved (navigation, insets, permissions, target-SDK behaviour).
4. **Plan.** Files to add or change, state model (`UiState` sealed interface, StateFlow), where data code goes,
   DI wiring, test list, device checks. Follow the project's architecture rules. Proceed within the user-authorized scope. Ask only about unresolved scope or consequential choices.
5. **Implement** in small steps, running the project's compile check after each. New UI is Compose, Material3, inside the
   project's theme and components, split into stateless `XContent` and stateful `XScreen`. No orientation locks.
6. **Tests.** ViewModel and use-case tests (JUnit5/Kotest/MockK, `runTest`). Run them with `--tests` and quote the summary.
7. **Device verification.** `$android-run-app` on the default phone AVD, navigate to the feature, `android screen`; repeat
   on the tablet AVD for any new or changed screen. Check insets (`edge-to-edge`) and large-screen layout (`adaptive`).
   Then hand off to the `android-verifier` agent with the test command, the journey file(s) for the touched screen, the
   device serial and application id. It returns the JSON journey result and screenshot paths; a FAILED action is a
   finding, not something to fix inside this step. A new screen gets a new journey.
8. **Review.** `android-reviewer` against the acceptance criteria. Fix Blockers/Majors; list declined Nits.
9. **Commit, only if asked**: `feat(<ticket>): <subject>` (or `refactor(<ticket>): ...` for modify-only). Body: at most 3 short lines.
   Do not push unless asked.
10. **Report**: files changed, commands run with results, screenshot paths, what is left for QA.
