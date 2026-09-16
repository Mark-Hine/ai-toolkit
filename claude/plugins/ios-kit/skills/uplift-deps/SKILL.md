---
name: uplift-deps
description: Toolchain/dependency uplift playbook for iOS apps: one axis per commit, release-note research, Package.resolved/Podfile.lock diffs, review.
disable-model-invocation: true
argument-hint: "[ticket] [what to uplift, e.g. 'Firebase' or 'deployment target 17']"
---

# Dependency uplift: $ARGUMENTS

Repo facts (workspace, schemes, build/test commands, SwiftPM vs CocoaPods, deliberate pins) come from the project's
`CLAUDE.md`. Work in plan mode until step 4 is approved.

1. **Baseline.** Clean `git status` on `feature/<ticket>-<slug>`. Run the project's build and test commands and copy the
   lock files to the scratchpad: `Package.resolved` (workspace: `<ws>.xcworkspace/xcshareddata/swiftpm/Package.resolved`;
   packages: next to `Package.swift`) and `Podfile.lock` if present. Quote results.
2. **Inventory.** List in-scope items with current versions and rules: SwiftPM references in `project.pbxproj`
   (`XCRemoteSwiftPackageReference` → `requirement`) or `Package.swift`; `Podfile` entries; `.swift-version`,
   `SWIFT_VERSION`, `SWIFT_STRICT_CONCURRENCY`, `IPHONEOS_DEPLOYMENT_TARGET`; Xcode version in CI (`fastlane`, pipeline YAML).
3. **Research.** Ask `ios-researcher` for the latest stable of each item, its release notes, minimum Xcode/deployment target,
   privacy-manifest status, and the current App Store minimum Xcode/SDK requirement and date.
4. **Plan.** One commit per axis, ordered Xcode/SDK → deployment target → Swift toolchain/language mode → SwiftPM packages →
   CocoaPods → third-party binaries. Name the schemes you will build and the tests you will run. Get approval.
5. **Apply each axis.** Edit versions only where the project declares them. SwiftPM: change the rule, then
   `xcodebuild -resolvePackageDependencies -workspace <ws> -scheme "<scheme>"`; CocoaPods: `pod update <Pod>` (never a
   bare `pod update`). Rebuild every scheme in `CLAUDE.md`, plus one Release build
   (`xcodebuild build -configuration Release -destination 'generic/platform=iOS' CODE_SIGNING_ALLOWED=NO`) for toolchain
   or deployment-target axes. Run the tests that passed at baseline. Diff the lock files against the baseline copies and
   list transitive changes. New or bumped SDKs on Apple's required-reason list must ship `PrivacyInfo.xcprivacy`.
6. **Runtime check** when an SDK with native code or a swizzling/analytics SDK changed: `/ios-kit:run-app`, launch plus one
   authenticated screen. The `ios-verifier` agent runs the baseline tests and the smoke check and returns the evidence.
7. **Review.** `ios-reviewer`. Fix Blockers/Majors.
8. **Commit** per axis: `chore(<ticket>): bump <thing> <old> -> <new>`; body: up to 3 lines naming release-note items that
   affect this app. Do not push unless asked.
9. **Report** table: item, old, new, build result, test result, notable transitive changes, follow-ups.
