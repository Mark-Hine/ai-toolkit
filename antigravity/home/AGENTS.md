# Personal defaults

Read `~/.gemini/config/machine.md` for local tool and device facts. Read `~/.gemini/config/guidance/common.md` for shared Git and work preferences and `~/.gemini/config/guidance/writing-style.md` for responses, documents, PR text and commit bodies. These are explicit file-reading instructions.

## Plugins and subagents

- The ai-toolkit plugins (`android-kit`, `ios-kit`, `pr-review`, `design-kit`) are linked under `~/.gemini/config/plugins/`. Each carries its skills, its rules (always on while the plugin is enabled), its hooks and its agents. Plugin agents load automatically and are invoked with `invoke_subagent`.
- Research and official-source lookups use `model: flash` with read-only tools. Deep code reviews and judgements use `model: pro` with read-only tools. Verifiers collect build, test, simulator and emulator evidence with `model: flash` and run commands under the automatic policy.
- Give every subagent a bounded task and re-check its findings before reporting them. If a subagent is unavailable, do the work inline and say so.

## UI and design

- Read `~/.gemini/config/guidance/design-standards.md` before creating or modifying UI screens, components or design systems. When `design-kit` is enabled, the same rules load with the plugin.
- Use `/design-standards` for the sources, rationale and platform APIs behind the tiered design rules (HIG, Material 3, WCAG 2.2, house), screen states, accessibility and platform fidelity.
- Delegate UI diffs, component audits and screen reviews to `ui-reviewer`.

## Android and Kotlin

- The android-kit rules load with the plugin. Each section names the file paths it applies to.
- Use `/android-feature`, `/android-bugfix`, `/android-uplift-deps`, `/android-run-app` and `/android-standards` when relevant. Use `/pr-review` for the formal JSON and Markdown PR-review deliverable.
- Project `AGENTS.md` (or `GEMINI.md`) and applicable personal rules take precedence over skills, subject to the current instructions. Read a project's `CLAUDE.md` if `AGENTS.md` is absent during migration.
- Discover optional tools before using them. Use `using-chrisbanes-skills`, `android-cli` and official Android skills when installed. Otherwise use the bundled standards references, current official documentation and installed Android SDK tools. Do not fabricate a missing CLI or skill.
- Delegate current platform research to `android-researcher`, non-trivial Android diff review to `android-reviewer`, and build, test and device evidence to `android-verifier`.

## iOS and Swift

- The ios-kit rules load with the plugin. Each section names the file paths it applies to. Project instructions take precedence, with `CLAUDE.md` as a migration fallback where no `AGENTS.md` exists.
- Use `/ios-feature`, `/ios-bugfix`, `/ios-uplift-deps`, `/ios-run-app` and `/ios-standards` when relevant. Discover optional SwiftUI skills and Xcode integrations before using them. Fall back to the bundled references, current official documentation and installed Xcode tools.
- Delegate current platform research to `ios-researcher`, non-trivial Swift diff review to `ios-reviewer`, and tests and simulator evidence to `ios-verifier`.
