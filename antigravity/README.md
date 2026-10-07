# Antigravity setup

The Antigravity port of the portable AI toolkit. Six plugins carry nineteen skills, ten specialist subagents, generated rules and lifecycle hooks, in the layout the bundled Antigravity customization docs describe. The Claude Code setup is in `../claude/` and the OpenAI Codex setup in `../codex/`.

## Install

Requires Python 3.11 or later. The installer needs no third-party packages, credentials or network access.

```bash
./antigravity/install.sh --dry-run
./antigravity/install.sh
```

Then restart Antigravity (`agy` or the IDE). New plugin directories are discovered at startup. `agy agents` lists the ten specialists and `agy plugin validate antigravity/plugins/<name>` checks a plugin.

Rerun the installer after pulling toolkit updates. Plugins are symlinked into place, so edits in this checkout are live at the next session. The installer preserves your own `config.json`, `hooks.json`, personal instructions and machine facts. Anything it replaces is backed up under `~/.gemini/config/backups/ai-toolkit-<timestamp>/` with a `manifest.json`. `ANTIGRAVITY_HOME` or `--gemini-home` selects the configuration directory (default `~/.gemini/config`).

An earlier version of this installer wrote `plugins.json`, `skills.json`, global `hooks.json` entries, `guidance/android`, `guidance/ios` and skill links under `~/.gemini/config/skills` and `~/.agents/skills`. The installer removes those when they are the ones it wrote, and leaves anything else alone.

## Installed layout

| Source | Global destination | Purpose |
| --- | --- | --- |
| `home/AGENTS.md` | `~/.gemini/config/AGENTS.md` managed block | Personal defaults, plugin and subagent routing |
| `../shared/guidance/common.md` | `~/.gemini/config/guidance/common.md` | Shared Git and work preferences |
| `../shared/guidance/kotlin.md` | `~/.gemini/config/guidance/kotlin.md` | Kotlin domain modeling and compatibility across platforms |
| `../shared/guidance/design-standards.md` | `~/.gemini/config/guidance/design-standards.md` | Tiered design rules, also loaded by `design-kit` |
| `../shared/guidance/design-assets.md` | `~/.gemini/config/guidance/design-assets.md` | Read before editing design contract, token, theme, SVG and icon files |
| `home/writing-style.md` | `~/.gemini/config/guidance/writing-style.md` | Condensed writing preferences |
| `home/machine.md.example` | `~/.gemini/config/machine.md`, created only if absent | Private machine facts |
| `plugins/<name>/` | `~/.gemini/config/plugins/<name>` symlink | Skills, generated rules, hooks and agents per plugin |

The shared Kotlin rule loads through the home instructions even when `android-kit` is disabled. Kotlin rationale and examples are bundled with `pr-review`.

Nothing is written to `config.json`, `hooks.json`, `plugins.json` or `skills.json`. Plugins are enabled by default. Use `agy plugin enable` or `agy plugin disable` to change that, never a hand edit of `config.json`.

## Plugins

Each plugin follows the documented shape: `plugin.json` (name, description, version), `skills/`, `rules/AGENTS.md`, `agents/` and, where needed, `hooks.json` with its scripts under `hooks/`.

- **`android-kit`**: five Android skills, generated Kotlin, Compose, UI-event and testing rules, the PreToolUse guard, and three specialists.
- **`ios-kit`**: five iOS skills, generated Swift, SwiftUI, UI-event and testing rules, the PreToolUse guard, the Swift lint hooks, and three specialists.
- **`web-kit`**: four web skills, generated TypeScript, React and testing rules, the PreToolUse guard, and three specialists.
- **`pr-review`**: the formal PR and release-promotion review skill with its platform packs and the Azure DevOps poster.
- **`design-kit`**: the `design-iterate` playbook, the `design-standards` skill with sources, rationale, platform APIs and design references, the generated design rules, and `ui-reviewer`.

### Rules are generated

`scripts/sync_rules.py` builds each plugin's `rules/AGENTS.md` from the canonical Claude rules under `../claude/home/rules/` and `../shared/guidance/design-standards.md`, applying the Antigravity wording (`AGENTS.md`, `/android-feature`, `~/.gemini/config/`). Plugin rules are plain markdown with no frontmatter and are always on while the plugin is enabled, so each section carries a scope line naming the file paths it applies to. Never edit the generated files. `sync_rules.py --check` runs in CI and in the validator.

### Skills

