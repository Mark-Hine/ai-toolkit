# Review protocol

The rules of engagement. Each one came out of a real review where it earned its place — the "why"
is recorded so the rule survives contact with a case it doesn't obviously fit.

§1–§12 govern how a review is conducted; §13–§16 are the grading rules that apply to every
platform pack; §17–§20 extend the grading rules (root cause, verification criteria, citation
hygiene, debug variants); §21–§24 govern the verification passes, retractions, severity
negotiation, and CI conduct. Never renumber §1–§16 — they are cross-referenced by number from
SKILL.md and every platform pack; new rules append.

## 1. Delta-only discipline

Review **only** `MERGE_BASE..SOURCE_HEAD`. Never paste baseline findings into a PR review — the
project's standing register already tracks them, where one exists, and repeating them in a PR reads
as blocking the vendor's merge on debt they didn't create. Pre-existing defects appear only when the delta **extends or
entrenches** them (say which), or via the register cross-reference table's verdicts.

The inverse also holds: every "this PR changed X" claim must be verified against the actual
merge-base tree (`git show MERGE_BASE:path`), not memory or the file's current look. Several
findings' whole weight rests on "the previous code did this correctly" — if that half is wrong,
the finding collapses publicly.

## 2. The scope statement is not optional

Every review — and every subsequent approval comment — carries the scope statement
(template.md §2). It is the legal/commercial boundary: approval of a promotion delta must never be
construable as sign-off of the target baseline, acceptance for production, or closure of register
findings. If someone asks to "just approve it", the approval text still names the commit range and
the three exclusions.

## 3. Severity vocabulary

- **B (Blocker)** — fix before merge. Reserved for verified defects in money movement, legal/
  compliance surfaces, security/privacy exposure, destructive UX, or CI integrity (a pipeline that
  cannot fail is a blocker even though no app code is wrong — it certifies everything else).
- **Q (Question)** — answer before merge. Wire-contract changes needing backend readiness
  confirmation, compliance/product sign-offs, intent checks ("bugfix or accidental flip?"). A Q is
  a gate: unanswered Qs hold approval just as Bs do.
- **M (Major)** — please ticket. Real defects or architecture erosion that shouldn't block the
  merge but must not evaporate. Every M's PR comment names the concrete fix so the ticket writes
  itself.
- **N (Minor/nit)** — hygiene, drive-by observations, process notes.

Escalation is evidence-driven: a suspicion is a Q, a verified mechanism is a B/M. Severity never
rises because the tone is harsh — it rises because the failure is proven.

## 4. Grading posture (default: harsh, standards-cited)

- **Cite the standard per finding**, using the vocabulary of the platform pack you loaded
  (`platforms/android.md`, `platforms/ios.md`, `platforms/spring-boot.md`,
  `platforms/react-nextjs.md`, or `platforms/generic.md`). Where the source grades
  its own advice — Android's SR/R, for instance — quote that grading rather than inventing one.
- **Where the only authority is community consensus, cap severity.** Some ecosystems publish
  doctrine and some don't; iOS architecture is the standard example. When you can't point at an
  authority, prefer "inconsistent with itself" framing — the same PR, or the same file, already
  does it right elsewhere, so point there. The cap does not apply to security-standard items or to
  verified defects: a bug is a bug regardless of who documented the pattern.
- **Where official guidance exists but the ecosystem has visibly not converged on it, cite it and
  cap severity.** The inverse of the case above, and the signals are concrete: mature,
  actively-maintained libraries shipping the opposite as a first-class API; an unresolved upstream
  issue where the platform declined to settle the question; or the vendor's own text hedging — a
  "strongly recommended" defined as *unless it clashes fundamentally with your approach*, a
  guidance-not-rules disclaimer, or a documented mitigation rejected only for tooling reasons. Grade
  the specific failure modes the guidance describes, not the pattern's existence, and prefer
  "inconsistent with itself" framing. Departing from an exemplar is not a defect.
- **Respect the pack's pragmatism guardrails** (§15). Harsh means rigorous, not dogmatic — flagging
  absent architectural ceremony as a defect discredits the real findings around it.
- The best finding shape names the correct pattern **already in the same PR** and asks the new
  code to match it. It is unanswerable.

## 5. PR comments are written for senior developers — concise

