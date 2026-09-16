---
name: feature
description: Feature or feature-change playbook for iOS apps: intake, pattern discovery, plan, implement, tests, simulator check, review, commit.
argument-hint: "[ticket] [one-line summary]  (say 'modify' if changing an existing feature)"
---

# Feature work: $ARGUMENTS

Repo facts (workspace, schemes, build/test commands, test framework, design-system package, bundle id, deployment target)
come from the project's `CLAUDE.md`. Never guess them.

1. **Intake.** If an Atlassian MCP tool is available, fetch the Jira ticket and quote its acceptance criteria; otherwise
   restate the goal in three bullets plus an out-of-scope list. Branch `feature/<ticket>-<slug>` off the default branch.
2. **Discover the pattern.** Use an Explore subagent to find the closest existing screen or flow: its SwiftUI `View` or
   `UIViewController`, view model / `@Observable` model, service or repository, where dependencies are assembled
   (composition root, `@Environment`), and tests. Note whether it is SwiftUI or UIKit and which test framework it uses.
   For a *modify* task also map every caller of the code you will change.
3. **Consult references.** Load `ios-kit:standards` for the house patterns (state ownership, one-shot events, design system).
   Ask `ios-researcher` only where guidance may have moved (navigation APIs, Liquid Glass, privacy manifests, deployment
   target behaviour, App Store requirements).
4. **Plan (plan mode).** Files to add or change, state model (one `enum State` per screen: `loading` / `loaded(...)` /
   `error(...)`), where data code goes, DI wiring, test list, simulator checks. Follow the project's architecture rules. Get approval.
5. **Implement** in small steps, running the project's build command after each. New UI is SwiftUI inside the project's
   design-system package and tokens, split into a stateless `XContent(state, actions)` with `#Preview` and a stateful
   `XScreen` that owns the `@MainActor` model and wires presentation. Loading runs in `.task`, never `Task {}` in `onAppear`.
   No force unwraps. Use `@Observable` unless the project's deployment target is below iOS 17 (its `CLAUDE.md` says).
6. **Tests.** View-model and service tests in the project's framework (Swift Testing or XCTest per `CLAUDE.md`; Quick/Nimble
   only where the target already uses it). Run them with `xcodebuild test … -only-testing:<Target>/<Suite>` and quote the
   summary (`xcrun xcresulttool get test-results summary --path <bundle>.xcresult`).
7. **Simulator verification.** `/ios-kit:run-app` on the default simulator, navigate to the feature, screenshot; repeat at
   `content_size accessibility-extra-large` and in dark appearance for any new or changed screen, and on an iPad simulator if
   `TARGETED_DEVICE_FAMILY` includes 2. Then hand off to the `ios-verifier` agent with the test command, the simulator, bundle
   id and the screens to check. It returns test totals, screenshot paths and findings; a failure is a finding, not something to
   fix inside this step.
8. **Review.** `ios-reviewer` against the acceptance criteria. Fix Blockers/Majors; list declined Nits.
9. **Commit**: `feat(<ticket>): <subject>` (or `refactor(<ticket>): ...` for modify-only). Body: at most 3 short lines.
   Do not push unless asked.
10. **Report**: files changed, commands run with results, screenshot paths, what is left for QA.
