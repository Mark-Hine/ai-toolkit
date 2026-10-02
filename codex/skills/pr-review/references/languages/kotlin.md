---
verified: 2026-10-03
sources: inline
---

# Kotlin language reference

Load for Kotlin changes alongside the applicable platform pack. These language rules apply to desktop, Android, server and multiplatform code. Project contracts and pinned compiler features take precedence. House judgments below require a concrete readability, correctness or compatibility reason; they do not make every string or tuple a finding.

## Sources and limits

Reviewed on 2026-10-03. These are primary Kotlin sources. Check the pinned compiler before using version-dependent features. No preview feature is required by this guidance.

| Rule | Source | Scope and limit |
| --- | --- | --- |
| KOT-DOMAIN | [Enums](https://kotlinlang.org/docs/enum-classes.html), [sealed classes and interfaces](https://kotlinlang.org/docs/sealed-classes.html) | Enums describe fixed instances. Sealed direct subclasses are restricted to the same module and package, with further multiplatform constraints. An SDK extension point across consumer modules stays open. |
| KOT-BOUNDARY | [Enums](https://kotlinlang.org/docs/enum-classes.html), [API backward compatibility](https://kotlinlang.org/docs/api-guidelines-backward-compatibility.html) | Kotlin defines enum names and ordinals. Explicit external codes and boundary parsing are house rules to preserve existing logs, stored values and wire contracts. |
| KOT-STATE | [Data classes](https://kotlinlang.org/docs/data-classes.html), [API simplicity](https://kotlinlang.org/docs/api-guidelines-simplicity.html) | Generated equality and named properties help model state. Choosing a named record over a tuple is a house readability judgment, not a blanket ban on `Pair` or primitives. |
| KOT-DISPATCH | [Sealed exhaustiveness](https://kotlinlang.org/docs/sealed-classes.html#use-sealed-classes-with-when-expression), [coding conventions](https://kotlinlang.org/docs/coding-conventions.html) | Closed cases can be checked exhaustively. Open extension types still require an explicit unsupported-case policy. Helper extraction must preserve evaluation and side-effect ordering. |
| KOT-SAFETY | [Null safety](https://kotlinlang.org/docs/null-safety.html), [type checks and casts](https://kotlinlang.org/docs/typecasts.html) | `!!` can throw; safe casts return null on failure. Validated Java/framework interop can need a cast. Avoiding unchecked production casts is a house rule with that boundary exception. |
| KOT-COMPAT | [API backward compatibility](https://kotlinlang.org/docs/api-guidelines-backward-compatibility.html), [data classes](https://kotlinlang.org/docs/data-classes.html) | Source compatibility does not prove JVM binary compatibility. Generated constructors, `copy`, default bridges, record accessors and destructuring are part of the review. |
| KOT-VERIFY | [API backward compatibility](https://kotlinlang.org/docs/api-guidelines-backward-compatibility.html), [coding conventions](https://kotlinlang.org/docs/coding-conventions.html) | Project checks and targeted regression evidence are house verification policy. The official pages do not mandate a particular linter or test framework. |

## Fixed choices and stable boundary codes

Use an enum when every decision has the same metadata. Keep the logged identifier explicit so a source rename does not change the external contract.

```kotlin
interface Decision { val logId: String }

enum class ImportDecision(override val logId: String) : Decision {
    READ_FILE("read-file"),
    WRITE_RECORDS("write-records"),
}

fun describe(decision: ImportDecision): String = when (decision) {
    ImportDecision.READ_FILE -> "Read the selected file"
    ImportDecision.WRITE_RECORDS -> "Save validated records"
}
```

The interface is open when external modules provide decisions. A closed enum local to one implementation can still dispatch exhaustively. Text belongs at the parsing or logging edge. A legacy adapter can retain arbitrary existing identifiers without treating a log label as authority for lifecycle ownership.

## Cases with different payloads

Use a sealed type when the payload differs by case. This avoids a string tag beside several nullable fields.

```kotlin
sealed interface ImportResult {
    data class Imported(val rowCount: Int) : ImportResult
    data class Rejected(val reason: String) : ImportResult
    data object Cancelled : ImportResult
}
```

Check availability of syntax such as `data object` against the pinned compiler. Keep a public consumer extension interface open instead of sealing it for exhaustiveness.

## State values and compatibility

`data class RetryWindow(val startedAtMillis: Long, val deadlineMillis: Long)` makes the roles and equality visible. A local `mapOf("mode" to savedCode)` remains clear and uses a standard library pair appropriately. A public data class is convenient only when its generated API can be maintained. An immutable regular wrapper with additive constructors may better preserve a published record's constructor, accessors, destructuring and `copy` methods.

Before replacing a string or tuple, identify the domain invariant it will protect. Preserve equality components and bounded collections. Avoid increasing visibility just to share a type that one component owns.

## Review and verification

- Trace typed metadata from creation through submission, refresh, retries and completion. It must not be reconstructed from telemetry text.
- Check configuration parsing, saved unknown values and explicit external codes separately from domain dispatch.
- Compare public JVM signatures and run Java and Kotlin consumers compiled against the prior release. Recompiling them proves source compatibility only.
- For behavioral refactors, assert the important ordering, counters, deadlines, ownership and seeded random behavior. A passing formatter or enum-only test does not prove these contracts.
- Use the existing compiler and formatter plus focused regression checks. Treat a new lint framework as separate tooling work unless the change explicitly includes it.

Grade a verified broken contract as correctness or compatibility. Grade a house readability concern according to its demonstrated effect and the project's adopted policy. Do not copy project-specific terminology, code or private research into this portable reference.
