# Personal defaults

Read `~/.codex/machine.md` for local tool and device facts. If CODEX_HOME is set, use that directory instead of `~/.codex` for these personal files. Read `guidance/common.md` for shared Git and work preferences and `guidance/writing-style.md` there for responses, documents, PR text and commit bodies. These are explicit file-reading instructions, not automatic imports.

## Android and Kotlin

- Read matching guidance before editing. `guidance/android/kotlin-style.md` applies to Android `.kt` and `.kts` files. `compose.md` applies to Compose screens and components. `ui-events.md` applies to ViewModels and UI event collectors. `testing.md` applies to tests and journeys. The `paths` headers document scope and are not automatically loaded by Codex.
- Use `$android-feature`, `$android-bugfix`, `$android-uplift-deps`, `$android-run-app` and `$android-standards` when relevant. Use `$pr-review` for the formal JSON and Markdown PR-review deliverable.
- Project AGENTS.md and applicable personal rules take precedence over skills, subject to the user's current instructions. Read a project's CLAUDE.md if AGENTS.md is absent during migration, and read matching project `.claude/rules` where no Codex equivalent exists.
- Discover optional skills before using them. Use `using-chrisbanes-skills`, `android-cli` and official Android skills when installed. Otherwise use bundled standards references, current official documentation and installed Android SDK tools. Do not fabricate a missing CLI or skill.
- Delegate current platform research to `android-researcher`, non-trivial Android diff review to `android-reviewer`, and build/test/device evidence collection to `android-verifier`. Give each a bounded task and re-check findings before reporting them. If custom agents are unavailable, perform the work inline and disclose the limitation.
- Role model and reasoning settings live in the installed `agents/<role>.toml` files. When manually spawning a role, use those settings and provide its installed instructions. Do not pass Claude model aliases.

## iOS and Swift

- Read matching guidance before editing. `guidance/ios/swift-style.md` applies to Swift files, `swiftui.md` to SwiftUI screens and components, `ui-events.md` to models and presentation, and `testing.md` to tests. Project instructions take precedence, with CLAUDE.md and project .claude/rules as migration fallbacks where no Codex equivalent exists.
- Use `$ios-feature`, `$ios-bugfix`, `$ios-uplift-deps`, `$ios-run-app` and `$ios-standards` when relevant. Discover optional SwiftUI skills and Xcode integrations before using them. Fall back to the bundled references, current official documentation and installed Xcode tools.
- Delegate current platform research to `ios-researcher`, non-trivial Swift/iOS diff review to `ios-reviewer`, and tests and simulator evidence to `ios-verifier`. Use the model and reasoning settings in the installed role TOML. Give each a bounded task and re-check findings. If unavailable, work inline and disclose the limitation.
