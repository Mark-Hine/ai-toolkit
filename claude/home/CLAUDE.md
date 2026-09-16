# Personal defaults (all projects)

@~/.claude/machine.md

## Git
- Follow the repository's documented Git contribution, branch naming and commit message conventions. When these are absent, use the defaults below.
- Use Conventional Commits with the ticket as scope when available, such as `fix(PROJ-123): handle expired sessions`. Use a lowercase imperative subject of at most 72 characters. Add a short body only when needed to explain what changed and why.
- Keep each commit to one logical change. Stage only the intended files or hunks, inspect the staged diff and exclude unrelated changes, secrets and unintended generated files. Run checks appropriate to the change before committing and report any failed or unavailable checks.
- Before committing, check the current branch. If it is `develop`, `main`, `master`, `release/*` or another branch protected by the project, create and switch to a suitably named feature or task branch before committing.
- Commit and push only when asked. Never push directly to a protected branch. Do not amend commits, rewrite history or force-push without explicit authorization.
- Do not add AI attribution, a generated-by footer or a Co-Authored-By trailer.

## How I want work done
- When changing the ai-toolkit setup, mirror shared changes between `codex/` and `claude/` in the same task, adapting paths and mechanisms for each agent. Preserve intentional agent-specific differences, including the separate writing styles. State any change that is not mirrored and why.
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
