---
verified: 2026-10-03
sources:
  - https://kotlinlang.org/docs/enum-classes.html
  - https://kotlinlang.org/docs/sealed-classes.html
  - https://kotlinlang.org/docs/data-classes.html
  - https://kotlinlang.org/docs/api-guidelines-backward-compatibility.html
  - https://kotlinlang.org/docs/api-guidelines-simplicity.html
  - https://kotlinlang.org/docs/coding-conventions.html
paths:
  - "**/*.kt"
  - "**/*.kts"
---

# Kotlin across platforms

Applies to Kotlin and Kotlin Gradle scripts in JVM, Android, server and other Kotlin projects. Project contracts take precedence. Platform rules add their scoped requirements.

- Model fixed choices with an enum when cases share one shape. Use a sealed hierarchy for a closed set of cases with different payloads. Public extension points implemented by consumers in other modules use an open interface. [KOT-DOMAIN]
- Parse and validate text at configuration, persistence, protocol and telemetry boundaries. Use typed values inside domain control flow. Give externally visible values explicit stable codes. Preserve existing codes and unknown-value handling. Enum names and ordinals are not a migration strategy. [KOT-BOUNDARY]
- Use named immutable records for related values that carry identity, deadlines or recovery state. Keep `Pair`, `Triple` and primitives where a short local operation or standard library API is clearer. A value class is useful when it prevents mixing distinct identities and the public contract allows it. [KOT-STATE]
- Dispatch closed enums and sealed hierarchies exhaustively. Avoid an `else` that hides a missing case. Open interfaces and untrusted input need deliberate fallback or rejection behavior. Prefer named predicates and focused helpers where they clarify lifecycle ownership or ordering. [KOT-DISPATCH]
- Handle nullable values explicitly. Avoid production `!!`, unchecked casts and building enums from external text with `valueOf` or `enumValueOf`. Justified interop boundaries validate the value, isolate any cast and explain the limit. Prefer an `is` check and smart cast over an unchecked `as`. [KOT-SAFETY]
- Preserve source, JVM binary and behavioral compatibility during a refactor. Adding a public data-class parameter changes generated members. Use additive overloads and one legacy adapter when consumers must remain compatible, and run consumers compiled before the change. Preserve ordering, ownership, clocks, random draws and externally visible labels. [KOT-COMPAT]
- Follow the repository's formatter, compiler warnings and dependency locks. Run focused regressions for the affected contracts, then required project checks. Add narrowly scoped checks for a demonstrated recurring defect. Do not introduce a new lint framework or broad style migration without an agreed need. [KOT-VERIFY]

For source rationale and generic examples, load `references/languages/kotlin.md` from the installed PR review skill. The reference is shared across all three agent layers.
