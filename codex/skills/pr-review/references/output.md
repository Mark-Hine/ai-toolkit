# Canonical output — `findings.json` (schema `pr-review/v1`)

The machine-readable review. Everything downstream reads this file: the markdown document is
rendered from it (template.md), the CI poster consumes it (`scripts/post_azdo.py`,
`references/ci.md`), and the next re-review walks it to know what to re-verify. The document and
the JSON must stay in parity — every finding ID in one appears in the other.

Write it next to the document: `pr-review-<source>-to-<target>-YYYY-MM-DD.json` (promotion) or
`pr-review-<branch-or-PR#>-YYYY-MM-DD.json` (feature). Local runs: repo root, untracked. CI runs:
the artifact staging directory.

## Shape

```json
{
  "schema": "pr-review/v1",
  "mode": "promotion",
  "run": "initial",
  "generated": "2026-08-30",
  "verdict": "request_changes",
  "scope": {
    "source": "sit",
    "target": "uat",
    "merge_base": "13da212b…",
    "source_head": "8e3be28a…",
    "commits": 297,
    "files": 271,
    "churn_note": "~78% formatter sweep, verified with git diff -w",
    "inferences": ["platform=android (settings.gradle.kts)", "ticket_key=ABC (211 hits)"]
  },
  "standards_basis": "<the pack's standards-basis paragraph, verbatim>",
  "manifest": {
    "result": "pass_with_queries",
    "checks": [
      {"name": "merge_base", "result": "pass", "note": "target HEAD is the merge-base"},
      {"name": "release_list", "result": "pass", "note": ""},
      {"name": "dependencies", "result": "query", "note": "lib X 1.2→2.0 across two lockfiles — intended?"},
      {"name": "tickets", "result": "pass", "note": "68/80 refs traceable"}
    ]
  },
  "findings": [
    {
      "id": "B1",
      "severity": "blocker",
      "title": "Failed delete reported as success",
      "file": "feature/payments/DeleteViewModel.kt",
      "line": 96,
      "symptom_sites": ["feature/payments/DeleteScreen.kt:210"],
      "root_cause": "repository result discarded at the call site; merge-base handled Failure",
      "merge_base_behaviour": "when(result) routed Failure to the error state",
      "standard": "ARCH-RECS",
      "finding": "<full engineer-facing evidence — the Finding cell, verbatim>",
      "pr_comment": "<the author-facing ask — the PR Comment cell, verbatim>",
      "verify_fixed_when": "when(result) handles Failure at the call site and a failed delete renders the error state — check file:line at the new head",
      "status": "open",
      "verification": {"adversarial": "confirmed", "lead_verified": true},
      "debug_only": false,
      "twin": null
    }
  ],
  "genuinely_good": ["<verified improvement, one line each>"],
  "register_crossref": [
    {"register_id": "SEC-02", "verdict": "unchanged", "evidence": "file:line or finding ID"}
  ]
}
```

## Field contract

Top level:

| Field | Values / notes |
|---|---|
| `schema` | `pr-review/v1`, literal. Bump only with a deliberate migration note. |
| `mode` | `promotion` \| `feature` |
| `run` | `initial` \| `re-review` |
| `verdict` | `approve` \| `approve_with_comments` \| `request_changes` — same rule as the document: any open blocker or unanswered question ⇒ `request_changes` |
| `scope` | the pinned range and counts; `inferences` lists every Phase-0 inference (mandatory in CI mode — protocol.md §24) |
| `standards_basis` | the loaded pack's block, so the JSON is self-describing when the doc isn't at hand |
| `manifest` | promotion mode only; omit in feature mode |
| `register_crossref` | only when a register exists; omit otherwise |

Per finding:

| Field | Values / notes |
|---|---|
| `id` | `B1…`/`Q1…`/`M1…`/`N1…` — **stable forever**; never renumbered across re-reviews (protocol.md §10) |
| `severity` | `blocker` \| `question` \| `major` \| `nit` |
| `file`, `line` | the **causal site**, source-side at the pinned SHA (protocol.md §17) |
| `symptom_sites` | other `file:line` manifestations; empty array when none |
| `root_cause` | one sentence naming the mechanism at the causal site |
| `merge_base_behaviour` | the verified "the target branch had X" half (protocol.md §1); empty string when the finding isn't comparative |
| `standard` | a registry key from the loaded pack (`ARCH-RECS`, `MASVS`, …) |
| `finding`, `pr_comment` | the two table cells, verbatim — the JSON carries them so renderers never re-write them |
| `verify_fixed_when` | the fix-verification contract (protocol.md §18) — required for B/Q/M, optional for N |
| `status` | `open` \| `fixed` \| `regressed` \| `partial` \| `retracted` — updated by re-reviews, with `file:line` evidence in `finding` history |
| `verification` | `adversarial`: `confirmed`/`weakened`/`inline` (no fan-out ran); `lead_verified`: bool — must be `true` for every published B/Q/M (protocol.md §6) |
| `debug_only` | `true` only with the confining guard quoted in `finding` (protocol.md §20) — such items are N at most |
| `twin` | paired-repo marker (`"<repo>: B2"`) or `null` |

## Rules

- **Parity**: doc ↔ JSON, both directions, checked at Phase 6.
- **Retraction** (protocol.md §22): keep the entry, set `status: "retracted"`, prepend
  `RETRACTED — <why>` to `finding`; a surviving sub-claim becomes a new entry with a new ID.
- **Re-review**: update statuses in place (evidence at the new head), append new findings, update
  `scope` to the new range, set `run: "re-review"`. Never rewrite history — the JSON is the
  record the poster reconciles PR threads against.
- The JSON never contains credentials, tokens, or absolute local paths.
