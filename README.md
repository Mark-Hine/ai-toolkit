# ai-toolkit

My portable setup for AI coding agents. It gives Claude Code, OpenAI Codex and Google Antigravity the same playbooks, specialist agents, standards and safety hooks. Everything is written once under `src/` and `shared/`, and a build script turns it into one folder per agent.

## What's in it

<!-- plugin-versions:start -->
| Kit | What it gives you | Version |
| --- | --- | --- |
| `android-kit` | Feature, bug-fix, dependency-uplift and run-app playbooks for Android, with researcher, reviewer and verifier agents | 1.7.0 |
| `ios-kit` | The same for iOS and SwiftUI, plus SwiftFormat and SwiftLint on edit where a repo opts in | 1.5.0 |
| `web-kit` | Feature, bug-fix and run-app playbooks for React, Next.js and TypeScript, with researcher, reviewer and verifier agents | 1.1.0 |
| `design-kit` | Tiered UI design rules (HIG, Material 3, WCAG 2.2, house), a design playbook and a UI reviewer agent | 1.9.0 |
| `pr-review` | A formal written PR review with a standards-cited findings register, posted to Azure DevOps or GitHub when asked | 1.5.1 |
| `guard-kit` | A hook that blocks protected-branch and force pushes, destructive git and edits to secrets | 1.3.0 |
| `toolkit` | Audit and pre-PR check skills for maintaining this repo | 1.4.4 |
<!-- plugin-versions:end -->

Versions are the Claude Code plugin versions, which installs pin to. `scripts/build/build.py` keeps this column current.

`shared/guidance/` holds the Git, Kotlin, design and writing preferences that every agent loads.

## Install

1. Clone the repo once and keep the checkout, because the installers link to it.

   ```bash
   git clone https://github.com/Mark-Hine/ai-toolkit.git ~/ai-toolkit
   ```

2. Run the installer for each agent you use.

   | Agent | Needs | Run | Then |
   | --- | --- | --- | --- |
   | Claude Code | `claude`, `git`, `jq` | `~/ai-toolkit/claude/install.sh` | Start a new session |
   | Codex | Codex CLI, Python 3.11 | `~/ai-toolkit/codex/install.sh` | Start a new session and open `/hooks` to trust the hooks |
   | Antigravity | `agy` or the IDE, Python 3.11 | `~/ai-toolkit/antigravity/install.sh` | Restart Antigravity and check with `agy agents` |

The installers keep your own settings, back up anything they replace, and create a `machine.md` for facts about your machine. Add `--dry-run` to the Codex or Antigravity installer to preview its changes. Each agent's README explains what its installer writes: [Claude Code](claude/README.md), [Codex](codex/README.md) and [Antigravity](antigravity/README.md).

To use only the Claude Code plugins, without the dotfiles layer, add the marketplace inside Claude Code and install the kits you want:

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

The Android, iOS and web kits depend on `guard-kit` and `design-kit`. The marketplace file Claude Code reads is `.claude-plugin/marketplace.json`.

## Update

Pull the checkout, then rerun the installer for each agent you use:

```bash
git -C ~/ai-toolkit pull
~/ai-toolkit/claude/install.sh
~/ai-toolkit/codex/install.sh
~/ai-toolkit/antigravity/install.sh
```

The rerun matters. Claude Code plugins are pinned to a version, and the Codex installer copies its agents and settings, so neither picks up a change until the installer runs again.

## Releases

When a plugin's version changes on `main`, CI tags it as `<plugin>--v<version>`, such as `pr-review--v1.5.1`, and publishes a GitHub Release listing the commits since that plugin's previous release. To pin a CI pipeline or a shared setup to a release, add the marketplace at that tag:

```
claude plugin marketplace add "Mark-Hine/ai-toolkit#pr-review--v1.5.1"
```

## How it works

Each agent folder is partly generated and partly hand-written. The generated files are committed, so installing never needs the build. `.gitattributes` lists them, and CI fails when one no longer matches its source.

