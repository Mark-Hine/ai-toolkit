# toolkit

Multi-agent orchestration and maintenance of the ai-toolkit repo. Three skills, all invoked by hand.

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `toolkit-orchestrate` | `/toolkit-orchestrate [task, status, or clean]` | Splits work into bounded subagent briefs and runs them in parallel with write isolation. Tracks each run in an untracked ledger at `.local/agent-notes.md` and checks the evidence in every result before reporting |
| `toolkit-audit` | `/toolkit-audit [all|android|ios|design|pr-review|writing|agents] [--stale-only]` | Re-checks every rule and reference against its cited source, classifies each rule (SUPPORTED, PARTIAL, COMMUNITY, HOUSE, WRONG, STALE), writes `docs/audits/<date>-audit.md` with proposed diffs, and refreshes `verified:` stamps only for files that pass and only after you confirm |
| `toolkit-check` | `/toolkit-check [base ref]` | Runs the pre-PR checks `AGENTS.md` requires for the files a branch changes, lists hand-written per-agent files that may need mirroring, and edits nothing |

Run the audit from the ai-toolkit checkout every 90 days, or when the `freshness` CI job starts warning. The monthly `linkcheck` job tells you when a cited page moved. The audit's `references/sources.md` names the authorities per domain and how to fetch pages that resist a plain request, and its `references/rubric.md` defines the classes with worked examples from the 2026-09-29 audit.

The orchestrate skill's `references/sources.md` records the platform docs behind each of its dispatch rules. It carries a `verified:` stamp, so the freshness job and the audit re-check it.
