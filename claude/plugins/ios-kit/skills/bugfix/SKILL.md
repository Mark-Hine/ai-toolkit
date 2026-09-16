---
name: bugfix
description: Bug-fix playbook for iOS apps: reproduce (test or simulator), root cause, minimal fix, regression test, review, commit.
argument-hint: "[ticket] [symptom]"
---

# Bug fix: $ARGUMENTS

Repo facts (workspace, schemes, build/test commands, test framework, bundle id) come from the project's `CLAUDE.md`.

1. **Restate** the symptom, expected behaviour, and affected scheme, OS version or device if known. Branch `fix/<ticket>-<slug>`.
2. **Locate.** Explore subagent: trace the path from symptom to code (view → view model → service/repository → API).
   Read the whole path, not the first suspicious line. `git log -S` for the change that introduced it.
3. **Reproduce.** Prefer a failing unit test in the target that owns the defect. For UI or platform bugs reproduce on the
   simulator with `/ios-kit:run-app` (an older runtime from `xcrun simctl list runtimes` for OS-specific issues); capture a
   screenshot and the relevant `log show` excerpt. Quote the failing output.
4. **Root cause.** One paragraph: what is wrong and why it produces the symptom. If a fix would only mask it (optional
   chaining that hides a nil, `DispatchQueue.main.async` to paper over isolation, a `try?`), say so and propose the real fix.
   Ask `ios-researcher` when an OS behaviour change or deprecation is suspected.
5. **Fix** with the minimal diff. Note refactor candidates as follow-ups instead of doing them.
6. **Verify.** Failing test now green plus the suite's other tests (`xcodebuild test … -only-testing:`); the project's build
   command for every scheme it lists. Hand the test rerun and, for UI bugs, the simulator smoke check to the `ios-verifier`
   agent and quote its results.
7. **Review.** `ios-reviewer` with the symptom and root cause as the task statement.
8. **Commit**: `fix(<ticket>): <subject>`; body: root cause in one line, guarding test in one line. Do not push unless asked.
9. **Report**: cause, fix, evidence (test before/after, screenshots), regression risk, pre-existing issues noticed.
