# Working in this repository

Read by Codex directly and by Claude Code through `CLAUDE.md`. Applies to every change in this repo.

## Branch and PR
- `main` is protected. Never commit on it or push to it. Every change goes on a branch named `type/short-slug` (`feat/`, `fix/`, `docs/`, `chore/`) and lands through a pull request that CI has passed.
- One logical change per PR. Conventional Commits, no ticket scope needed here (`fix(android-kit): …`, `docs: …`).
- No AI attribution in commits or PR text.

## Before opening a PR
- `bash scripts/check-private-terms.sh` must print "No private terms found." Nothing in this repo may name an employer, a work repository, a colleague, a device or a machine path.
- `bash claude/plugins/android-kit/hooks/test-guards.sh` must pass when a hook changed.
- `claude plugin validate .` must pass when anything under `claude/plugins/` or `.claude-plugin/` changed.
- `python3 codex/scripts/validate.py` must pass when anything under `codex/` changed.

## Mirroring
- Shared conventions live in both `claude/` and `codex/`. A change to one is mirrored to the other in the same PR, adapted to each agent's mechanism (Claude plugins, hooks and `~/.claude/rules`; Codex `AGENTS.md`, `config.toml`, agent TOML and Python hooks). Intentional differences, including the two writing styles, stay. The PR description names anything not mirrored and why.

## Layout rules
- Plugins ship only what applies to every repo. Repo-specific facts belong in that repo's own `CLAUDE.md` or `AGENTS.md`.
- Rules carry the rule; rationale and code samples go in a `standards` skill's `references/`.
- Machine facts (simulators, AVDs, CLI paths, ticket prefixes) go in `machine.md`, never in tracked files.
