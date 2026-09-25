# Personal defaults

Read `~/.gemini/config/machine.md` for local tool and device facts. If `GEMINI_CONFIG_DIR` is set, use that directory instead of `~/.gemini/config` for these personal files. Read `guidance/common.md` for shared Git and work preferences and `guidance/writing-style.md` for responses, documents, PR text and commit bodies.

## Subagents

- Always match subagent capabilities to the task. Research and official-source lookups use fast models (`model: flash`, read-only). Deep code reviews and judgements use high-reasoning models (`model: pro`, read-only). Verifiers collect build, test, simulator and emulator evidence (`model: flash`, workspace writes enabled).
- When a specialist role is not already active, define it with `define_subagent` using the specifications in `agents/` and invoke it via `invoke_subagent`.

## Android and Kotlin

- Read matching guidance before editing. `guidance/android/kotlin-style.md` applies to Android `.kt` and `.kts` files. `compose.md` applies to Compose screens and components. `ui-events.md` applies to ViewModels and UI event collectors. `testing.md` applies to tests and journeys.
- When `android-kit` is enabled, its consolidated rules under `rules/AGENTS.md` are active.
- Use `/android-feature`, `/android-bugfix`, `/android-uplift-deps`, `/android-run-app` and `/android-standards` when relevant. Use `/pr-review` for the formal JSON and Markdown PR-review deliverable.
- Project `AGENTS.md` (or `GEMINI.md`) and applicable personal rules take precedence over skills, subject to the user's current instructions. Read a project's `CLAUDE.md` if `AGENTS.md` is absent during migration.
- Discover optional tools before using them. Use `using-chrisbanes-skills`, `android-cli` and official Android skills when installed. Otherwise use bundled standards references, current official documentation and installed Android SDK tools. Do not fabricate a missing CLI or skill.
- Delegate current platform research to `android-researcher`, non-trivial Android diff review to `android-reviewer`, and build/test/device evidence collection to `android-verifier`. Give each a bounded task and re-check findings before reporting them. If subagents are unavailable, perform the work inline and disclose the limitation.

## iOS and Swift

- Read matching guidance before editing. `guidance/ios/swift-style.md` applies to Swift files, `swiftui.md` to SwiftUI screens and components, `ui-events.md` to models and presentation, and `testing.md` to tests. Project instructions take precedence, with `CLAUDE.md` as a migration fallback where no `AGENTS.md` exists.
- When `ios-kit` is enabled, its consolidated rules under `rules/AGENTS.md` are active.
- Use `/ios-feature`, `/ios-bugfix`, `/ios-uplift-deps`, `/ios-run-app` and `/ios-standards` when relevant. Discover optional SwiftUI skills and Xcode integrations before using them. Fall back to bundled references, current official documentation and installed Xcode tools.
- Delegate current platform research to `ios-researcher`, non-trivial Swift/iOS diff review to `ios-reviewer`, and tests and simulator evidence to `ios-verifier`. Give each a bounded task and re-check findings. If unavailable, work inline and disclose the limitation.
