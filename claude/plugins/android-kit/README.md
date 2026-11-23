# android-kit

Claude Code plugin for Android work. Install with `/plugin marketplace add Mark-Hine/ai-toolkit` then `/plugin install android-kit@ai-toolkit`.

| Component | Use |
| --- | --- |
| `/android-kit:feature PROJ-123 <summary>` | Feature or feature-change playbook: intake, pattern discovery, plan, implement, tests, emulator check, review, commit |
| `/android-kit:bugfix PROJ-123 <symptom>` | Reproduce (test or emulator), root cause, minimal fix, regression test, review, commit |
| `/android-kit:uplift-deps PROJ-123 <what>` | Toolchain/dependency uplift, one axis per commit, release-note research, dependency diffs (manual invocation only) |
| `/android-kit:run-app <avd> <flavour>` | Build, install, launch and screenshot a debug variant via the Android CLI |
| `standards` skill | Index of official Android/Kotlin/Gradle docs, Now in Android, JetSnack and house patterns, preloaded into the researcher |
| `android-reviewer` agent | Read-only diff review, runs the project's compile check, grades Blocker/Major/Nit |
| `android-researcher` agent | Read-only research via `android docs` and official sources. Its shell is limited by guard-kit to `android docs` and `android sdk list` |
| `android-verifier` agent | Runs unit tests and `journeys/*.xml` on the emulator, returns JSON results and screenshots. Its shell is limited by guard-kit to gradle compile, assemble and test tasks, `android`, `adb` and reads |
| guard-kit dependency | The PreToolUse guard lives in the `guard-kit` plugin, which this plugin depends on. Its README lists what it blocks |

Playbooks read repo facts (modules, build commands, design system, app id) from the project's `CLAUDE.md`. Machine facts (AVD names, CLI paths) come from `~/.claude/machine.md`. Path-scoped Kotlin, Compose, testing and UI-events rules install separately with `claude/install.sh`. When a rule is not installed, the playbooks fall back to the standards references. Optional companions, such as Google's Android skills and `using-chrisbanes-skills`, are listed with install commands in `skills/standards/references/companions.md`. A playbook continues without a missing companion and marks its check Unverified.

## Evals

`evals/` holds a `claude plugin eval` suite. Each case copies the fixture in `evals/_fixtures/rewards/` into an empty workspace. The fixture is a small Kotlin module with a stand-in `gradlew` script, so a run needs no Android toolchain. The script logs each call to `.gradle-calls.log` and reports a test result from the sources.

| Case | Request | What passes |
| --- | --- | --- |
| `bugfix-zero-balance` | Fix a one-line bug | Exactly one regression test added, the bug fixed, a test run with `--tests`, no whole-project test run, and a final message that reports the failing run and the passing run |
| `change-points-cap` | Make a small behaviour change | The change made, the existing tests kept, a test for the new rule, at most 3 new tests, a test run with `--tests` and no whole-project test run |

```bash
claude plugin eval claude/plugins/android-kit --scaffold --allow-tools Bash Write Edit --no-publish
```

Eval runs load only this plugin, without `~/.claude/rules`, so they measure the playbooks and agents but not the rule files. Results go to `evals/results/`, which git ignores.
