---
name: ios-bugfix
description: "Bug-fix playbook for iOS apps: reproduce (test or simulator), root cause, minimal fix, regression test, review, commit."
---

Read the project AGENTS.md (or GEMINI.md) and applicable guidance first. Fall back to CLAUDE.md if AGENTS.md is absent. Follow global rules for optional tools, specialist subagents and Git actions.

# Bug fix: the user request

Repo facts (workspace, schemes, build/test commands, test framework, bundle id) come from the project's `AGENTS.md`.

1. **Restate** symptom, expected behaviour, and affected scheme, OS version or device if known. Branch `fix/<ticket>-<slug>`.
2. **Locate.** Research subagent: trace the path from symptom to code (view → view model → service/repository → API).
   Read the whole path, not the first suspicious line. `git log -S` for the change that introduced it.
3. **Reproduce.** Prefer a failing unit test in the target that owns the defect. For UI or platform bugs reproduce on
   simulator with `/ios-run-app` (an older runtime from `xcrun simctl list runtimes` for OS-specific issues); capture a
   screenshot and relevant `log show` excerpt. Quote the failing output.
4. **Root cause.** One paragraph: what is wrong and why it produces the symptom. If a fix would only mask it (optional
   chaining that hides a nil, `DispatchQueue.main.async` to paper over isolation, a `try?`), say so and propose the real fix.
   Ask `ios-researcher` when an OS behaviour change or deprecation is suspected.
5. **Fix** with minimal diff. Note refactor candidates as follow-ups instead of doing them.
6. **Verify.** Failing test now green plus suite's other tests (`xcodebuild test … -only-testing:`); project's build
   command for every scheme it lists. Hand test rerun and, for UI bugs, simulator smoke check to `ios-verifier` and quote results.
7. **Review.** `ios-reviewer` with symptom and root cause as the task statement.
8. **Commit, only if asked.** Follow shared Git conventions. Do not push unless asked.
9. **Report**: cause, fix, evidence (test before/after, screenshots), regression risk, pre-existing issues noticed.
