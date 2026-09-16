---
paths:
  - "**/*View.swift"
  - "**/*Screen.swift"
  - "**/*Content.swift"
  - "**/Views/**/*.swift"
  - "**/DesignSystem/**/*.swift"
---

# SwiftUI (iOS repos)

- Design system: screens use the project's design-system package (named in its `CLAUDE.md`); colours, type and spacing
  come from its tokens via `@Environment`, never `Color(red:…)`, hex or `.font(.system(size:))`; project components and
  `ButtonStyle`/`ViewModifier` variants before raw SwiftUI controls. Reference shape: `ios-kit:standards` → `references/apple-samples.md`.
- Split screen-level views into a stateful `XScreen` that owns or receives the model and wires presentation, and a
  stateless `XContent(state:, actions:)` that renders. `#Preview` targets the stateless one with fixture data, no network, no DI graph.
- State ownership: one owner per value. `@State` for view-local UI state; the screen's `@MainActor @Observable` model
  created by its owner (`@State private var model = XModel()`) and passed down as a value or `Binding`; shared services via
  `.environment(...)` at the root. Never copy model data into `@State` and sync by hand; never create an
  `@ObservedObject`/model inline in `body`. Use `ObservableObject`/`@StateObject` only where the project's deployment target is below iOS 17.
- Side effects run in `.task {}` / `.task(id:)` so they cancel with the view; no `Task {}` in `onAppear`, no loading in a model's `init`.
- One `enum State` per screen (`loading` / `empty` / `loaded(...)` / `error(...)`); no `isLoading` + empty array sentinels.
- Presentation and navigation are data: `NavigationStack(path:)` with typed routes, `navigationDestination(item:)`,
  `sheet(item:)`, `alert(item:)`; the modifier resets the binding on dismiss. Rule `ui-events.md` covers one-shot events.
- Lists: stable identity (`Identifiable` or an explicit stable `id`), never `id: \.self` on duplicable data or `UUID()` in `body`.
- Callbacks: leaves and reusable components take individual closures. Above five callbacks on a screen/section view, group
  them in an `XActions` struct of closures built once by the model. Never build it inside `body`; never put state in it.
- Accessibility on every new control: `accessibilityLabel`/`Hint`/traits, 44×44 pt minimum hit target, Dynamic Type via
  text styles or `@ScaledMetric`, layout checked at `accessibility-extra-large`; decorative images `.accessibilityHidden(true)`.
- Layout adapts to size classes; no fixed device-size frames, no orientation assumptions; check iPad when the target supports it.
