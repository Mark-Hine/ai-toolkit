# ai-toolkit

My portable setup for AI coding agents. One folder per agent.

| Folder | Agent | Status |
| --- | --- | --- |
| [`claude/`](claude/README.md) | Claude Code | Android playbooks, standards, reviewer/researcher/verifier agents, guard hooks, writing-style rules, global `CLAUDE.md`, one-command installer |
| [`codex/`](codex/README.md) | OpenAI Codex | Six skills, specialist agents, global settings, Android and writing guidance, guard hooks, repeatable installer |

`.claude-plugin/marketplace.json` at the repo root is required by Claude Code; it points at the plugins under `claude/plugins/`.

## Install (Codex)

```bash
./codex/install.sh
```

Start a new Codex session and use `/hooks` to review and trust the installed hooks. See [Codex setup](codex/README.md) for migration details, settings, verification and backups.

## Install (Claude Code)

```bash
git clone https://github.com/Mark-Hine/ai-toolkit.git ~/ai-toolkit
~/ai-toolkit/claude/install.sh
```

Plugins only, without the dotfiles layer:

```
/plugin marketplace add Mark-Hine/ai-toolkit
/plugin install android-kit@ai-toolkit
/plugin install pr-review@ai-toolkit
```

## Privacy

Machine-specific facts (AVD names, CLI paths, ticket prefix, default branch) live in `~/.claude/machine.md`. The installer creates it from `claude/home/machine.md.example` and never commits it. Codex machine facts live in `~/.codex/machine.md`. Repo-specific facts belong in that repo's own `AGENTS.md` or `CLAUDE.md`, and the playbooks read them from there rather than hardcoding them. CI runs gitleaks on every push to catch credentials.

## Licence

MIT.
