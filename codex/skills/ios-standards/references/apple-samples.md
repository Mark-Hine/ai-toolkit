# Apple sample apps as SwiftUI blueprints

Apple ships no architecture guide; its samples are the closest thing to a reference implementation. Imported from the Claude reference dated 2026-09-04. Recheck version-sensitive claims against the linked sources before use.

| Sample | Source | Requires | Use it for |
|---|---|---|---|
| Landmarks (2025) | https://developer.apple.com/documentation/swiftui/landmarks-building-an-app-with-liquid-glass | Xcode 26, iOS 26 | Current SwiftUI shape: `NavigationSplitView`, Liquid Glass toolbars and badges, `matchedGeometryEffect`, Icon Composer icons |
| Backyard Birds | https://github.com/apple/sample-backyard-birds · https://developer.apple.com/documentation/swiftui/backyard-birds-sample | Xcode 15, iOS 17.2 | Model layer split into packages (`BackyardBirdsData`, `BackyardBirdsUI`, `LayeredArtworkLibrary`), SwiftData + Observation, a `Styles.swift` design-system layer, widgets via App Intents, StoreKit views |
| Food Truck | https://github.com/apple/sample-food-truck · https://developer.apple.com/documentation/swiftui/food-truck-building-a-swiftui-multiplatform-app | Xcode 14.3, iOS 16.4 | `NavigationSplitView` + `NavigationStack` with `@State` selection/path at the app root, shared `FoodTruckKit` package, Charts, custom `Layout`, Live Activities |
| Fruta | https://developer.apple.com/documentation/appclip/fruta-building-a-feature-rich-app-with-swiftui | Xcode 13.3, iOS 15.4 | One `App` shared across app, App Clip and widget targets; older data-flow APIs (`ObservableObject`), read for structure only |
| Destination Video | https://developer.apple.com/documentation/visionos/destination-video | Xcode 16, iOS 18 | Tab/sidebar adaptivity across size classes, SwiftData persistence |

## Shape to mirror
- **Model code in a Swift package**, UI in the app target or a UI package; the app target is a thin composition root that
  builds the model once and injects it with `.environment(model)` (Backyard Birds, Food Truck). Feature packages depend on
  shared packages, never on each other.
- **One `@Observable` model per screen or domain**, `@MainActor`, exposing values the view reads directly; views hold
  only view-local `@State`. Navigation state (`selection`, `path`) lives with the view that owns the `NavigationStack`/`NavigationSplitView`.
- **Design-system layer**: `ButtonStyle`, `LabelStyle` and `ViewModifier` conformances plus `@ViewBuilder` slots instead
  of boolean appearance flags; tokens read from the environment; asset-catalog colours with dark variants; every component
  has a `#Preview` with fixture data. This is the design-system package's shape too (named in each repo's `AGENTS.md`).
- **Navigation as data**: typed route values, `NavigationStack(path:)`, `navigationDestination(for:)`; deep links construct
  the same values. A home-grown router is fine if it is typed and centralised.
- **Liquid Glass (iOS 26)**: adopt system components and let the toolbar/tab bar render glass; custom glass only through
  the documented `glassEffect` APIs, gated on deployment target.

## Cautions
- Samples ship without unit tests and without networking or DI beyond the environment. Use the official docs
  (`official-docs.md`) for concurrency, testing and security; use the sample for structure and SwiftUI API usage.
- Each sample targets the OS it launched with. `@Observable` needs iOS 17, Swift Testing needs Xcode 16, Liquid Glass
  needs iOS 26. Repos with a lower deployment target keep `ObservableObject`/`@StateObject` for those screens and say so in `AGENTS.md`.
- Samples are single-brand and single-environment. Multi-scheme environment config, Firebase plists per environment and
  CocoaPods interop are app-repo concerns the samples do not cover.
