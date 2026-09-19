---
paths:
  - "**/*ViewModel.swift"
  - "**/*Model.swift"
  - "**/*Screen.swift"
  - "**/*Route.swift"
  - "**/*Routes.swift"
  - "**/*Effect.swift"
  - "**/*Effects.swift"
  - "**/*State.swift"
  - "**/*Router.swift"
  - "**/*Coordinator.swift"
---

# One-shot model → UI events

Canonical code and rationale: `ios-standards` skill, `references/ui-events.md`.

- **Screen state** is one `enum State` (`loading` / `loaded(...)` / `error(...)`, `error` with cases when kinds differ)
  on a `@MainActor @Observable` model, `private(set)`, updated directly after `await`; no `DispatchQueue.main.async`.
- **Navigation, sheets and alerts are data, not events**: typed `enum Route: Hashable` in `path: [Route]` bound to
  `NavigationStack(path:)` with `navigationDestination(for:)`; `sheet: Sheet?` and `alert: Alert?` bound to `sheet(item:)`
  / `alert(item:)`. The system resets the binding on dismiss, so the model never clears presentation state by hand.
  The model never imports navigation or UIKit types; one `XRouteView` maps routes to views; deep links append the same routes.
- **Toasts are app-scoped**: the model calls an injected `ToastPresenter` (`@Observable`, in the environment); the root view
  renders the queue once. No screen owns toast state; a toast is never an alert.
- **True one-shot effects** (haptics, scroll-to, focus, `dismiss()`) go through the shared `EventStream<Effect>` (buffered,
  main actor, fresh stream per subscriber), consumed in `.task { for await e in model.effects.events { handle(e) } }` with an
  exhaustive `switch` in the screen. `.task` is cancelled when the view disappears; buffered effects arrive on re-subscribe.
- **Loading runs in the screen's `.task { await model.load() }`**, never in the model's `init` or `onAppear { Task {} }`.
- **Never**: boolean or optional triggers the model resets after a delay; a `PassthroughSubject`/`AsyncStream` iterated by
  more than one view or after cancellation; a sink `send(Action)` closure as the only API of a content view in new code;
  `NavigationLink(destination:)` for deep-linkable screens; `UINavigationController` or `dismiss` reached from a model.
- Below iOS 17 (project `AGENTS.md`): same shape with `ObservableObject` + `@Published` and `@StateObject`.
