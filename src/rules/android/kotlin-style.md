---
verified: 2026-09-29
sources:
  - https://kotlinlang.org/docs/coding-conventions.html
  - https://developer.android.com/kotlin/style-guide
paths:
  - "**/*.kt"
  - "**/*.kts"
---

# Kotlin style (Android repos)

- Formatting follows the repo's `.editorconfig` (typical: 4-space indent for `.kt`/`.kts`, LF, no star imports,
  final newline). If the repo's formatter is unavailable, format by hand to match surrounding code.
- Use `when` as an expression over sealed types and keep it exhaustive, with no `else` branch that hides a missing case.
  Prefer guard conditions and early returns to nested `if`. Skill: `kotlin-control-flow`.
- Structured concurrency: no stored `CoroutineScope` in classes other than ViewModels (`viewModelScope`) and
  lifecycle owners (`lifecycleScope`), no `GlobalScope` and no `runBlocking` outside tests. Inject dispatchers
  rather than hardcoding `Dispatchers.IO`. Skill: `kotlin-coroutines-structured-concurrency`.
- State to the UI is `StateFlow` updated with `update {}`. One-shot events go through `Channel(BUFFERED).receiveAsFlow()`
  collected lifecycle-aware (rule `ui-events.md`). Do not introduce new `LiveData`. Skill: `kotlin-flow-state-event-modeling`.
- Use `@JvmInline value class` for a distinct identifier or amount when it prevents mixing domain values and the
  public contract permits it. Keep ordinary primitives and local tuples where they are clearer.
  Skill: `kotlin-types-value-class`.
- Nullability: no `!!` in production code. Use `requireNotNull`/`checkNotNull` with a message or handle the null.
- Match the existing file's style over these rules when editing a legacy file. Do not reformat unrelated lines.
