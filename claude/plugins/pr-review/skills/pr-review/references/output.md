---
verified: 2026-09-29
sources: house
---

# Canonical output: `findings.json` (schema `pr-review/v1`)

The machine-readable review. Everything downstream reads this file: the markdown document is
rendered from it (template.md), the poster consumes it (`scripts/post_review.py`,
`references/ci.md`), and the next re-review walks it to know what to re-verify. The document and
the JSON must stay in parity. Every finding ID in one appears in the other.

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
    "host": "azure",
    "destinations": ["azure", "confluence"],
    "inferences": ["platform=android (settings.gradle.kts)", "ticket_key=ABC (211 hits)", "host=azure (origin URL)"]
  },
  "standards_basis": "<the pack's standards-basis paragraph, verbatim>",
  "manifest": {
    "result": "pass_with_queries",
    "checks": [
      {"name": "merge_base", "result": "pass", "note": "target HEAD is the merge-base"},
      {"name": "release_list", "result": "pass", "note": ""},
      {"name": "dependencies", "result": "query", "note": "lib X 1.2 to 2.0 across two lockfiles. Intended?"},
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
      "finding": "<full engineer-facing evidence, the Finding cell verbatim>",
      "pr_comment": "<the author-facing ask, the PR Comment cell verbatim>",
      "verify_fixed_when": "when(result) handles Failure at the call site and a failed delete renders the error state. Check file:line at the new head",
      "status": "open",
      "verification": {"adversarial": "confirmed", "lead_verified": true},
      "debug_only": false,
      "twin": null,
      "evidence": [
        {
          "kind": "device_harness",
          "path": "pr-review-evidence/78455-b1-delete-failure-shows-success.png",
          "caption": "Left: a failed delete shows the success screen. Right: the same failure at the merge-base shows the error state",
          "method": "Real screen and view model on an API 36 emulator, repository mocked to return Failure",
          "sha": "8e3be28a41c0",
          "device": "Pixel 9 Pro emulator, API 36"
        }
      ]
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
| `verdict` | `approve` \| `approve_with_comments` \| `request_changes`, by the same rule as the document: any open blocker or unanswered question ⇒ `request_changes` |
| `scope` | the pinned range and counts. `inferences` lists every Phase-0 inference (mandatory in CI mode, protocol.md §24) |
| `scope.host` | optional, `azure` or `github`: where the PR lives. The poster uses it when `--host` is not given |
| `scope.destinations` | optional list of where the review goes: the PR host plus `file` or `confluence` for the document. Phase 0 records it and Phase 7 reads it. The poster ignores it |
| `standards_basis` | the loaded pack's block, so the JSON is self-describing when the doc isn't at hand |
| `manifest` | promotion mode only. Omit in feature mode |
| `register_crossref` | only when a register exists. Omit otherwise |
| `genuinely_good` | verified improvements, one line each. Posted in the PR summary under "Good in this delta" |

Per finding:

| Field | Values / notes |
|---|---|
| `id` | `B1…`/`Q1…`/`M1…`/`N1…`, **stable forever** and never renumbered across re-reviews (protocol.md §10) |
| `severity` | `blocker` \| `question` \| `major` \| `nit` |
| `file`, `line` | the **causal site**, source-side at the pinned SHA (protocol.md §17) |
| `symptom_sites` | other `file:line` manifestations, or an empty array when none. Posted as the thread's **Also at** line |
| `root_cause` | one sentence naming the mechanism at the causal site. It is posted on the PR as the thread's **Why** line, so write it for the author |
| `merge_base_behaviour` | the verified "the target branch had X" half (protocol.md §1), or an empty string when the finding isn't comparative |
| `standard` | a registry key from the loaded pack (`ARCH-RECS`, `MASVS`, …) |
| `finding`, `pr_comment` | the two table cells, verbatim. The JSON carries them so renderers never re-write them |
| `verify_fixed_when` | the fix-verification contract (protocol.md §18), required for B/Q/M and optional for N |
| `status` | `open` \| `fixed` \| `regressed` \| `partial` \| `retracted`, updated by re-reviews, with `file:line` evidence in `finding` history |
| `verification` | `adversarial`: `confirmed`/`weakened`/`inline` (no fan-out ran). `lead_verified`: bool, which must be `true` for every published B/Q/M (protocol.md §6) |
| `debug_only` | `true` only with the confining guard quoted in `finding` (protocol.md §20). Such items are N at most |
| `twin` | paired-repo marker (`"<repo>: B2"`) or `null` |
| `evidence` | optional array of proof the author can check in seconds, for B, Q and M findings only (protocol.md §25, `references/evidence.md`). Omit it, or leave it empty, when nothing was collected |

Per evidence item:

| Field | Values / notes |
|---|---|
| `kind` | `unit_test` \| `render` \| `device_harness` \| `device_live` \| `recording` \| `transcript`, the ladder rung that produced it |
| `path` | the file, relative to the directory that holds `findings.json`, such as `pr-review-evidence/78455-m1-lookup-vs-manual.png`. Never absolute and never containing `..`. Required for every kind except `unit_test` and `transcript`, which may carry only an `excerpt`. Images are PNG, JPEG, GIF or WebP, and every file is at most 5 MB |
| `caption` | one sentence saying what the reader sees, defect first, then the control when the image is a pair |
| `method` | how it was made and what was stubbed, such as "Real screen and view model on an API 36 emulator, repository mocked". Never call a harness or a render a live reproduction |
| `sha` | the commit the evidence was built from: `scope.source_head`, or the new head in a re-review |
| `device` | the emulator, simulator, browser or JVM it ran on, or `null` for a unit test or transcript |
| `excerpt` | optional text of at most 20 lines: the failing assertion, or a redacted request and response. Rendered as a code block |
| `url` | optional link to a copy already hosted elsewhere, such as a Confluence attachment. The poster embeds it in place of uploading `path`, and on GitHub it is the only way an image shows inline |

The field is additive, so the schema stays `pr-review/v1`. A file without `evidence` is valid, and
an older poster ignores the field and posts the thread without the image.

## Rules

- **Parity**: doc ↔ JSON, both directions, checked at Phase 6.
- **Retraction** (protocol.md §22): keep the entry, set `status: "retracted"`, prepend
  `RETRACTED: <why>` to `finding`. A surviving sub-claim becomes a new entry with a new ID.
- **Re-review**: update statuses in place (evidence at the new head), append new findings, update
  `scope` to the new range, set `run: "re-review"`. Never rewrite history. The JSON is the
  record the poster reconciles PR threads against.
- The JSON never contains credentials, tokens, or absolute local paths. Evidence files and
  excerpts carry test data only.
