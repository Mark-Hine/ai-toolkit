---
verified: 2026-09-29
sources: house
---

# Classification rubric

One class per rule. Every class needs a quoted sentence from the source, or the Unverified flag.

| Class | Meaning | Grades as |
| --- | --- | --- |
| SUPPORTED | The source states the rule, or something stronger. | Keep. Eligible for a stamp refresh. |
| PARTIAL | The source supports a narrower or weaker claim than the rule makes. | Narrow the rule to what the source says, or add the missing condition. |
| COMMUNITY | No official source states it. A credible named origin exists (author, post, date). | Keep as T2 or house preference with the origin named. Never graded above Nit by reviewers unless a project opts in. |
| HOUSE | A deliberate standard of this toolkit, tagged `[HOUSE]` or `sources: house`. | Check only for internal consistency and for a source that now contradicts it. Never report it as unsourced. |
| WRONG | The source contradicts the rule. | Fix in the next content PR. The file keeps its old stamp until then. |
| STALE | A newer source, version or platform release supersedes the rule. | Fix in the next content PR. The file keeps its old stamp until then. |

Flags. `Unverified` when the source could not be read. `Conflicts with <file:line>` when two files disagree. `Tier 1` or `Tier 2` for design rules, taken from the rule file.

## Decision rules

- Quote first. Find the sentence, then classify. A rule that needs three sources to support it is PARTIAL at best.
- A version pin in a rule is STALE the day a newer stable ships, unless the rule says why the pin exists.
- A date in a rule ("from 2026-04-28") is STALE once the date has passed. Replace it with a look-up instruction.
- A rule that names an API is WRONG when the API does not exist, and STALE when the API is deprecated with a replacement.
- Two files that state different requirements for the same situation are a conflict even if each is SUPPORTED on its own.

## Worked examples from the 2026-09-29 audit

| Rule | Class | Why |
| --- | --- | --- |
| "Respect reduced motion via `LocalAccessibilityManager`" | WRONG | The Compose API exposes accessibility-service state and timeouts. Android's mechanism is the Remove animations setting and `ANIMATOR_DURATION_SCALE`. |
| "Window size classes Compact, Medium, Expanded" | STALE | The current page adds Large (1200 to 1599 dp) and Extra-large (1600 dp and wider). |
| "Minimum 44 by 44 pt touch targets on iOS" | PARTIAL | HIG says 44 pt is the default control size and 28 pt the minimum. |
| "8-point spatial grid" | COMMUNITY, then narrowed | Material 3 states an 8 dp scale with 4 dp for small elements. HIG defines no grid. |
| "No async work from ViewModel init" | HOUSE | The maintainer's standard, kept deliberately, also supported by the official state-production page. |