| Source | What it holds | Built into |
| --- | --- | --- |
| `src/skills/` | Skills with their references and scripts | Each agent's skill folders |
| `src/agents/` | Researcher, reviewer and verifier agents | Claude and Antigravity Markdown agents, Codex TOML agents |
| `src/rules/` | Path-scoped platform rules | `claude/home/rules/`, `codex/home/guidance/` and the Antigravity plugin rules |
| `shared/hooks/` | The guard and Swift lint hooks | The hook copies in each agent folder |
| `scripts/build/agents.toml` | Each agent's wording, capabilities, model tiers and agent settings | Every generated file |

A source is Markdown with two additions. A token such as `{@project_file}` becomes each agent's wording, so it renders as `CLAUDE.md` for Claude and `AGENTS.md` for Codex. A block such as `<!-- if: plan_mode -->` keeps text only for agents with that capability. To change a skill, agent or rule, edit its source and run `python3 scripts/build/build.py`.

Plugin manifests, hook registration, home instructions, settings and installers stay hand-written in each agent folder.

## Adding an agent

A new agent needs these pieces:

1. An adapter in `scripts/build/targets/<agent>.py` that subclasses `Target`, registered in `scripts/build/targets/__init__.py`. It says where skills and agents go and how their frontmatter looks.
2. A `[targets.<agent>]` table in `scripts/build/agents.toml` with its tokens, formats, capabilities, model tiers, preambles and agent roles, plus its hook copies in the `[[copies]]` tables.
3. A render branch for its hook output in `shared/hooks/guard.py`, with tests in `shared/tests/`, and its own hook registration.
4. An `<agent>/` folder with its home instructions, `machine.md.example`, installer, validator, tests and a CI job. A Python installer can subclass `Installer` in `shared/install_common.py` for dry runs, backups, the managed `AGENTS.md` block, `machine.md` and the shared guidance links.
5. A `ci_cli` value and a block in `src/skills/pr-review/pr-review/references/ci.md` if pr-review should run in that agent's CI mode.

## Keeping standards fresh

Every rule, standards reference and pr-review pack carries a `verified:` date and a `sources:` list. These tools keep them current:

| Tool | Runs | What it does |
| --- | --- | --- |
| `tools/freshness.py` | Every push, and monthly | Warns at 90 days and fails at 180. The monthly `scheduled` workflow opens a `freshness` issue when anything is due |
| `tools/linkcheck.py` | Monthly | Checks every cited URL and opens a `linkcheck` issue when a source is gone |
| `tools/source_anchors.py` | Every push (lint), and monthly | Confirms that the sentence each source key rests on is still on the live page ([format](docs/source-anchors.md)), and opens an `anchors` issue when a quote drifts |
| `/toolkit:audit` | By hand | Re-reads each source, writes `docs/audits/<date>-audit.md` with proposed fixes, and refreshes stamps only after you confirm |

When the freshness job warns, run the audit from this checkout, land each fix as a small PR against its source, then let the audit refresh the stamps. In Codex the skills are `$toolkit-audit` and `$toolkit-check`, and in Antigravity `/toolkit-audit` and `/toolkit-check`.

## Contributing

Branch, open a PR and wait for green CI. `AGENTS.md` has the rules for this repo, and `CLAUDE.md` and `GEMINI.md` point to it. Run `/toolkit:check` before opening a PR. It runs the checks the changed files need and edits nothing.

## Privacy

Machine facts such as emulator names, CLI paths, the ticket prefix and the default branch live in `machine.md` in each agent's config folder (`~/.claude/`, `~/.codex/` or `~/.gemini/config/`). The installers create it from a template and it is never committed. Facts about one repo belong in that repo's own `AGENTS.md`, `CLAUDE.md` or `GEMINI.md`. CI runs gitleaks on every push to catch credentials.

## Licence

MIT.

The source anchors quote short passages from third-party documentation, such as Apple's Human Interface Guidelines, Material Design, the Android and Kotlin documentation, WCAG and MDN. Each quote is at most two sentences, names its page, and is there so a rule can cite the sentence it rests on. Copyright in quoted text stays with its owner, and no page text is committed.
