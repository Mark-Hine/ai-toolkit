# Working in this repository

Read by Codex directly, by Claude Code through `CLAUDE.md`, and by Antigravity through `GEMINI.md`. Applies to every change in this repo.

## Branch and PR
- `main` is protected. Never commit on it or push to it. Every change goes on a branch named `type/short-slug` (`feat/`, `fix/`, `docs/`, `chore/`) and lands through a pull request that CI has passed.
- One logical change per PR. Conventional Commits, no ticket scope needed here (`fix(android-kit): …`, `docs: …`).
- No AI attribution in commits or PR text.

## Before opening a PR
- Run the validation checks required by the files changed. Report failed or unavailable checks in the PR.
- `bash claude/plugins/android-kit/hooks/test-guards.sh` must pass when a hook changed.
- `claude plugin validate .` must pass when anything under `claude/plugins/` or `.claude-plugin/` changed.
- `python3 codex/scripts/validate.py` must pass when anything under `codex/` changed.
- `python3 antigravity/scripts/validate.py` and `python3 -m unittest discover -s antigravity/tests` must pass when anything under `antigravity/` changed.

## Mirroring
- Shared conventions live in `claude/`, `codex/`, and `antigravity/`. A change to one is mirrored to the others in the same PR, adapted to each agent's mechanism (Claude plugins, hooks and `~/.claude/rules`; Codex `AGENTS.md`, `config.toml`, agent TOML and Python hooks; Antigravity `plugins/`, `hooks.json`, `GEMINI.md`/`AGENTS.md` and Python hooks). Intentional differences, including writing styles, stay. The PR description names anything not mirrored and why.

## Layout rules
- Plugins ship only what applies to every repo. Repo-specific facts belong in that repo's own `CLAUDE.md` or `AGENTS.md`.
- Rules carry the rule; rationale and code samples go in a `standards` skill's `references/`.
- Machine facts (simulators, AVDs, CLI paths, ticket prefixes) go in `machine.md`, never in tracked files.
