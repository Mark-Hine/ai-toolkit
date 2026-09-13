# Claude Code setup

Two layers. Plugins carry the shareable parts. The `home/` dotfiles layer carries what plugins cannot ship: `~/.claude/CLAUDE.md`, path-scoped rules and personal settings.

## Layout

| Path | What | Loads |
| --- | --- | --- |
| `plugins/android-kit/skills/` | `/android-kit:feature`, `bugfix`, `uplift-deps`, `run-app`, `standards` (reference index, not user-invoked) | On invocation or when relevant |
| `plugins/android-kit/agents/` | `android-reviewer` (opus, read-only, grades Blocker/Major/Nit), `android-researcher` (sonnet, read-only, official docs only) | When delegated |
| `plugins/android-kit/hooks/` | Guard hooks: block pushes to protected branches, force pushes, destructive git, `timeout`-wrapped commands, edits to secrets and signing files | Every matching tool call |
| `plugins/pr-review/` | Formal written PR review with a standards-cited findings register; Android, iOS and generic grading | On "review this PR" or `/pr-review` |
| `home/CLAUDE.md` | Global preferences: commits, work style, subagent models, Android routing. Imports `~/.claude/machine.md` | Every session |
| `home/rules/writing-style.md` | Plain-prose rules: no em dashes, no colon-hinged sentences, no announcing, tables over paragraphs | Every session |
| `home/rules/android/` | Kotlin style, Compose, testing, one-shot UI events. Path-scoped, load only when matching files are touched | On matching files |
| `home/settings.snippet.json` | Style reminder hook, hidden skills, permission allowlist, `includeCoAuthoredBy: false` | Merged into `~/.claude/settings.json` |

## Install

```bash
git clone https://github.com/Mark-Hine/ai-toolkit.git ~/ai-toolkit
~/ai-toolkit/claude/install.sh
```

The script symlinks the dotfiles, creates `~/.claude/machine.md` from `home/machine.md.example` if missing, merges the settings snippet without overwriting your own keys (backups are written beside the file), adds the marketplace and installs both plugins. Re-run it after `git pull`. Requires `claude`, `git`, `jq`.

## Customise

- Machine facts (AVD names, CLI paths, ticket prefix, default branch): edit `~/.claude/machine.md`. Never commit it.
- Repo facts belong in that repo's `CLAUDE.md`. The playbooks read module names, build commands and design-system names from there and never hardcode them.
- Precedence: a project `CLAUDE.md` and these rules win over any skill. Conflicts are followed the rule's way and reported.

## Design principles

- Shared content is platform-scoped, never repo-scoped. Repo breakage is documented in that repo, not enforced here.
- Rules carry only the rule; rationale and code samples live in `plugins/android-kit/skills/standards/references/`.
- Subagents pin models. Research is cheap (sonnet); review needs judgement (opus). Never `inherit`.
- Guard hooks are deterministic and repo-agnostic. Agent tool restrictions live beside the agent, not in the shared hooks.
