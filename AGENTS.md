# Working in this repository

Read by Codex directly, by Claude Code through `CLAUDE.md`, and by Antigravity through `GEMINI.md`. Applies to every change in this repo.

## Branch and PR
- `main` is protected. Never commit on it or push to it. Every change goes on a branch named `type/short-slug` (`feat/`, `fix/`, `docs/`, `chore/`) and lands through a pull request that CI has passed.
- One logical change per PR. Conventional Commits, no ticket scope needed here (`fix(android-kit): …`, `docs: …`).
- No AI attribution in commits or PR text.

## Before opening a PR
- Run the validation checks required by the files changed. Report failed or unavailable checks in the PR.
- `python3 -m unittest discover -s shared/tests` and `bash claude/tests/test-guards.sh` must pass when a hook changed. Hook modules are canonical under `shared/hooks/`. Edit them there and run `python3 scripts/build/build.py` to refresh the plugin and Codex copies.
- `python3 -m unittest discover -s claude/tests` must pass when `claude/install.sh` or anything under `claude/home/` changed.
- `claude plugin validate . --strict` and `claude plugin validate claude/plugins/<name> --strict` must pass when anything under `claude/plugins/` or `.claude-plugin/` changed. Bump `version` in that plugin's `plugin.json` whenever its files change, because installs pin to the version.
- `python3 scripts/build/build.py --check`, `python3 scripts/ci/check_repo.py`, `python3 scripts/ci/check_style.py` and `python3 tools/freshness.py` must pass on every change. A rule or reference you touch keeps its `verified:` date unless you re-read its sources. The style check enforces the dash and banned-word rules of `claude/home/rules/writing-style.md` on tracked prose. It checks sources and `scripts/build/agents.toml`, not generated files. Add a quoted source that needs a dash to `scripts/ci/style-exceptions.txt`.
- `python3 -m unittest discover -s scripts/build/tests` must pass when anything under `scripts/build/` or `src/` changed.
- `python3 codex/scripts/validate.py` and `python3 -m unittest discover -s codex/tests` must pass when anything under `codex/` changed.
- `python3 antigravity/scripts/validate.py` and `python3 -m unittest discover -s antigravity/tests` must pass when anything under `antigravity/` changed.

## Generated files
- `scripts/build/build.py` generates agent files from agent-neutral sources. Sources live in `src/` (templates with `{@token}` wording and `<!-- if: capability -->` blocks) and `shared/` (files copied as they are). Per-agent wording, capabilities and copy targets are in `scripts/build/agents.toml`.
- Never edit a generated file. Edit its source and run the build. The generated paths are listed in `.gitattributes`. The platform rules under `claude/home/rules/{android,ios,web}/`, `codex/home/guidance/{android,ios,web}/` and `antigravity/plugins/*/rules/` come from `src/rules/`.

## Mirroring
- Skills, agents, platform rules and hook scripts are written once in `src/` or `shared/` and built into `claude/`, `codex/` and `antigravity/`. A difference between agents is a token value or a capability block in the source, never a hand edit in one layer.
- The per-agent files the build does not write, such as plugin manifests, hook registration, home instruction files, settings and installers, are mirrored by hand in the same PR, adapted to each agent's mechanism. Claude uses plugins, hooks and `~/.claude/rules`. Codex uses `AGENTS.md`, `config.toml`, agent TOML and Python hooks. Antigravity uses `plugins/`, `hooks.json`, `GEMINI.md`/`AGENTS.md` and Python hooks. Intentional differences, including writing styles, stay. The PR description names anything not mirrored and why.

## Layout rules
- Plugins ship only what applies to every repo. Repo-specific facts belong in that repo's own `CLAUDE.md` or `AGENTS.md`.
- Rules carry the rule. Rationale and code samples go in a `standards` skill's `references/`.
- Machine facts (simulators, AVDs, CLI paths, ticket prefixes) go in `machine.md`, never in tracked files.
