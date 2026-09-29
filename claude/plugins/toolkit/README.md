# toolkit

Maintenance of the ai-toolkit repo itself. One skill, invoked by hand.

| Skill | Invocation | Purpose |
| --- | --- | --- |
| `audit` | `/toolkit:audit [all|android|ios|design|pr-review|writing|agents] [--stale-only]` | Re-checks every rule and reference against its cited source, classifies each rule (SUPPORTED, PARTIAL, COMMUNITY, HOUSE, WRONG, STALE), writes `docs/audits/<date>-audit.md` with proposed diffs, and refreshes `verified:` stamps only for files that pass and only after you confirm |

Run it from the ai-toolkit checkout every 90 days, or when the `freshness` CI job starts warning. The monthly `linkcheck` job tells you when a cited page moved. `references/sources.md` names the authorities per domain and how to fetch pages that resist a plain request. `references/rubric.md` defines the classes with worked examples from the 2026-09-29 audit.
