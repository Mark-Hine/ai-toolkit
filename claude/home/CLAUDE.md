# Personal defaults (all projects)

@~/.claude/machine.md

Shared Git and work preferences load from `~/.claude/rules/common.md`. Writing preferences load from `~/.claude/rules/writing-style.md`.

## Subagents
- Always pin `model`; never `inherit`. Research/fetch agents: `sonnet`. Review/judgement agents: `opus`.

## Android/Kotlin work
- Before implementing, check `/skills` for an installed skill that covers the task and load it. Official Android skills
  (`testing-setup`, `edge-to-edge`, `adaptive`, `agp-9-upgrade`, `r8-analyzer`, `android-intent-security`) are procedures; follow them.
- Precedence: the project `CLAUDE.md` and the rules in `~/.claude/rules/` win over any skill. If a skill and a rule
  conflict, follow the rule and state the conflict in the report. If a skill and official docs conflict, ask `android-researcher`.
- Route Kotlin/Compose design questions through `using-chrisbanes-skills`; use the `/android-kit:*` playbooks; platform
  facts via `android-researcher`, never memory; non-trivial diffs to `android-reviewer` before "done".

## iOS and Swift

- Read matching rules before editing. `~/.claude/rules/ios/swift-style.md` applies to Swift files, `swiftui.md` to SwiftUI screens and components, `ui-events.md` to models and presentation, and `testing.md` to tests. Project instructions and matching project rules take precedence.
- Use the `/ios-kit:feature`, `/ios-kit:bugfix`, `/ios-kit:uplift-deps`, `/ios-kit:run-app` and `ios-kit:standards` playbooks when relevant. Discover optional SwiftUI skills and Xcode integrations before using them. Fall back to the bundled references, current official documentation and installed Xcode tools.
- Delegate current platform research to `ios-researcher`, non-trivial Swift/iOS diff review to `ios-reviewer`, and tests and simulator evidence to `ios-verifier`. Use the model settings under Subagents. Give each a bounded task and re-check findings. If unavailable, work inline and disclose the limitation.
