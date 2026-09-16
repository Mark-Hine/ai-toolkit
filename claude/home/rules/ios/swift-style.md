---
paths:
  - "**/*.swift"
---

# Swift style (iOS repos)

- Formatting follows the repo's `.swiftformat` / `.swiftlint.yml`; run the repo's formatter only if its `CLAUDE.md` says it
  works, otherwise format by hand to match surrounding code. Naming follows the Swift API Design Guidelines (clarity at the
  point of use, `ed`/`ing` for non-mutating variants, argument labels that read as a phrase).
- Optionals: no `!` force unwrap, `try!` or `as!` in production code. `guard let`/`if let` with an early return, `??`, or
  `preconditionFailure("<why>")` when nil is a programmer error. Matching the repo's `force_unwrapping` lint rule is not optional.
- Control flow: `guard` for preconditions, `switch` over enums kept exhaustive (no `default` that hides a new case),
  `enum` with associated values over parallel optionals or boolean flags.
- Types: models are `struct`s; `final class` only for identity-bearing state owners; `private` by default, `public` only
  at package boundaries. Dependencies come through `init` or `@Environment`, never `Something.shared` from feature code.
- Structured concurrency: `async`/`await` and `async let`/task groups over `Task.detached`, `DispatchQueue`, semaphores or
  completion handlers in new code. An unstructured `Task {}` is allowed only at a lifecycle boundary that owns and cancels
  it (view `.task`, `UIViewController` appear/disappear pair, app entry). No `DispatchQueue.main.async` to fix isolation:
  annotate the type `@MainActor` instead. Main-safety belongs to the data layer (`nonisolated`/actor), so view models `await`.
- Every `withCheckedContinuation` resumes exactly once; prefer the throwing variant and propagate errors typed
  (`enum XError: Error`), not `NSError` or `String`.
- Inject time and randomness (`Clock`, `RandomNumberGenerator`) and network (`URLProtocol`-stubbable `URLSession` or a
  protocol seam) so tests are deterministic.
- Logging via `os.Logger` with `privacy: .private` for anything user-specific; no `print` in production paths.
- Match the existing file's style over these rules when editing a legacy UIKit file; do not reformat unrelated lines.
