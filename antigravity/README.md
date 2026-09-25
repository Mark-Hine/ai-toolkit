# Antigravity setup

The Antigravity port of the portable AI toolkit packages three plugins, eleven skills, six specialist subagents, personal instructions, Android, iOS and writing guidance, and lifecycle hooks according to Antigravity best practices. The Claude Code setup remains in `../claude/` and the OpenAI Codex setup in `../codex/`.

## Install

Requires Python 3.11 or later. The installer needs no third-party packages, credentials or network access.

```bash
./antigravity/install.sh --dry-run
./antigravity/install.sh
```

Rerun the installer after pulling toolkit updates. It preserves existing configuration values, unrelated custom hooks, personal instructions and machine facts. Displaced files, symlinks and directories are backed up under `~/.gemini/config/backups/ai-toolkit-<timestamp>/`, with original locations recorded in `manifest.json`.

`ANTIGRAVITY_HOME` or `GEMINI_CONFIG_DIR` selects the configuration directory (defaults to `~/.gemini/config`). Skills also link to `~/.agents/skills` (or `--skills-home PATH`) for workspace-level and flat discovery. Keep this checkout available because skills, guidance, plugins and hooks are symlinked to it.

## Installed layout

| Source | Global destination | Purpose |
| --- | --- | --- |
| `home/AGENTS.md` | `~/.gemini/config/AGENTS.md` managed block | Personal defaults, writing preferences, and plugin/subagent routing |
| `home/GEMINI.md` | `~/.gemini/config/GEMINI.md` symlink | Symlink to `AGENTS.md` for dual Antigravity discovery |
| `../shared/guidance/common.md` | `~/.gemini/config/guidance/common.md` | Shared Git and work preferences used across all agents |
| `home/guidance/` | `~/.gemini/config/guidance/` | Writing preferences and modular Android/iOS rules |
| `home/config.defaults.json` | Merged into `~/.gemini/config/config.json` | Registers plugins `android-kit`, `ios-kit`, and `pr-review` as enabled |
| `home/machine.md.example` | `~/.gemini/config/machine.md`, created only if absent | Private machine facts (simulators, AVDs, CLI paths) |
| `home/plugins.json` | `~/.gemini/config/plugins.json` | Explicit plugins manifest for discovery |
| `home/skills.json` | `~/.gemini/config/skills.json` | Explicit skills manifest for discovery |
| `plugins/` | `~/.gemini/config/plugins/` | Modular bundles with skills, consolidated rules, hooks and subagent specs |
| `skills/` | `~/.agents/skills/` | Portable workflows with references and scripts |
| `hooks/` | Referenced by merged `~/.gemini/config/hooks.json` | PreToolUse command/file safety guard and PostToolUse Swift lint |

## Plugins, skills and specialist subagents

### Plugins

- **`android-kit`**: Android development plugin bundling 5 skills, consolidated Kotlin/Compose rules, guard hooks, and 3 specialist subagent definitions.
- **`ios-kit`**: iOS/Swift development plugin bundling 5 skills, consolidated Swift/SwiftUI rules, Swift lint hooks, and 3 specialist subagent definitions.
- **`pr-review`**: Formal PR and release-promotion review plugin with multi-platform grading criteria and Azure DevOps integration.

### Skills

| Invocation | Behavior |
| --- | --- |
| `/android-feature` | Intake, pattern discovery, scoped plan, implementation, tests and emulator verification |
| `/android-bugfix` | Reproduction, root cause, focused fix and regression evidence |
| `/android-uplift-deps` | Explicitly invoked dependency/toolchain uplift with compatibility research |
| `/android-run-app` | Explicitly invoked build, install, launch and screenshot workflow |
| `/android-standards` | Android, Kotlin, Gradle, NIA, JetSnack and house-pattern reference index |
| `/ios-feature` | Intake, pattern discovery, scoped plan, implementation, tests and simulator checks |
| `/ios-bugfix` | Reproduction, root cause, minimal fix and regression evidence |
| `/ios-uplift-deps` | Explicitly invoked Xcode/Swift/dependency uplift |
| `/ios-run-app` | Explicitly invoked simulator build, install, launch and screenshots |
| `/ios-standards` | Apple/Swift/Xcode docs, house patterns and project instructions template |
| `/pr-review` | Formal JSON and Markdown review, release-promotion verification, and re-review tracking |

### Specialist Subagents

Defined via `define_subagent` and invoked via `invoke_subagent` using the specifications in `agents/`:

| Specialist Role | Antigravity Model | Capabilities | Description |
| --- | --- | --- | --- |
| `android-reviewer` | `pro` | Read-only | Evaluates diff against criteria, grades Blocker/Major/Nit, writes no code |
| `android-researcher` | `flash` | Read-only | Queries official Android/Kotlin/Gradle documentation |
| `android-verifier` | `flash` | Workspace write | Runs Gradle test tasks and emulator journeys, collects evidence |
| `ios-reviewer` | `pro` | Read-only | Evaluates Swift diffs, grades Blocker/Major/Nit, writes no code |
| `ios-researcher` | `flash` | Read-only | Queries official Apple/Swift/Xcode documentation |
| `ios-verifier` | `flash` | Workspace write | Runs `xcodebuild test` and simulator smoke checks, collects evidence |

## Migration decisions and Antigravity best practices

- **Plugin packaging**: Uses Antigravity's first-class plugin structure (`plugin.json`, `rules/AGENTS.md`, `skills/`, `hooks.json`).
- **Consolidated rules**: As recommended in the Antigravity Plugins Guide, consolidated rules are placed in `plugins/<name>/rules/AGENTS.md`. Antigravity automatically merges these when the plugin is enabled.
- **Progressive disclosure**: Skills maintain concise `SKILL.md` runbooks and store bulky manuals, guidelines and code samples in `references/`. The agent reads them on demand.
- **Hook contracts**:
  - `PreToolUse`: Evaluates commands (`CommandLine`) and file operations (`TargetFile`, `write_to_file`, `replace_file_content`). Emits `{"decision": "allow"}` or `{"decision": "deny", "reason": "..."}`.
  - `PostToolUse`: Runs SwiftFormat/SwiftLint on changed `.swift` files and returns `{}` in compliance with Antigravity's contract.
- **Shared conventions**: Shared Git and work defaults remain centralized in `shared/guidance/common.md`, linked into installed guidance.
- **Writing preferences**: Preserves concise plain-prose preferences without boilerplate fillers.

## Guard coverage

The PreToolUse guard hook blocks:
- Protected-branch pushes (`main`, `master`, `develop`, `release/*`)
- Force pushes (`--force`, `-f`, `+ref`) and mirror pushes
- Unchecked implicit pushes without explicit remote and feature refspec
- Destructive Git operations (`reset --hard`, `clean -fd`, `checkout -- .`, `restore .`)
- `timeout` command wrappers
- Editing secrets, signing files, keystores, provisioning profiles, network security configs, `.env` files, and package lock files
- Specialists attempting to write to source code or execute unauthorized commands

## Validation

```bash
python3 -m unittest discover -s antigravity/tests -v
python3 antigravity/scripts/validate.py
bash -n antigravity/install.sh
```

CI runs these validation checks and unit tests on every push and pull request.
