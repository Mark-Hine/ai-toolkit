# ai-toolkit

My portable setup for AI coding agents. One folder per agent, with shared personal preferences under `shared/`.

| Folder | Agent | Status |
| --- | --- | --- |
| [`antigravity/`](antigravity/README.md) | Google Antigravity | Eleven skills, Android/iOS specialist agents, plugin architecture, lifecycle hooks (`PreToolUse`, `PostToolUse`), scoped guidance, repeatable installer |
| [`claude/`](claude/README.md) | Claude Code | Android and iOS playbooks, standards indexes, reviewer/researcher/verifier agents, guard hooks, writing-style rules, global `CLAUDE.md`, one-command installer |
| [`codex/`](codex/README.md) | OpenAI Codex | Eleven skills, Android/iOS specialist agents, global settings, scoped guidance, guard hooks, repeatable installer |

`.claude-plugin/marketplace.json` at the repo root is required by Claude Code; it points at the plugins under `claude/plugins/`.

## Install (Antigravity)

```bash
./antigravity/install.sh
```

Inspect the installed configuration in `~/.gemini/antigravity-cli/` and review registered hooks in `hooks.json`. See [Antigravity setup](antigravity/README.md) for details on plugins, skills, hooks, and verification.

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
/plugin install ios-kit@ai-toolkit
/plugin install pr-review@ai-toolkit
```

## Contributing

Branch, PR, green CI. The rules for changes to this repo are in `AGENTS.md` (Codex), `CLAUDE.md` (Claude Code), and `GEMINI.md` (Antigravity).

## Privacy

Machine-specific facts (AVD names, CLI paths, ticket prefix, default branch) live in `~/.claude/machine.md`. The installer creates it from `claude/home/machine.md.example` and never commits it. Codex machine facts live in `~/.codex/machine.md`. Antigravity machine facts live in `~/.gemini/antigravity-cli/machine.md`. Repo-specific facts belong in that repo's own `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`, and the playbooks read them from there rather than hardcoding them. CI runs gitleaks on every push to catch credentials.

## Licence

MIT.
