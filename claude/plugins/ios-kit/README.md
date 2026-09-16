# ios-kit

Claude Code plugin for iOS work. Install with `/plugin marketplace add Mark-Hine/ai-toolkit` then `/plugin install ios-kit@ai-toolkit`.

| Component | Use |
| --- | --- |
| `/ios-kit:feature PROJ-123 <summary>` | Feature or feature-change playbook: intake, pattern discovery, plan, implement, tests, simulator check, review, commit |
| `/ios-kit:bugfix PROJ-123 <symptom>` | Reproduce (test or simulator), root cause, minimal fix, regression test, review, commit |
| `/ios-kit:uplift-deps PROJ-123 <what>` | Xcode/Swift/SwiftPM/CocoaPods uplift, one axis per commit, `Package.resolved`/`Podfile.lock` diffs (manual invocation only) |
| `/ios-kit:run-app <simulator> <scheme>` | Build, install, launch and screenshot a debug scheme via `xcodebuild` and `xcrun simctl` (manual invocation only) |
| `standards` skill | Index of Apple/Swift.org docs, Apple sample apps (Landmarks, Backyard Birds, Food Truck), house patterns, and a per-repo `CLAUDE.md` template; preloaded into the researcher |
| `ios-reviewer` agent | Read-only diff review, runs the project's build and targeted tests, grades Blocker/Major/Nit, checks effective artefacts (built `Info.plist`, lock files) |
| `ios-researcher` agent | Read-only research on Apple/Swift guidance; shell limited to read-only tooling queries by `agents/hooks/ios-researcher-bash.sh` |
| `ios-verifier` agent | Runs `xcodebuild test`, summarises with `xcresulttool`, launches and screenshots on the simulator; shell limited by `agents/hooks/ios-verifier-bash.sh`. Reports that interaction was not verified when no XCUITest covers a screen |
| `hooks/swift-lint.sh` | PostToolUse on `.swift` edits. Runs SwiftFormat `--lint` and SwiftLint only when the repo has `.swiftformat` or `.swiftlint.yml` and the binary is installed; findings come back as feedback |

Playbooks read repo facts (workspace, schemes, bundle id, design-system package, test framework) from the project's `CLAUDE.md`. Machine facts (default simulator) come from `~/.claude/machine.md`. Path-scoped Swift, SwiftUI, testing and UI-events rules install separately from `claude/home/rules/ios/`. Optional companions, documented in the standards index: Paul Hudson's `swiftui-agent-skill` for SwiftUI API detail, XcodeBuildMCP for simulator UI automation, Sosumi for Apple docs as Markdown.
