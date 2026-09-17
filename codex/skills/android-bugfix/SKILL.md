---
name: android-bugfix
description: "Bug-fix playbook for Android apps: reproduce (test or emulator), root cause, minimal fix, regression test, review, commit."
---

Read the project AGENTS.md and applicable global guidance first. Fall back to CLAUDE.md if AGENTS.md is absent. Follow the global rules for optional tools, specialist agents and Git actions.


# Bug fix: the user request

Repo facts (modules, build/test commands, app id) come from the project's `AGENTS.md`.

1. **Restate** the symptom, expected behaviour, and affected variant or device if known. Branch `fix/<ticket>-<slug>`.
2. **Locate.** explorer subagent: trace the path from symptom to code (screen → ViewModel → use case/repository → API).
   Read the whole path, not the first suspicious line. `git log -S` for the change that introduced it.
3. **Reproduce.** Prefer a failing unit test in the module that owns the defect. For UI or platform bugs reproduce on the
   emulator with `$android-run-app` (min-SDK AVD for min-SDK issues); capture `android screen` and `adb logcat` excerpts.
   Quote the failing output.
4. **Root cause.** One paragraph: what is wrong and why it produces the symptom. If a fix would only mask it (catch-all,
   null guard), say so and propose the real fix. Ask `android-researcher` when a platform behaviour change is suspected.
5. **Fix** with the minimal diff. Note refactor candidates as follow-ups instead of doing them.
6. **Verify.** Failing test now green plus the class's other tests; the project's compile check; for UI bugs re-run on the
   emulator with a screenshot. Hand the failing-test rerun and the screen's journey (if one exists) to the
   `android-verifier` agent and quote its results.
7. **Review.** `android-reviewer` with the symptom and root cause as the task statement.
8. **Commit, only if asked.** Follow the shared Git conventions. Do not push unless asked.
9. **Report**: cause, fix, evidence (test before/after, screenshots), regression risk, pre-existing issues noticed.
