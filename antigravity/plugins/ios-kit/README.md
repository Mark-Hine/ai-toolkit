# ios-kit

iOS and Swift development plugin for Google Antigravity. Packages feature and bugfix playbooks, simulator and dependency workflows, house standards, consolidated rules, specialist subagent specifications, and Swift lint lifecycle hooks.

## Skills

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `ios-feature` | `/ios-feature` | Feature playbook: intake, pattern discovery, plan, implement, tests, simulator check, review |
| `ios-bugfix` | `/ios-bugfix` | Bug-fix playbook: reproduce, root cause, minimal fix, regression test, review |
| `ios-run-app` | `/ios-run-app` | Explicitly invoked simulator build, install, launch and screenshot capture |
| `ios-standards` | `/ios-standards` | Reference index for Apple docs, SwiftUI data-flow, house patterns, and project instructions template |
| `ios-uplift-deps` | `/ios-uplift-deps` | Explicitly invoked Xcode/Swift/dependency uplift |

## Rules (`rules/AGENTS.md`)

Consolidated Swift style, SwiftUI state ownership, UI events, testing, and specialist subagent delegation guidelines automatically loaded when this plugin is enabled.

## Specialist Subagents (`agents/`)

- `ios-reviewer`: Read-only diff review (`model: pro`). Grades correctness, requirements, security, build health without writing code.
- `ios-researcher`: Read-only Apple platform and official documentation research (`model: flash`).
- `ios-verifier`: Runs tests and simulator checks (`model: flash`, workspace writes enabled).

## Hooks (`hooks.json`)

PostToolUse hook running SwiftFormat / SwiftLint on modified `.swift` files when the repository provides `.swiftformat` or `.swiftlint.yml`.
