# pr-review

Produces the formal PR-review deliverable for a code change: a standards-cited findings register
(Blocker / Question / Major / Nit) with concise PR comments written for senior developers, a
scoped-approval statement, per-finding fix-verification criteria, and — for environment-branch
promotions — verification of the merge-base, release list, dependency changes and ticket
references. Every finding is anchored at its root cause, adversarially verified by a second
opinion, then personally re-verified by the lead before it ships.

It carries deep Android and iOS grading criteria as loadable platform packs, and falls back to a
generic pack for any other kind of repo — grading against the repo's own linters, CI config and
conventions first, then the canonical authority for the stack in play, plus OWASP ASVS/Top 10.

## Output

Two artifacts, JSON first:

- **`findings.json`** — the canonical, machine-readable review (schema `pr-review/v1`,
  `references/output.md`): verdict, scope, and per-finding severity, causal `file:line`,
  merge-base behaviour, standard tag, PR comment, and a `verify_fixed_when` criterion that
  re-reviews and the CI poster check fixes against.
- The **markdown review document**, rendered from the JSON (`references/template.md`).

## Modes

- **Local (default):** interactive — infers the repo profile, echoes it back, asks what stays
  ambiguous. Nothing is posted; the human pastes the document into the PR.
- **CI (`PR_REVIEW_MODE=ci`):** headless — never asks, ambiguity resolves to safe defaults, both
  artifacts go to the artifact staging directory, and the pipeline posts `findings.json` to the
  PR via `scripts/post_azdo.py` (inline threads at `file:line`, a summary thread, a reviewer
  vote; idempotent across re-runs). Wiring, an Azure DevOps example, and gating semantics:
  `references/ci.md`.

## What it is not

- **Not the built-in `/code-review`** — that gives quick inline findings on a working-tree diff.
  This produces the written review that gets posted to the PR and defended with its author.
- **Not a codebase assessment** — pre-existing debt belongs to an assessment or audit; this reviews
  only the PR delta and cross-references a standing register if the project has one.
- In local mode it never posts, commits, or sends anything; in CI mode posting is done by the
  pipeline under its own credentials and configuration, not by the skill deciding to.

## Usage

Run it from inside the repo being reviewed:

```
/pr-review                              # infers source/target, asks what it can't
/pr-review main..feature/checkout       # explicit range
/pr-review staging → production         # promotion mode
/pr-review PR 1234                      # by PR number
/pr-review re-review                    # prior review exists, head has moved
/pr-review ci: …                        # headless CI conduct (or PR_REVIEW_MODE=ci)
```

**Promotion mode** activates automatically when both endpoints are environment branches — it adds
manifest verification and the full scoping statement. Everything else runs feature mode with the
same findings machinery and a simple scope line.

## What it works out for itself

At Phase 0 the skill infers, echoes for correction, and asks only when genuinely ambiguous (in CI:
never asks — defaults, with every inference recorded in the JSON): the platform (Android / iOS /
generic), the environment-branch vocabulary this repo actually uses, the ticket key pattern from
commit history, whether a standing quality register exists, the reviewing org for the footer, and
whether a paired repo has a matching review. Nothing to configure and no state to maintain — it
works on a repo it has never seen.

## Prerequisites

Run inside a git repo with history fetched. Everything else is optional and degrades with a note
rather than failing: no register means that section is skipped, no ticket key means reconciliation
is skipped, no paired repo means no twins table.

## Install

See the repo root README — symlink recommended:

```bash
ln -s "$(pwd)/claude-skills/pr-review" ~/.claude/skills/pr-review
```

## Structure

```
pr-review/
├── SKILL.md                  # phased protocol (0 setup/profile/mode · 1 manifest · 2 fan-out ·
│                             #  2a adversarial verification · 3 lead verification · 3.5 emit JSON ·
│                             #  4 register · 5 twins · 6 render+deliver · R re-review)
├── scripts/
│   └── post_azdo.py          # findings.json → Azure DevOps PR threads + reviewer vote (stdlib-only)
└── references/
    ├── protocol.md           # §1–§12 rules of engagement (delta-only, severity vocabulary,
    │                         #  verification discipline, churn honesty, re-review rules);
    │                         #  §13–§16 grading rules shared by every platform;
    │                         #  §17–§24 extensions (root cause, verification criteria, SHA
    │                         #  ancestry, debug variants, adversarial pass, retractions,
    │                         #  severity negotiation, CI conduct)
    ├── template.md           # document section contract and default wording (rendered from JSON)
    ├── output.md             # findings.json schema (pr-review/v1) and rendering rules
    ├── ci.md                 # pipeline wiring: Azure DevOps example, gating, other CI systems
    └── platforms/
        ├── android.md        # architecture, state/Compose/coroutines, MASVS, a11y, standards block
        ├── ios.md            # SwiftUI/concurrency, MASVS, a11y, standards block, consensus cap
        └── generic.md        # any other stack: the repo's own adopted standards first, then the
                              #  canonical authority per stack; deploy/migration ordering
```

Each pack carries its own standards-basis block — pasted straight into the review — its own source
registry of canonical URLs (with link definitions so `[KEY]` references render as links), and its
own list of ceremonies *not* to flag. Exactly one pack loads per review, chosen at Phase 0.
