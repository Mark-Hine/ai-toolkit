---
verified: 2026-09-29
sources:
  - https://developer.apple.com/documentation/swiftui/view/alert(_:ispresented:presenting:actions:message:)
  - https://developer.apple.com/documentation/swiftui/model-data
paths:
  - "**/*View.swift"
  - "**/*Screen.swift"
  - "**/*Content.swift"
  - "**/Views/**/*.swift"
  - "**/DesignSystem/**/*.swift"
---

# SwiftUI (iOS repos)

- Design system: screens use the project's design-system package (named in its `AGENTS.md`). Colours, type and spacing
  come from its tokens via `@Environment`, never `Color(red:…)`, hex or `.font(.system(size:))`. Project components and
  `ButtonStyle`/`ViewModifier` variants come before raw SwiftUI controls. Reference shape: `ios-standards` → `references/apple-samples.md`.
- Split screen-level views into a stateful `XScreen` that owns or receives the model and wires presentation, and a
  stateless `XContent(state:, actions:)` that renders. `#Preview` targets the stateless one with fixture data, no network, no DI graph.
- State ownership: one owner per value. Use `@State` for view-local UI state. The screen's `@MainActor @Observable` model is
  created by its owner (`@State private var model = XModel()`) and passed down as a value or `Binding`. Shared services go through
  `.environment(...)` at the root. Never copy model data into `@State` and sync by hand, and never create an
  `@ObservedObject`/model inline in `body`. Use `ObservableObject`/`@StateObject` only where the project's deployment target is below iOS 17.
- Side effects run in `.task {}` / `.task(id:)` so they cancel with the view. No `Task {}` in `onAppear`, and no loading in a model's `init`.
- One `enum State` per screen (`loading` / `empty` / `loaded(...)` / `error(...)`), with no `isLoading` + empty array sentinels.
- Presentation and navigation are data: `NavigationStack(path:)` with typed routes, `navigationDestination(item:)`,
  `sheet(item:)`, and `alert(_:isPresented:presenting:actions:message:)` bound to an optional through a `Binding(isPresent:)` helper. The modifier resets the binding on dismiss. Rule `ui-events.md` covers one-shot events.
- Lists: stable identity (`Identifiable` or an explicit stable `id`), never `id: \.self` on duplicable data or `UUID()` in `body`.
- Callbacks: leaves and reusable components take individual closures. Above five callbacks on a screen/section view, group
  them in an `XActions` struct of closures built once by the model. Never build it inside `body`, and never put state in it.
- Accessibility on every new control: `accessibilityLabel`/`Hint`/traits, a 44 by 44 pt hit region on buttons, never below the 28 pt HIG minimum, Dynamic Type via
  text styles or `@ScaledMetric`, layout checked at `accessibility-extra-large`, and decorative images `.accessibilityHidden(true)`.
- Layout adapts to size classes, with no fixed device-size frames and no orientation assumptions. Check iPad when the target supports it.
- Follow `guidance/design-standards.md` for design rules and their tiers. Screens design loading, loaded, empty and error, plus partial only where they show cached or offline data. Text uses Dynamic Type styles. Delegate UI diff reviews to `ui-reviewer`.
