# Review-document template

The section contract for the rendered document. **`findings.json` is the source of truth**
(`references/output.md`); this document is rendered from it, and the two must stay in parity —
every finding ID in the JSON appears here and vice versa.

Sections appear **in this order**; sections marked
*(promotion mode)* are omitted for feature-PR reviews, and *(conditional)* sections are omitted
when they'd be empty. Text in `<angle brackets>` is filled per run.

Headings below name the template's sections; the fenced blocks show what the **emitted document**
actually contains, including its own heading numbering.

The wording in the fenced blocks is a safe default, not scripture. Scope and attribution wording in
particular is where an organisation's own approved language belongs — if your team or legal
function has agreed a form of words for review scope, paste it in place of the default and keep it
stable across reviews, because its value comes from being recognisable.

## Title and verdict

```markdown
# Technical review — <Platform/Repo> <SOURCE> → <TARGET> promotion     (promotion mode)
# Technical review — <Repo> PR <number/branch>: <one-line topic>       (feature mode)

**Verdict: <Request changes | Approve with comments | Approve>.** <One paragraph: count the
blockers and name each in half a sentence, count the questions, then the release clause — e.g.
"All other findings are comment-level and should not hold up the merge once the blockers clear.">
```

Verdict rule: any B → **Request changes**. No B but unanswered Q → **Request changes** (the
questions gate approval). M/N only → **Approve with comments**.

If a paired repo was reviewed for the same change and its blockers do **not** reproduce here, say
so in a **Credit where due** paragraph directly under the verdict — it tells the author the reviews
are independent rather than copy-pasted.

## Standards basis

One paragraph naming every standard the findings cite, with URLs. **Paste the standards-basis block
from the platform pack you loaded** (`platforms/android.md`, `platforms/ios.md`,
`platforms/spring-boot.md`, `platforms/react-nextjs.md`) or, for the generic
pack, the basis you established from the repo's own configs, docs and the stack's official
guidance.

Then append the verification sentence:

```markdown
Every claim below was verified against the <source> tree; line numbers are <source>-side
(`origin/<source>` = `<HEAD_SHA>`).
```

If a ref had to be resolved by raw SHA (protocol.md §8), record that here too, so the reader can
reproduce the exact range.

## Scope of this approval

**Promotion mode — the scoping statement. All three exclusions are the point of it:**

```markdown
This review and any subsequent approval cover **only the <source>→<target> delta** — commits
`<MERGE_BASE>..<SOURCE_HEAD>` (<N> commits, <N> files, +<adds>/−<dels><churn note, if the delta is
mostly mechanical: "; ~<N>% is a formatter sweep and regenerated files, verified to add only <N>
net-new lines of behaviour — all 'delta-added' claims below were re-verified with
whitespace-insensitive diffs, not inferred from raw churn">). It does **not** constitute technical
sign-off of the pre-existing <TARGET> baseline, acceptance of the release for production, or
closure of any finding in <the standing quality register, named>, whose findings remain open except
where noted in §<register section>. Pre-existing defects are flagged only where this delta extends
or entrenches them.
```

**Feature mode — the simple scope line:**

```markdown
This review covers the PR delta only — commits `<MERGE_BASE>..<HEAD>` against `<target branch>`
(<N> commits, <N> files).<" Register findings remain open except where noted below." if a register
exists>
```

## Promotion manifest verification *(promotion mode)*

Heading: `## 1. Promotion manifest verification — <PASS | PASS, one query | FAIL>`. Bullets, each
ending ✔ when clean; queries called out in **bold** with the ask stated as a question:

- Merge-base check: target HEAD is the merge-base; source strictly contains target; the PR diff is
  exactly what lands.
- Release list: first-parent merge history vs the PR description; mergebacks verified empty;
  count of commits pushed directly to the source branch.
- Third-party dependency additions/version changes (name the manifests and lockfiles checked).
- Ticket reconciliation: unique ticket references vs the count the description claims; example
  unticketed or mislabeled commits by SHA. Omit if the project doesn't use ticket keys in commits.

## Findings

```markdown
## 2. Findings

ID prefix = severity: **B** = blocker (fix before merge) · **Q** = question (answer before merge)
· **M** = major (please ticket) · **N** = minor/nit. Line numbers are `origin/<source>`-side.

| ID | Finding | PR Comment | Verified fixed when |
|---|---|---|---|
```

Column contract:

