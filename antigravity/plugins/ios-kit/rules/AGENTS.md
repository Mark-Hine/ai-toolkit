# iOS and Swift Rules

These rules apply when working with iOS and Swift code in this repository.

## Subagents and Specialist Delegation

- Delegate current platform research to `ios-researcher` (`model: flash`, read-only).
- Delegate non-trivial diff review to `ios-reviewer` (`model: pro`, high reasoning, read-only).
- Delegate test execution and simulator evidence collection to `ios-verifier` (`model: pro`, workspace writes enabled).
- When specialists are not yet defined, configure them with `define_subagent` using the specifications in `agents/` and invoke them with `invoke_subagent`.

## Swift Style

- Formatting follows the repo's `.swiftformat` / `.swiftlint.yml`; run the repo's formatter only if its `AGENTS.md` says it works, otherwise format by hand to match surrounding code. Naming follows the Swift API Design Guidelines (clarity at the point of use, `ed`/`ing` for non-mutating variants, argument labels that read as a phrase).
- Optionals: no `!` force unwrap, `try!` or `as!` in production code. `guard let`/`if let` with an early return, `??`, or `preconditionFailure("<why>")` when nil is a programmer error.
- Control flow: `guard` for preconditions, `switch` over enums kept exhaustive (no `default` that hides a new case), `enum` with associated values over parallel optionals or boolean flags.
- Types: models are `struct`s; `final class` only for identity-bearing state owners; `private` by default, `public` only at package boundaries. Dependencies come through `init` or `@Environment`, never `Something.shared` from feature code.
- Structured concurrency: `async`/`await` and `async let`/task groups over `Task.detached`, `DispatchQueue`, semaphores or completion handlers in new code. An unstructured `Task {}` is allowed only at a lifecycle boundary that owns and cancels it (view `.task`, `UIViewController` appear/disappear pair, app entry). No `DispatchQueue.main.async` to fix isolation: annotate the type `@MainActor` instead. Main-safety belongs to the data layer (`nonisolated`/actor), so view models `await`.
- Every `withCheckedContinuation` resumes exactly once; prefer the throwing variant and propagate errors typed (`enum XError: Error`), not `NSError` or `String`.
- Inject time and randomness (`Clock`, `RandomNumberGenerator`) and network (`URLProtocol`-stubbable `URLSession` or a protocol seam) so tests are deterministic.
- Logging via `os.Logger` with `privacy: .private` for anything user-specific; no `print` in production paths.
- Match existing file style when editing legacy UIKit files; avoid reformatting unrelated lines.

## SwiftUI

- Design system: screens use the project's design-system package (named in its `AGENTS.md`); colours, type and spacing come from its tokens via `@Environment`, never `Color(red:…)`, hex or `.font(.system(size:))`; project components and `ButtonStyle`/`ViewModifier` variants before raw SwiftUI controls.
- Split screen-level views into a stateful `XScreen` that owns or receives the model and wires presentation, and a stateless `XContent(state:, actions:)` that renders. `#Preview` targets the stateless one with fixture data, no network, no DI graph.
- State ownership: one owner per value. `@State` for view-local UI state; the screen's `@MainActor @Observable` model created by its owner (`@State private var model = XModel()`) and passed down as a value or `Binding`; shared services via `.environment(...)` at the root. Never copy model data into `@State` and sync by hand; never create an `@ObservedObject`/model inline in `body`. Use `ObservableObject`/`@StateObject` only where the project's deployment target is below iOS 17.
- Side effects run in `.task {}` / `.task(id:)` so they cancel with the view; no `Task {}` in `onAppear`, no loading in a model's `init`.
- One `enum State` per screen (`loading` / `empty` / `loaded(...)` / `error(...)`); no `isLoading` + empty array sentinels.
- Presentation and navigation are data: `NavigationStack(path:)` with typed routes, `navigationDestination(item:)`, `sheet(item:)`, `alert(item:)`; the modifier resets the binding on dismiss.
- Lists: stable identity (`Identifiable` or an explicit stable `id`), never `id: \.self` on duplicable data or `UUID()` in `body`.
- Callbacks: leaf views take individual closures. Above five callbacks on a screen/section view, group them in an `XActions` struct of closures built once by the model. Never build it inside `body`; never put state in it.
- Accessibility on every new control: `accessibilityLabel`/`Hint`/traits, 44×44 pt minimum hit target, Dynamic Type via text styles or `@ScaledMetric`, layout checked at `accessibility-extra-large`; decorative images `.accessibilityHidden(true)`.
- Layout adapts to size classes; no fixed device-size frames, no orientation assumptions; check iPad when the target supports it.

## One-Shot Model to UI Events

- **Screen state** is one `enum State` (`loading` / `loaded(...)` / `error(...)`) on a `@MainActor @Observable` model, `private(set)`, updated directly after `await`; no `DispatchQueue.main.async`.
- **Navigation, sheets and alerts are data, not events**: typed `enum Route: Hashable` in `path: [Route]` bound to `NavigationStack(path:)` with `navigationDestination(for:)`; `sheet: Sheet?` and `alert: Alert?` bound to `sheet(item:)` / `alert(item:)`. The system resets the binding on dismiss. ViewModels never import navigation or UIKit types.
- **Toasts are app-scoped**: the model calls an injected `ToastPresenter` (`@Observable`, in the environment); root view renders the queue once.
- **True one-shot effects** (haptics, scroll-to, focus, `dismiss()`) go through shared `EventStream<Effect>` (buffered, main actor, fresh stream per subscriber), consumed in `.task { for await e in model.effects.events { handle(e) } }` with an exhaustive `switch` in the screen.
- **Loading runs in the screen's `.task { await model.load() }`**, never in the model's `init` or `onAppear { Task {} }`.
- **Never**: boolean or optional triggers the model resets after a delay; `PassthroughSubject`/`AsyncStream` iterated by multiple views; `NavigationLink(destination:)` for deep-linkable screens; `UINavigationController` or `dismiss` called from a model.

## Tests and Verification

- Framework per repo, named in its `AGENTS.md`: Swift Testing (`@Test`, `#expect`, `#require`, `@Suite`) for new tests where adopted; otherwise XCTest. UI tests (`XCUIApplication`) stay in XCTest.
- Async: `async` test functions with `await`; Swift Testing `confirmation` or XCTest `fulfillment(of:)` for callbacks. No `sleep` or generous waits; inject a `Clock`.
- Parallel tests: no shared mutable statics, `UserDefaults.standard` or Keychain without an isolated suite name.
- Bug fixes start with a failing test reproducing the report, then the fix, then green.
- Run targeted: `xcodebuild test -workspace <ws> -scheme "<test scheme>" -destination '<sim>' -only-testing:<Target>/<Suite>` using the command form from `AGENTS.md`. Summarise with `xcrun xcresulttool get test-results summary`.
- Hand test and simulator smoke checks off to `ios-verifier`.
