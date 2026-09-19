---
name: ios-uplift-deps
description: "Toolchain/dependency uplift playbook for iOS apps: one axis per commit, release-note research, Package.resolved/Podfile.lock diffs, review."
---

Read the project AGENTS.md (or GEMINI.md) and applicable guidance first. Fall back to CLAUDE.md if AGENTS.md is absent. Follow global rules for optional tools, specialist subagents and Git actions.

# Dependency uplift: the user request

Repo facts (workspace, schemes, build/test commands, SwiftPM vs CocoaPods, deliberate pins) come from the project's
`AGENTS.md`. State the plan before editing versions and proceed within user-authorized scope.

1. **Baseline.** Clean `git status` on `feature/<ticket>-<slug>`. Run the project's build and test commands and copy
   lock files to scratchpad: `Package.resolved` (workspace: `<ws>.xcworkspace/xcshareddata/swiftpm/Package.resolved`;
   packages: next to `Package.swift`) and `Podfile.lock` if present. Quote results.
2. **Inventory.** List in-scope items with current versions and rules: SwiftPM references in `project.pbxproj`
   (`XCRemoteSwiftPackageReference` → `requirement`) or `Package.swift`; `Podfile` entries; `.swift-version`,
   `SWIFT_VERSION`, `SWIFT_STRICT_CONCURRENCY`, `IPHONEOS_DEPLOYMENT_TARGET`; Xcode version in CI (`fastlane`, pipeline YAML).
3. **Research.** Ask `ios-researcher` for latest stable of each item, its release notes, minimum Xcode/deployment target,
   privacy-manifest status, and current App Store minimum Xcode/SDK requirement and date.
4. **Plan.** One commit per axis, ordered Xcode/SDK → deployment target → Swift toolchain/language mode → SwiftPM packages →
   CocoaPods → third-party binaries. Name schemes you will build and tests you will run. Proceed within authorized scope; ask only about unresolved scope or consequential choices.
5. **Apply each axis.** Edit versions only where the project declares them. SwiftPM: change the rule, then
   `xcodebuild -resolvePackageDependencies -workspace <ws> -scheme "<scheme>"`; CocoaPods: `pod update <Pod>` (never a
   bare `pod update`). Rebuild every scheme in `AGENTS.md`, plus one Release build
   (`xcodebuild build -configuration Release -destination 'generic/platform=iOS' CODE_SIGNING_ALLOWED=NO`) for toolchain
   or deployment-target axes. Run tests that passed at baseline. Diff lock files against baseline copies and
   list transitive changes. New or bumped SDKs on Apple's required-reason list must ship `PrivacyInfo.xcprivacy`.
6. **Runtime check** when an SDK with native code or a swizzling/analytics SDK changed: `/ios-run-app`, launch plus one
   authenticated screen. The `ios-verifier` agent runs baseline tests and smoke check and returns evidence.
7. **Review.** `ios-reviewer`. Fix Blockers/Majors.
8. **Commit, only if asked.** Follow shared Git conventions. Do not push unless asked.
9. **Report** table: item, old, new, build result, test result, notable transitive changes, follow-ups.