- **ID** — `B1…`, `Q1…`, `M1…`, `N1…`, numbered by severity then discovery order. IDs are stable
  across re-reviews of the same PR: never renumber an existing finding; new findings take the next
  free number. When a paired repo has the same defect, append **"<other repo> twin"** in bold at
  the end of the Finding cell.
- **Finding** — the engineer-facing cell: `file:line` evidence first, **anchored at the causal
  site** with symptom sites listed after it (protocol.md §17), what changed relative to the
  merge-base ("the target branch had X; this PR does Y"), the mechanism, and the standard tag in
  brackets. Written for the reviewer who will verify it.
- **PR Comment** — the author-facing cell, written concisely for a senior developer: the concrete
  fix as a polite, specific ask first ("Restore… / Move…") — always the root-cause fix, never a
  symptom patch — plus the consequence only when it is not obvious from the Finding cell, in
  product terms ("as shipped, a failed delete shows success while the debit keeps running"). One
  to three sentences; no step-by-step walkthroughs, no platform-concept explanations, no restating
  the Finding's evidence. Self-contained — it must survive being pasted alone into the PR with no
  surrounding context.
- **Verified fixed when** — the fix-verification contract (protocol.md §18): the observable that
  proves the defect gone — a command to run, a `file:line` expectation, or a named test that must
  pass; for a Q, the answer or evidence that closes it. One or two sentences, mechanical enough
  that the re-review (and the CI poster) can check it without re-deriving the finding. Optional
  for N rows.

One row per finding; related defects share a row only when they share a fix. Escape `|` inside
cells as `\|`. A retracted finding keeps its row: the Finding cell gains a leading
**RETRACTED — <what was wrong and why>** correction note and the other cells are left as
published; a surviving sub-claim moves to its own new row (protocol.md §22).

## Cross-repo twins *(conditional)*

Only when the same change was reviewed in a paired repo (a mobile platform pair, a client and its
service, a fork). Each row is one defect needing a single coordinated fix:

```markdown
## 3. Cross-repo twins (for one coordinated fix)

| Topic | <Repo A> | <Repo B> |
|---|---|---|
| <shared defect, one line> | <finding IDs in A> | <finding IDs in B> |
```

## Cross-reference to the quality register *(conditional)*

Only when the project keeps a standing register of known findings:

```markdown
## <n>. Cross-reference to <register name>

Verdicts describe what **this delta** does to each finding; all other register findings remain
open and unaffected.

| Finding | Verdict in this delta | Evidence |
|---|---|---|
| <REG-ID short title> | **Worsens** \| **Partially addressed** \| **Unchanged** \| **Exposure widened** \| **Mixed** | <finding ID or file:line> |
```

Only findings the delta actually touches get a row; group "Unchanged" rows by theme to keep the
table short. For a small PR this section may legitimately be one sentence.

## Genuinely good in this delta

Mandatory, even at Request Changes — credit is what keeps a harsh register credible and the working
relationship intact. Bullets naming real, verified improvements. Where a finding merely asks new
code to match a good pattern the same PR introduced, say so here.

## Appendix A — focused manual-review checklist

Numbered, ranked by risk: `file:line` clusters and the finding IDs they carry, so a human reviewer
can spend one hour on the highest-value locations.

## Footer

```markdown
---
*Review conducted by <reviewing team> against merge-base `<MERGE_BASE>` (<target>) →
`<SOURCE_HEAD>` (<source>). Standards references: §Standards basis above.<" Companion review:
<paired repo>." if one exists><" Register references are to <register name>." if one exists>*
```

## Re-review addendum shape (Phase R, addendum framing)

Insert after the manifest section as `## 1a. Re-review — PR head moved to <NEW_SHA> (+<n> commits)`:

1. A status table for **every open prior finding**, Blockers first — each status verified against
   the finding's `Verified fixed when` criterion, never asserted:

```markdown
| ID | Status | Evidence (file:line @ <NEW_SHA>) |
|---|---|---|
| B1 | **untouched** \| **fixed** \| **regressed** \| **partial** | <what you checked at the new head> |
```

2. New findings from the added range, using the next free IDs.
3. Verified-good fixes from the added range.

The fresh-rewrite framing instead regenerates the whole document at the new head with no
re-review language — ask which is wanted (protocol.md §10); CI mode defaults to the addendum.
Either way, `findings.json` statuses are updated first and the document rendered from it.
