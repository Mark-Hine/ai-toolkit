---
verified: 2026-09-29
sources:
  - https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md
  - https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md
  - https://www.swift.org/blog/swift-6.2-released/
  - https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/
paths:
  - "**/*.swift"
---

# Swift style (iOS repos)

- Formatting follows the repo's `.swiftformat` / `.swiftlint.yml`. Run the repo's formatter only if its `CLAUDE.md` says it
  works, otherwise format by hand to match surrounding code. Naming follows the Swift API Design Guidelines (clarity at the
  point of use, `ed`/`ing` for non-mutating variants, argument labels that read as a phrase).
- Optionals: no `!` force unwrap, `try!` or `as!` in production code. `guard let`/`if let` with an early return, `??`, or
  `preconditionFailure("<why>")` when nil is a programmer error. Matching the repo's `force_unwrapping` lint rule is not optional.
- Control flow: `guard` for preconditions, `switch` over enums kept exhaustive (no `default` that hides a new case),
  `enum` with associated values over parallel optionals or boolean flags.
- Types: models are `struct`s, and `final class` is only for identity-bearing state owners. Use `private` by default, `public` only
  at package boundaries. Dependencies come through `init` or `@Environment`, never `Something.shared` from feature code.
- Structured concurrency: `async`/`await` and `async let`/task groups over `Task.detached`, `DispatchQueue`, semaphores or
  completion handlers in new code. An unstructured `Task {}` is allowed only at a lifecycle boundary that owns and cancels
  it (view `.task`, `UIViewController` appear/disappear pair, app entry). No `DispatchQueue.main.async` to fix isolation.
- Isolation defaults: read the target's settings before adding annotations. `SWIFT_DEFAULT_ACTOR_ISOLATION` and `SWIFT_APPROACHABLE_CONCURRENCY` in Xcode, or `.defaultIsolation(MainActor.self)` and the `NonisolatedNonsendingByDefault` upcoming feature in a package, decide what unannotated code means. Under MainActor default isolation, unannotated code already runs on the main actor, so do not add `@MainActor` to it. Otherwise annotate the type `@MainActor`.
- With `NonisolatedNonsendingByDefault` on (Swift 6.2, SE-0461), a `nonisolated async` function runs on the caller's actor. Mark work that must leave the main actor, such as decoding, file IO or crypto, `@concurrent`, or put it in an actor. Main-safety belongs to the data layer, so view models `await` and never hop with `DispatchQueue` or `Task.detached`.
- Every `withCheckedContinuation` resumes exactly once. Prefer the throwing variant and propagate errors typed
  (`enum XError: Error`), not `NSError` or `String`.
- Inject time and randomness (`Clock`, `RandomNumberGenerator`) and network (`URLProtocol`-stubbable `URLSession` or a
  protocol seam) so tests are deterministic.
- Logging via `os.Logger` with `privacy: .private` for anything user-specific, with no `print` in production paths.
- Match the existing file's style over these rules when editing a legacy UIKit file. Do not reformat unrelated lines.
