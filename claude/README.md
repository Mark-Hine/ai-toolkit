# Claude Code setup

Two layers. Plugins carry the shareable parts. The `home/` dotfiles layer carries what plugins cannot ship: `~/.claude/CLAUDE.md`, path-scoped rules and personal settings.

## Layout

| Path | What | Loads |
| --- | --- | --- |
| `plugins/android-kit/skills/` | `/android-kit:feature`, `bugfix`, `uplift-deps`, `run-app`, `standards` (reference index, not user-invoked) | On invocation or when relevant |
| `plugins/android-kit/agents/` | `android-reviewer` (opus, read-only, grades Blocker/Major/Nit), `android-researcher` (sonnet, read-only, official docs only), `android-verifier` (sonnet, runs tests and emulator journeys, reports evidence) | When delegated |
| `plugins/guard-kit/hooks/` | One PreToolUse guard shared with the Codex and Antigravity layers. Blocks pushes to protected branches, force and delete pushes, bare pushes, destructive git, `timeout`-wrapped commands and edits to secrets and signing files, and limits the researcher and verifier agents to their documented commands. android-kit and ios-kit depend on it | Every `Bash`, `Edit`, `Write`, `NotebookEdit` call |
| `plugins/ios-kit/skills/` | `/ios-kit:feature`, `bugfix`, `uplift-deps`, `run-app`, `standards` (Apple docs index plus a per-repo `CLAUDE.md` template) | On invocation or when relevant |
| `plugins/ios-kit/agents/` | `ios-reviewer` (opus, read-only), `ios-researcher` (sonnet, read-only, Apple docs only), `ios-verifier` (sonnet, runs tests and simulator smoke checks) | When delegated |
| `plugins/ios-kit/hooks/` | SwiftFormat and SwiftLint after `.swift` edits, only where the nearest config file opts in. SwiftLint errors block, warnings come back as context | On matching edits |
| `plugins/pr-review/skills/pr-review/` | Formal written PR review with a standards-cited findings register, grading Android, iOS, Spring Boot, React/Next.js and generic repos | On "review this PR" or `/pr-review:pr-review` |
| `plugins/design-kit/skills/` | `/design-kit:iterate` (design playbook with the `DESIGN.md` contract, rendered options and the user's pick), `standards` (sources, rationale and platform APIs for the tiered design rules) | On invocation or when relevant |
| `plugins/design-kit/agents/` | `ui-reviewer` (opus, read-only, grades UI diffs against the tiered design rules, citing rule ID and source) | When delegated |
| `plugins/toolkit/skills/` | `/toolkit:audit` (re-checks the standards against their sources and writes a findings register, invoked by hand) | On invocation |
| `home/CLAUDE.md` | Global preferences: subagent models, Android and iOS routing. Imports `~/.claude/machine.md` | Every session |
| `../shared/guidance/common.md` | Shared Git and work preferences, linked as `~/.claude/rules/common.md` | Every session |
| `../shared/guidance/kotlin.md` | Kotlin domain modeling and compatibility across platforms, linked as `~/.claude/rules/kotlin.md` | On matching `.kt` and `.kts` files |
| `../shared/guidance/design-assets.md` | Pointer to the design contract and the iterate skill, linked as `~/.claude/rules/design-assets.md` | On matching `DESIGN.md`, token, stylesheet, theme, SVG and icon files |
| `../shared/guidance/design-standards.md` | Tiered design rules with IDs and source keys (T1 official, T2 house), linked as `~/.claude/rules/design-standards.md` | Every session |
| `home/rules/writing-style.md` | Plain-prose rules with a source key per rule (GOV.UK, Google, Microsoft, plain-language guidelines, Anthropic). Rationale lives in `../shared/guidance/references/writing-style-rationale.md` | Every session |
| `home/rules/android/` | Kotlin style, Compose, testing, one-shot UI events. Path-scoped, load only when matching files are touched | On matching files |
| `home/rules/ios/` | Swift style, SwiftUI state ownership and design-system use, testing (Swift Testing/XCTest), one-shot model → UI events. Path-scoped | On matching `.swift` files |
| `home/settings.snippet.json` | Style reminder hook, permission allowlist, empty `attribution` so commits and PRs carry no AI trailer. Add your own `skillOverrides` in `~/.claude/settings.json` to hide skills you never use | Merged into `~/.claude/settings.json` |

## Install

```bash
git clone https://github.com/Mark-Hine/ai-toolkit.git ~/ai-toolkit
~/ai-toolkit/claude/install.sh
```

The script symlinks the dotfiles and shared personal preferences, creates `~/.claude/machine.md` from `home/machine.md.example` if missing, merges the settings snippet without overwriting your own keys (backups are written beside the file), adds the marketplace and installs the six plugins. Re-run it after `git pull`. Requires `claude`, `git`, `jq`.

## Customise

- Machine facts (AVD names, default simulator, CLI paths, ticket prefix, default branch): edit `~/.claude/machine.md`. Never commit it.
- Repo facts belong in that repo's `CLAUDE.md`. The playbooks read module names, build commands and design-system names from there and never hardcode them.
- Precedence: a project `CLAUDE.md` and these rules win over any skill. Conflicts are followed the rule's way and reported.

## Design principles

- Shared content is platform-scoped, never repo-scoped. Repo breakage is documented in that repo, not enforced here.
- Rules carry only the rule. Rationale and code samples live in skill references. The shared Kotlin rationale is mirrored into every PR review skill as `references/languages/kotlin.md`.
- Subagents pin models. Research is cheap (sonnet), but review needs judgement (opus). Never `inherit`.
- Guard hooks are deterministic and repo-agnostic. One Python module under `shared/hooks/` serves all three layers, and the plugin and Codex copies are kept identical by CI. Agent command limits come from the same module, keyed on the `agent_type` the hook input carries.

See the root README, "Keeping standards fresh", for the 90-day audit cadence and the `/toolkit:audit` skill.
