# Codex setup

The Codex port of the Claude setup includes eleven skills, six specialist agents, personal instructions, Android, iOS and writing guidance, command permissions, and lifecycle hooks. The Claude setup remains available in `../claude/`.

## Install

Requires Codex CLI and Python 3.11 or later. The installer itself needs no third-party Python packages, credentials or network access.

```bash
./codex/install.sh --dry-run
./codex/install.sh
```

Start a new Codex session, then open `/hooks` to review and trust the command guard, Swift lint hook and each specialist's guard. Codex skips untrusted hooks. Open `/skills` to check discovery. Rerun the installer after pulling toolkit updates. It preserves existing config values, unrelated hooks, personal instructions and machine facts. It backs up displaced files, symlinks and directories under `~/.codex/backups/ai-toolkit-<timestamp>/`, with original locations recorded in `manifest.json`.

`CODEX_HOME` or `--codex-home PATH` selects the config directory. Personal skills install under `~/.agents/skills`. `--skills-home PATH` is useful for isolated checks, but custom locations must themselves be a Codex-discovered skill directory to activate skills. Keep this checkout available because skills, guidance and command rules are symlinked to it. Agent files and merged settings are regenerated on reinstall.

## Installed layout

| Source | Global destination | Purpose |
| --- | --- | --- |
| `home/AGENTS.md` | `~/.codex/AGENTS.md` managed block | Routing to shared preferences, writing, Android and iOS guidance |
| `../shared/guidance/common.md` | `~/.codex/guidance/common.md` | Shared Git and work preferences used by both agents |
| `home/guidance/` | `~/.codex/guidance/` | Writing preferences and scoped Android/iOS rules |
| `home/config.defaults.toml` | Merged into `~/.codex/config.toml` | Model, reasoning, approval, sandbox, web search and agent defaults |
| `home/toolkit.rules` | `~/.codex/rules/ai-toolkit.rules` | Routine command escalation permissions |
| `home/machine.md.example` | `~/.codex/machine.md`, created only if absent | Private machine facts |
| `skills/` | `~/.agents/skills/` | Reusable workflows with their references and scripts |
| `agents/` | `~/.codex/agents/` | Reviewer, researcher and verifier with pinned models and role hooks |
| `hooks/` | Referenced by merged `~/.codex/hooks.json` | Command/patch guard and opt-in Swift lint |

## Skills and agents

| Invocation or role | Behavior |
| --- | --- |
| `$android-feature` | Pattern discovery, scoped plan, implementation, tests and device verification |
| `$android-bugfix` | Reproduction, root cause, focused fix and regression evidence |
| `$android-uplift-deps` | Explicitly invoked dependency/toolchain uplift with compatibility research |
| `$android-run-app` | Explicitly invoked build, install, launch and screenshot workflow |
| `$android-standards` | Android, Kotlin, Gradle, NIA, JetSnack and house-pattern reference index |
| `$ios-feature` | Pattern discovery, scoped plan, implementation, tests and simulator checks |
| `$ios-bugfix` | Reproduction, root cause, minimal fix and regression evidence |
| `$ios-uplift-deps` | Explicitly invoked Xcode/Swift/dependency uplift |
| `$ios-run-app` | Explicitly invoked simulator build, install, launch and screenshots |
| `$ios-standards` | Apple/Swift/Xcode docs, house patterns and a project instructions template |
| `$pr-review` | Formal JSON and Markdown review, release-promotion checks and re-review tracking |
| `android-reviewer`, `ios-reviewer` | `gpt-6-astra`, high reasoning, read-only code review |
| `android-researcher`, `ios-researcher` | `gpt-5.6-terra`, medium reasoning, read-only official-source research |
| `android-verifier`, `ios-verifier` | `gpt-5.6-terra`, medium reasoning, workspace writes for build/test outputs and device evidence |

Existing main-session model settings win. Fresh installations default to `gpt-6-astra` and high reasoning, `on-request` approvals, `workspace-write` sandboxing and live web search. Subagent concurrency is capped at three unless already configured. No login token, MCP credential or broad project trust is added.

## Migration decisions

