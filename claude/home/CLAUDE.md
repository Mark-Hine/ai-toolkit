# Personal defaults (all projects)

@~/.claude/machine.md

Shared Git and work preferences load from `~/.claude/rules/common.md`. Writing preferences load from `~/.claude/rules/writing-style.md`. Tiered design rules load from `~/.claude/rules/design-standards.md`.

## Subagents
- Always pin `model` and never `inherit`. Research/fetch agents: `sonnet`. Review/judgement agents: `opus`.

## UI/UX and Design Standards
- Read `~/.claude/rules/design-standards.md` before creating or modifying UI screens, components, and design systems.
- Use `/design-kit:standards` for the sources, rationale and platform APIs behind the tiered design rules (HIG, Material 3, WCAG 2.2, house), screen states, accessibility and platform fidelity.
- Delegate UI/UX diffs, component audits, and screen reviews to `ui-reviewer`. Give it a bounded task and re-check findings before reporting them.

## Kotlin across platforms

- `~/.claude/rules/kotlin.md` applies to `.kt` and `.kts` files in every project. Android rules add platform requirements.
- For rationale, examples and Kotlin review criteria, load `references/languages/kotlin.md` from `/pr-review:pr-review`.

## Android/Kotlin work
- Before implementing, check `/skills` for an installed skill that covers the task and load it. Official Android skills
  (`testing-setup`, `edge-to-edge`, `adaptive`, `agp-9-upgrade`, `r8-analyzer`, `android-intent-security`) are procedures. Follow them.
- Precedence: the project `CLAUDE.md` and the rules in `~/.claude/rules/` win over any skill. If a skill and a rule
  conflict, follow the rule and state the conflict in the report. If a skill and official docs conflict, ask `android-researcher`.
- Route Kotlin/Compose design questions through `using-chrisbanes-skills`. Use the `/android-kit:*` playbooks. Take platform
  facts from `android-researcher`, never memory. Send non-trivial diffs to `android-reviewer` before "done".

## iOS and Swift

- Read matching rules before editing. `~/.claude/rules/ios/swift-style.md` applies to Swift files, `swiftui.md` to SwiftUI screens and components, `ui-events.md` to models and presentation, and `testing.md` to tests. Project instructions and matching project rules take precedence.
- Use the `/ios-kit:feature`, `/ios-kit:bugfix`, `/ios-kit:uplift-deps`, `/ios-kit:run-app` and `ios-kit:standards` playbooks when relevant. Discover optional SwiftUI skills and Xcode integrations before using them. Fall back to the bundled references, current official documentation and installed Xcode tools.
- Delegate current platform research to `ios-researcher`, non-trivial Swift/iOS diff review to `ios-reviewer`, and tests and simulator evidence to `ios-verifier`. Use the model settings under Subagents. Give each a bounded task and re-check findings. If unavailable, work inline and disclose the limitation.