| Invocation | Behavior |
| --- | --- |
| `/android-feature` | Intake, pattern discovery, scoped plan, implementation, tests and emulator verification |
| `/android-bugfix` | Reproduction, root cause, focused fix and regression evidence |
| `/android-uplift-deps` | Dependency and toolchain uplift with compatibility research. Invoke it explicitly |
| `/android-run-app` | Build, install, launch and screenshot workflow. Invoke it explicitly |
| `/android-standards` | Android, Kotlin, Gradle, NIA, JetSnack and house-pattern reference index |
| `/ios-feature` | Intake, pattern discovery, scoped plan, implementation, tests and simulator checks |
| `/ios-bugfix` | Reproduction, root cause, minimal fix and regression evidence |
| `/ios-uplift-deps` | Xcode, Swift and dependency uplift. Invoke it explicitly |
| `/ios-run-app` | Simulator build, install, launch and screenshots. Invoke it explicitly |
| `/ios-standards` | Apple, Swift and Xcode docs, house patterns and the project instructions template |
| `/pr-review` | Formal JSON and Markdown review, release-promotion verification and re-review tracking |
| `/design-iterate` | Design playbook: the `DESIGN.md` contract, before and after captures, rendered options on a blind board, the user's pick, then tokens and review |
| `/design-standards` | Sources, rationale and platform APIs for the tiered design rules (HIG, Material 3, WCAG 2.2, house) |

Antigravity has no switch for implicit skill invocation, so the "invoke it explicitly" skills say so in their descriptions and nothing enforces it.

### Specialist subagents

Plugin agents load with their plugin and are invoked with `invoke_subagent`. Their frontmatter uses the documented fields only.

| Agent | Model | Tools | Commands | Description |
| --- | --- | --- | --- | --- |
| `android-researcher` | `flash` | read, web | policy `off`, every command is approved by a person | Queries official Android, Kotlin and Gradle documentation |
| `android-reviewer` | `pro` | read | `off` | Grades a diff Blocker, Major or Nit, writes no code |
| `android-verifier` | `flash` | read | `auto` | Runs Gradle test tasks and emulator journeys, collects evidence |
| `ios-researcher` | `flash` | read, web | `off` | Queries official Apple, Swift and Xcode documentation |
| `ios-reviewer` | `pro` | read | `off` | Grades a Swift diff, writes no code |
| `ios-verifier` | `flash` | read | `auto` | Runs `xcodebuild test` and simulator smoke checks, collects evidence |
| `ui-reviewer` | `pro` | read, web | `off` | Grades UI against the tiered design rules, citing rule ID and source |

No specialist has a write tool. Hooks receive no agent identity on Antigravity, so per-agent command limits come from each agent's `tools` list and `commandExecutionPolicy`, not from the guard.

## Hooks

The guard is the shared module `../shared/hooks/guard.py`, copied into `android-kit/hooks/` and `ios-kit/hooks/` and kept identical by CI. Each kit registers it under its own hook name, so both run when both kits are enabled, and both give the same answer. It runs as `python3 hooks/guard.py --agent antigravity` with the working directory at the plugin, as the hook docs specify.

- On `PreToolUse` for `run_command`, `write_to_file`, `replace_file_content` and `multi_replace_file_content`, it answers `{"decision": "deny", "reason": ...}` for a blocked call and `{"decision": "ask"}` otherwise. `ask` keeps the normal permission prompt and its Always Allow cache. An empty object is treated as a denial and `allow` would skip the prompt, so neither is used.
- It blocks protected-branch, force, bare and deletion pushes, `HEAD` as a push destination, destructive git, `timeout` wrappers behind any shell or wrapper, and edits to secrets, signing material, lock files and `.git/`. Edits to CI definitions are denied here because Antigravity hooks cannot ask for a specific call.

The Swift lint hook in `ios-kit` runs SwiftFormat and SwiftLint on edited `.swift` files when the nearest config file opts in. `PostToolUse` output must be `{}`, so the hook records findings per conversation and the `PreInvocation` hook hands them to the model as an ephemeral message on the next turn.

## Validation

```bash
python3 antigravity/scripts/sync_rules.py --check
python3 antigravity/scripts/validate.py
python3 -m unittest discover -s antigravity/tests -v
python3 -m unittest discover -s shared/tests -v
bash -n antigravity/install.sh
for p in antigravity/plugins/*/; do agy plugin validate "$p"; done
```

The validator checks the documented `plugin.json` keys, agent frontmatter (pinned model, known tools, no write tools, existing skills), hook manifests (events, matchers, commands that resolve inside the plugin, timeouts, byte-identical copies of the shared modules), the generated rules, the home layout, cross-layer leaks and local links. CI runs all of it, plus `agy plugin validate` in a job that is allowed to fail until the CLI installer is pinned.

See the root README, "Keeping standards fresh", for the 90-day audit cadence and the `/toolkit-audit` skill.