- `CLAUDE.md` becomes `AGENTS.md`. Project `CLAUDE.md` is a fallback when no `AGENTS.md` exists. Existing project Claude rules can still be read during transition.
- Codex does not automatically apply the Claude `paths` frontmatter in these Markdown rules. Global instructions explicitly route the agent to the relevant guidance files.
- Claude slash commands become `$skill-name` invocations. Dependency uplift and run-app retain explicit invocation. Standards remains available for automatic discovery because it supplies references.
- Plans precede multi-file edits and dependency work. Already authorized work proceeds without another approval gate. Commits and pushes require the user's request.
- Claude model aliases, tool lists, persistent agent memory and max-turn metadata are replaced with supported Codex agent configuration. Reviewer/researcher use a read-only sandbox. The verifier can write build artifacts but its hooks block direct source edits and constrain shell commands.
- Command rules migrate the routine allowlist. `git branch` is narrowed to `git branch --list` because the broader prefix also permits branch mutation. Attribution is controlled by global instructions.
- PR-review references retain Android, iOS and generic grading. Azure DevOps posting remains an explicitly invoked pipeline helper. The CI example now uses Codex but has not been run against an Azure pipeline.
- External Android skills, `using-chrisbanes-skills`, Android CLI, SDK packages and AVDs are not bundled. Discover installed tools and use the documented SDK/official-documentation fallback. Device verification remains unavailable when the necessary SDK or emulator is absent.

## Configuration ownership

Repository contribution and mirroring rules live in the root `AGENTS.md`; root `CLAUDE.md` imports it. Shared personal Git and work preferences live in `shared/guidance/common.md`, linked into each agent's installed guidance. Home instructions contain agent-specific loading and routing. Skills contain task procedures, scoped rules contain coding conventions, and references hold rationale and examples. Role model settings are authoritative in agent TOML.

The installer replaces only its managed instruction block and hooks, preserving unrelated settings. Reinstalling removes the old Codex writing-reminder hook and does not duplicate guard or lint hooks. The writing guide is read through the home instructions instead of being repeated every prompt. Claude keeps its separate writing style and reminder.

## iOS migration

The five skills, three specialists, four scoped rules and standards references mirror the Claude iOS toolkit. Claude-only metadata is replaced with Codex skill policies, role TOML and hooks. Optional Xcode integrations are discovered rather than required. Research and review remain read-only; test artifacts are written by the verifier. Reviewer build requests go to the verifier. Simulator checks target the selected UDID and restore prior visual settings.

The Swift lint hook handles `apply_patch`, `Edit` and `Write`. It runs installed SwiftFormat/SwiftLint only when the edited file's repository has the corresponding config. It reports findings without rewriting files. Shell-based edits are outside this hook's coverage. Xcode, simulators and linters are not installed by the toolkit; their live execution must be verified in an app repository.

Intentional differences remain. Codex uses its existing stricter push policy, including explicit literal refspecs and no remote deletion. Its specialist commands are single invocations without shell filters. Source references preserve the upstream guidance and dates; this port does not revalidate every Apple example or version claim. Recheck those sources when applying them.

## Guard coverage

The command hook blocks protected-branch pushes, force pushes, unchecked implicit pushes, destructive Git operations and `timeout` wrappers. Use an explicit remote and feature refspec when pushing. The patch hook checks added, updated, deleted and moved paths for secrets, signing files, Firebase/network configuration, generated binaries, iOS entitlements, export options and dependency lock files. Regenerate lock files with the package manager instead of editing them. Specialist hooks also block direct source edits and limit research or verification commands.

Push flags are checked within their own shell segment, including combined force flags such as `-uf`.

The command check excludes literal quoted heredoc bodies and checks `timeout` in command positions. Document text and ordinary arguments can mention the wrapper. Commands before and after a heredoc, literal shell `-c` arguments, and simple command substitutions remain checked. Unquoted heredoc bodies remain subject to conservative checks because the shell can expand commands in them.

These hooks prevent common mistakes. They are not a shell sandbox or a complete parser for scripts, Git aliases, computed commands, alternate file-writing tools or shell-based file writes. Keep the Codex sandbox and approval policy enabled. Do not work around a hook block. Review changed hook scripts after updating the toolkit. Managed client policy can take precedence over user settings.

## Validation

```bash
python3 -m unittest discover -s codex/tests -v
python3 codex/scripts/validate.py
bash -n codex/install.sh
```

The tests exercise actual guard inputs and installer behavior, including preservation, backups, repeated installs, dry runs and malformed configuration. CI validates skill frontmatter, local links, TOML and source syntax. The iOS port adds specialist command, Swift lint and installer upgrade coverage.

## Official references

- [Personal instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Skill discovery and invocation](https://learn.chatgpt.com/docs/build-skills)
- [Custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Hooks and required trust review](https://learn.chatgpt.com/docs/hooks)
- [Command rules](https://learn.chatgpt.com/docs/agent-configuration/rules)
- [Non-interactive Codex](https://learn.chatgpt.com/docs/non-interactive-mode)
