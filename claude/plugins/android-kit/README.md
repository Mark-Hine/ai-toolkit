# android-kit

Claude Code plugin for Android work. Install with `/plugin marketplace add Mark-Hine/ai-toolkit` then `/plugin install android-kit@ai-toolkit`.

| Component | Use |
| --- | --- |
| `/android-kit:feature PROJ-123 <summary>` | Feature or feature-change playbook: intake, pattern discovery, plan, implement, tests, emulator check, review, commit |
| `/android-kit:bugfix PROJ-123 <symptom>` | Reproduce (test or emulator), root cause, minimal fix, regression test, review, commit |
| `/android-kit:uplift-deps PROJ-123 <what>` | Toolchain/dependency uplift, one axis per commit, release-note research, dependency diffs (manual invocation only) |
| `/android-kit:run-app <avd> <flavour>` | Build, install, launch and screenshot a debug variant via the Android CLI (manual invocation only) |
| `standards` skill | Index of official Android/Kotlin/Gradle docs, Now in Android, JetSnack and house patterns; preloaded into the researcher |
| `android-reviewer` agent | Read-only diff review, runs the project's compile check, grades Blocker/Major/Nit |
| `android-researcher` agent | Read-only research via `android docs` and official sources; shell limited by `agents/hooks/android-researcher-bash.sh` |
| `android-verifier` agent | Runs unit tests and `journeys/*.xml` on the emulator, returns JSON results and screenshots; shell limited to gradle test tasks, `android`, `adb` by `agents/hooks/android-verifier-bash.sh` |
| `hooks/` | Guard hooks (see `hooks/guard-bash.sh`, `hooks/guard-edit.sh`); require `jq` |

Playbooks read repo facts (modules, build commands, design system, app id) from the project's `CLAUDE.md`. Machine facts (AVD names, CLI paths) come from `~/.claude/machine.md`. The `android-cli` skill from Google's Android CLI is expected for emulator and docs steps.