Each finding's PR-comment cell is one to three sentences: the specific ask first ("Restore the
`when(result)` handling on delete and update…"), then the consequence **only when it is not
obvious from the Finding cell**, stated in product terms (money, a legal record, customer data)
rather than architectural jargon ("as shipped, a failed delete shows success while the debit keeps
running"). Do not walk the failure step-by-step, explain platform concepts, or restate evidence
the Finding cell already carries — the reader is a senior developer, and the Finding column holds
the mechanism for anyone who wants it. The cell must still work when pasted alone into the PR.
Where a design decision needs explaining rather than correcting, asking the author two or three
direct questions in the comment is legitimate and often the fastest route to a fix; sarcasm never
is.

## 6. Personal verification (the no-blind-trust rule)

Subagent findings are leads, not findings. Before publishing, the lead reviewer personally
re-verifies **every B, Q, and M**: open the file at the pinned SHA, confirm the line numbers, the
mechanism, and the merge-base half of the claim. This has caught real fabrications — an agent has
cited a file that does not exist in the tree; one grep refuted it and the finding was demoted.
N-level items may ship on agent evidence, but their file:line must at least resolve.

## 7. Churn honesty

When the delta is dominated by mechanical churn (formatting sweeps, regenerated localization
files), raw diff presence proves nothing. Establish the churn share up front — a delta can be
overwhelmingly a formatter sweep plus regenerated files, with only a handful of real net-new lines
hiding in it — state it in the scope section, and verify every "delta-added" claim with a
whitespace-insensitive diff
(`git diff -w`) or a merge-base grep. A "new" line that merely moved is a retracted finding
waiting to happen.

## 8. Ref quirks and pinning

- Pin `SOURCE_HEAD` at Phase 0; all published line numbers are source-side at that SHA. If the
  head moves mid-review, decide: re-pin and re-verify, or publish against the old pin and note it.
- **When a ref name doesn't resolve**, don't guess and don't silently review a different range —
  ref-name conflicts (a tag and a branch sharing a name, a stale remote-tracking entry) do happen
  in real clones. Resolve the endpoint from the raw SHA instead (`git ls-remote` or
  `git rev-parse`), and record the workaround in the review's standards-basis line so the reader
  can reproduce your range exactly.

## 9. Mode detection

Promotion mode when **both** endpoints are environment branches, using the set detected for this
repo at Phase 0 rather than an assumed vocabulary. Candidates worth recognising: `dev`, `develop`,
`sit`, `qa`, `test`, `uat`, `stage`/`staging`, `preprod`, `prod`/`production`, `main`/`master`, and
`release/*`. Many teams suffix these by region, brand, or tenant (`dev-eu`, `uatAcme`) — treat a
suffixed branch as its base environment. Promotion mode enables the manifest section and the full
scoping statement. Everything else — feature branches, a trunk→environment merge, PR-by-number — is
feature mode: same findings machinery, simple scope line, no manifest section.

When detection is ambiguous, say what you inferred and ask before asserting promotion mode; the
scoping statement it produces is a commercial artefact and shouldn't appear by accident.

## 10. Re-review mode

Triggered when a prior review deliverable exists for this PR and the head moved. Order of work:

1. **Blockers first.** Re-verify every prior B at the new head before reading anything new —
   "all blockers untouched" is the single most important sentence of a re-review.
2. **Then every other open finding.** Re-verify each open Q and M against its `verify_fixed_when`
   criterion (§18). Every status — `fixed`, `untouched`, `regressed`, `partial` — cites `file:line`
   evidence at the new head; a status without evidence is a claim, not a verification.
3. Review only the added range (`OLD_HEAD..NEW_HEAD`) for new findings; verify claimed fixes in
   the added range actually fix (and don't regress a neighbouring path).
4. **Ask which framing** before writing: an **addendum** (§1a section, prior IDs stable, new
   findings take next free IDs) or a **fresh rewrite** (whole document regenerated at the new
   head, no re-review language — requested when the review's audience shouldn't see the history).
   Both have been wanted at different times; don't guess. In CI mode (§24) don't ask — default to
   the addendum plus thread updates.
5. Never renumber existing finding IDs — they may already be quoted in PR comments and tickets.

## 11. Register cross-reference discipline

Where the project keeps a standing quality/assessment register — a CSV or table of known findings,
typically produced by an audit or assessment — it is the cross-reference key, not a source of
review findings. If the repo has no such register, skip the section and say so; don't invent one.
Verdict vocabulary: **Worsens** / **Partially addressed** /
**Unchanged** / **Exposure widened** / **Mixed** — each with an evidence pointer. Only findings
the delta touches get rows; the table's framing sentence ("all other register findings remain
open and unaffected") is part of the scope boundary, so keep it.

## 12. Output hygiene

- Deliverables: `findings.json` (the canonical output — see `references/output.md`) and the
  markdown document rendered from it, side by side. Names: `pr-review-<source>-to-<target>-YYYY-MM-DD.{json,md}`
  (promotion) or `pr-review-<branch-or-PR#>-YYYY-MM-DD.{json,md}` (feature). Local runs write them
  at the repo root, untracked — the document gets pasted into the PR, not committed. CI runs write
  to the artifact staging directory instead.
- **Local mode:** nothing is posted to the PR or sent anywhere by this skill. Posting is the
  human's call.
- **CI mode (§24):** the pipeline posts `findings.json` via the shipped adapter
  (`scripts/post_azdo.py`) — that posting is authorized by the pipeline's own configuration, not
  by this skill deciding to.
- If the working tree carries modifications you didn't make, say so and review against
  `origin/<source>`, never the tree.

## 13. Volatile facts are looked up, never recalled

Platform facts move faster than any document that describes them: API deprecations, store
submission gates and their effective dates, "the current recommended library" for storage or
crypto, whether a given attestation service still exists. The platform packs deliberately point at
this rule instead of asserting such facts, because a confidently wrong deprecation claim in a
review is worse than no claim — it burns the credibility of the findings around it.

So: before a finding depends on one of these, look it up and cite what you found with its date. If
you can't verify it in the moment, downgrade the claim to a question for the author rather than
stating it.

## 14. `Unverified` is a valid grade — and "method, not vibes"

Static reading cannot settle everything. A claim that would need a device trace, a profiler run, a
screen-reader pass, or a load test to confirm is labelled **Unverified**, together with the exact
run that would confirm it. That is a useful review output: it hands the team a reproducible next
step instead of an argument.

The corollary is that performance and rendering claims need an artefact, not an intuition. "This
will cause extra recomposition / re-renders / allocations" is unverified unless you can point at
compiler metrics, a profiler capture, or a quoted parameter that provably breaks the mechanism.
Reviewers who assert performance from reading alone are usually wrong, and are always
unfalsifiable.

## 15. Pragmatism guardrails

Harshness has to be aimed at defects, not at architectural taste, or the vendor learns to discount
the whole document. Two framings keep it aimed:

- **Flag the absence of discipline, not the absence of ceremony.** Missing layering, no clear owner
  for a piece of state, no seam where tests need one — those are findings. A missing use-case
  layer, no repository interface per data source, or the team's choice among competing patterns is
  not, when the codebase applies its choice consistently.
- **Flag inconsistency within this codebase.** Where a paradigm debate is genuinely unresolved in
  the wider community, the reviewable question is whether this repo contradicts itself — one
  feature doing it two ways is a finding; the repo differing from your preference is not.

Each platform pack names the specific ceremonies not to flag for that ecosystem.

## 16. Main-safety belongs to the data layer

Whichever type performs blocking work owns moving it off the critical thread, so callers don't have
to know. Presentation-layer code should be able to call any data-layer function without arranging
its own thread hop; a hop appearing in a view model or controller is a signal that main-safety
leaked upward. Grade it as a style issue rather than a bug unless it demonstrably blocks the UI
thread. Each pack expresses this in its own idiom (dispatchers and `withContext`, actors and
`async`, executors and thread pools).

## 17. Root cause, not symptom

A finding is anchored at the **causal site** — the line where the mechanism lives — with other
manifestations listed as symptom sites inside the same finding, not raised as separate findings.
The test: *if the PR comment's exact ask is done, does the defect class die, or just this
instance?* If only the instance dies, the finding is aimed at a symptom and needs re-anchoring.
The PR comment always asks for the root-cause fix; symptom-level patches are what the finding
exists to prevent.

Why it earned its place: a drafted ticket was once built on an unreachable "runtime switch"
symptom and had to be rewritten from scratch; a register finding blamed a manager class when the
mechanism was actually dozens of top-level values frozen at class-load — the wrong causal claim
changed both the fix and the effort estimate. Both the adversarial pass (§21) and the lead's
personal verification (§6) explicitly challenge the causal claim, not just the evidence.

## 18. Verification criteria are part of the finding

Every B, Q, and M ships a `verify_fixed_when` criterion — the observable that proves the defect's
absence, stated when the finding is verified (you just proved the defect exists; state what would
prove it gone). It must be mechanical wherever possible: a command to run, a `file:line`
expectation, or a named test that must pass. "The code is cleaner" is not a criterion. For a Q,
the criterion is the answer or evidence that closes it (e.g. "backend confirms the v2 endpoint is
deployed to the target environment"). For an N it is optional.

The criterion is a contract three parties share: the assignee knows when they are done, the
re-review (§10) checks each open finding against it with `file:line` evidence at the new head, and
the CI poster carries it into the PR thread verbatim so the conversation happens against the same
test. Where a criterion cannot be checked statically, it states the exact run that would check it —
the same discipline §14 applies to claims, extended to fixes.

## 19. SHA ancestry before citation

Never cite a commit, branch tip, or "fixed in `<sha>`" without confirming the SHA is still
reachable from the ref you're publishing against: `git merge-base --is-ancestor <sha> <ref>`.
Histories get amended and rebased, and a dead reference fails silently — the reader clicks
through to nothing, or worse, to a different tree than the one reviewed. Branch names and SHAs
are re-derived at use time, never recalled from earlier in the session or from notes; this rule
exists because recalled SHAs have gone orphaned mid-review more than once.

## 20. Debug-variant exclusion

A defect confined to debug builds — and **verifiably** absent from every release variant — is not
flagged at B/Q/M. Quote the guard that confines it (the build-type or flavor conditional, the
debug-only source set, the release config that strips it); at most it becomes an N noting the
verification. The verification is mandatory: "probably debug-only" is not an exclusion, it is an
unverified claim, and an unverified claim about a security-sensitive surface is a Q for the
author.

## 21. The adversarial pass

Between fan-out and the lead's personal verification, adversarial agents try to **refute** every
lead — a second opinion whose job is to disagree. Each agent checks, per lead: the cited file and
line exist at the pinned SHA; the merge-base half of the claim is true (`git show
MERGE_BASE:path`); the finding is anchored at the root cause, not a symptom (§17); it isn't
debug-only (§20); and where a runnable command settles the question — a compile, a test, a grep —
it runs the command rather than reading harder. Verdicts: **CONFIRMED** / **REFUTED** (with the
counter-evidence) / **WEAKENED** (survives but at lower severity or narrower scope).

Two rules keep the pass honest:

- **Batch and assert completeness.** Leads go to agents in batches (about eight per agent), and
  every agent's final line asserts "N of N verified". A batch that cannot make that assertion is
  re-dispatched — a truncated pass that silently verified a fraction of its leads has happened,
  and it is worse than no pass because it launders the unverified remainder.
- **Refutations are recorded, not deleted.** A REFUTED lead is dropped from the findings table,
  but the refutation (claim + counter-evidence) is kept in the run's notes — a refutation is
  review output, and the lens that produced the lead may produce its siblings.

## 22. Retractions are visible

When a published finding turns out to be wrong, it is retracted in place — the ID is kept, the
status becomes `retracted`, and a correction note says what was wrong and why. Never a silent
edit or deletion: anyone who read the earlier version must be able to see what changed. If part
of the retracted finding survives (a real sub-defect inside a wrong framing), the surviving claim
gets its **own new ID** rather than living inside the retraction — a confirmed defect must not be
buried in a retracted one.

## 23. Severity is negotiable with the human

In local mode, echo the grades with the findings summary — severity is the reviewer's proposal,
not a verdict. The human may re-grade (up or down); the register records the final call. Where a
grade is genuinely arguable, say so in one line ("this is the severity call I'd defend but
concede is arguable") rather than presenting it as settled. In CI mode the echo is skipped;
re-grades arrive as configuration or as an instruction to the next run, never as a mid-run
conversation.

## 24. CI conduct

When the review runs headless in a pipeline (CI mode, detected at Phase 0), there is no one to
ask, so every ask in the phases resolves to its safe default:

- Ambiguous promotion detection ⇒ **feature mode**. The full scoping statement is a commercial
  artefact and must never appear by accident (§9); a pipeline that wants promotion mode states it
  in configuration.
- Re-review framing ⇒ **addendum** plus thread updates (§10).
- Severity echo-back ⇒ skipped (§23).
- Missing register, ticket key, or paired repo ⇒ skip those sections silently.
- A wrong inference costs a review run, not a conversation — so CI mode also **records every
  inference it made** in the JSON's scope block, where the pipeline log makes it auditable.

Posting: CI mode is the one context where output leaves the machine — `findings.json` is posted
to the PR by the shipped adapter under the pipeline's own credentials and configuration
(`references/ci.md`). The skill itself still never posts; the pipeline does.
