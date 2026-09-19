# android-kit

Android development plugin for Google Antigravity. Packages feature and bugfix playbooks, testing and dependency workflows, house standards, consolidated rules, specialist subagent specifications, and lifecycle safety guards.

## Skills

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `android-feature` | `/android-feature` | Feature playbook: intake, pattern discovery, scoped plan, implementation, unit tests, device verification, review |
| `android-bugfix` | `/android-bugfix` | Bug-fix playbook: reproduction, root cause, minimal fix, regression testing, review |
| `android-run-app` | `/android-run-app` | Explicitly invoked build, install, launch and screenshot capture |
| `android-standards` | `/android-standards` | Reference index for official docs, Now in Android, JetSnack, UI events and testing |
| `android-uplift-deps` | `/android-uplift-deps` | Explicitly invoked toolchain and dependency upgrade with compatibility research |

## Rules (`rules/AGENTS.md`)

Consolidated Kotlin, Jetpack Compose, UI events, testing and subagent delegation guidelines automatically loaded when this plugin is enabled.

## Specialist Subagents (`agents/`)

- `android-reviewer`: Read-only diff review (`model: pro`, high reasoning). Grades correctness, requirements, security, build health without writing code.
- `android-researcher`: Read-only platform and official documentation research (`model: flash`).
- `android-verifier`: Test runner and emulator journey verification (`model: pro`, workspace write enabled).

## Hooks (`hooks.json`)

PreToolUse guard hook enforcing branch protection, destructive git blocks, timeout prevention, and secret file protection.
