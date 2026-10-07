# ai-toolkit

My portable setup for AI coding agents. One folder per agent, with shared personal preferences under `shared/`.

[Kotlin guidance](shared/guidance/kotlin.md) applies across platforms through each home loader and installer. Its [source rationale](shared/guidance/references/kotlin-rationale.md) is bundled in each PR review skill and loaded by the Android, Spring Boot and generic packs.

| Folder | Agent | Status |
| --- | --- | --- |
| [`antigravity/`](antigravity/README.md) | Google Antigravity | Six plugins (`android-kit`, `ios-kit`, `web-kit`, `pr-review`, `design-kit`, `toolkit`) carrying nineteen skills, ten specialist agents, rules generated from the Claude rules, and the shared guard and Swift lint hooks. Symlink installer |
| [`claude/`](claude/README.md) | Claude Code | Android, iOS, web and UI/UX design playbooks, standards indexes, reviewer/researcher/verifier agents, guard hooks, writing-style rules, global `CLAUDE.md`, one-command installer |
| [`codex/`](codex/README.md) | OpenAI Codex | Nineteen skills, Android/iOS/web/UI specialist agents, global settings, scoped guidance, guard hooks, repeatable installer |

`.claude-plugin/marketplace.json` at the repo root is required by Claude Code. It points at the plugins under `claude/plugins/`.

## Install (Antigravity)

```bash
./antigravity/install.sh
```

The installer links the plugins into `~/.gemini/config/plugins/` and the shared guidance into `~/.gemini/config/guidance/`, and adds a managed block to `~/.gemini/config/AGENTS.md`. Hooks ship inside each plugin, nothing is registered globally. Restart Antigravity, then check with `agy agents`. See [Antigravity setup](antigravity/README.md).

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
/plugin install guard-kit@ai-toolkit
/plugin install android-kit@ai-toolkit
/plugin install ios-kit@ai-toolkit
/plugin install web-kit@ai-toolkit
/plugin install pr-review@ai-toolkit
/plugin install design-kit@ai-toolkit
/plugin install toolkit@ai-toolkit
```

## Keeping standards fresh

Every rule file, standards reference and pr-review pack carries a `verified:` date and a `sources:` list. Four mechanisms keep them honest.

- `tools/freshness.py` runs in CI on every push and warns at 90 days, fails at 180. The monthly `scheduled` workflow opens or updates a `freshness` issue when anything is due.
- `tools/linkcheck.py` runs monthly over every cited URL, with per-host rules for pages that render client-side or block bots, and opens a `linkcheck` issue when a source is gone.
- `tools/source_anchors.py` confirms that the one or two sentences each source key rests on are still on the live page (`docs/source-anchors.md`). Agents read these anchors and never fetch a page to grade a rule. CI lints the anchor files, and a monthly run opens an `anchors` issue when a quote drifts or a page cannot be read.
- `/toolkit:audit` (`$toolkit-audit` in Codex, `/toolkit-audit` in Antigravity) re-reads each source, classifies every rule, writes `docs/audits/<date>-audit.md` with proposed diffs, and refreshes stamps only for files that pass and only after you confirm.
- `/toolkit:check` (`$toolkit-check` in Codex, `/toolkit-check` in Antigravity) runs the pre-PR checks `AGENTS.md` requires for the files a branch changes and lists layers that may need mirroring. It edits nothing.

Cadence. When the freshness job warns, run the audit from this checkout, land the fixes as small mirrored PRs, then let the skill refresh the stamps. `tools/mirror_parity.py` runs in CI and fails when the three layers drift apart between audits.

## Contributing

Branch, PR, green CI. The rules for changes to this repo are in `AGENTS.md` (Codex), `CLAUDE.md` (Claude Code), and `GEMINI.md` (Antigravity).

## Privacy

Machine-specific facts (AVD names, CLI paths, ticket prefix, default branch) live in `~/.claude/machine.md`. The installer creates it from `claude/home/machine.md.example` and never commits it. Codex machine facts live in `~/.codex/machine.md`. Antigravity machine facts live in `~/.gemini/config/machine.md`. Repo-specific facts belong in that repo's own `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`, and the playbooks read them from there rather than hardcoding them. CI runs gitleaks on every push to catch credentials.

## Licence

MIT.

The source anchors quote short passages from third-party documentation, such as Apple's Human Interface Guidelines, Material Design, the Android and Kotlin documentation, WCAG and MDN. Each quote is at most two sentences, names its page, and is there so a rule can cite the sentence it rests on. Copyright in quoted text stays with its owner, and no page text is committed.
