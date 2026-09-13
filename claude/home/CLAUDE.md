# Personal defaults (all projects)

@~/.claude/machine.md

## Git
- Commits: Conventional Commits, ticket as scope, e.g. `chore(PROJ-123): target Android 17 (API 37)`; lowercase
  imperative subject ≤72 chars; body ≤3 short lines (what and why), no file lists.
- Commit or push only when asked. Never push to `develop`, `main` or `release/*`. One commit per logical change.
  No AI attribution anywhere, so no `Co-Authored-By` trailer and no "Generated with Claude Code" footer.

## How I want work done
- Plan mode before touching more than one file or any dependency version. Small clear fixes: just do them. Minimal
  diff, no unrelated refactors, renames or reformatting.
- Writing follows `~/.claude/rules/writing-style.md` in every reply, PR text and commit body.
- Evidence over assertion: any "compiles", "tests pass" or "renders" claim quotes the command and its result;
  cite code as `file:line`; otherwise write "Unverified". Report failures and skipped steps as such.
- Decide routine things yourself and state the assumption. Ask first before: push, force push, deleting files,
  editing secrets/signing/network-security config, or changing the task's scope.

## Subagents
- Always pin `model`; never `inherit`. Research/fetch agents: `sonnet`. Review/judgement agents: `opus`.

## Android/Kotlin work
- Before implementing, check `/skills` for an installed skill that covers the task and load it. Official Android skills
  (`testing-setup`, `edge-to-edge`, `adaptive`, `agp-9-upgrade`, `r8-analyzer`, `android-intent-security`) are procedures; follow them.
- Precedence: the project `CLAUDE.md` and the rules in `~/.claude/rules/` win over any skill. If a skill and a rule
  conflict, follow the rule and state the conflict in the report. If a skill and official docs conflict, ask `android-researcher`.
- Route Kotlin/Compose design questions through `using-chrisbanes-skills`; use the `/android-kit:*` playbooks; platform
  facts via `android-researcher`, never memory; non-trivial diffs to `android-reviewer` before "done".
