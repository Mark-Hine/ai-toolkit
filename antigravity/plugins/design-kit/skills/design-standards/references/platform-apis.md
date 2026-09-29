---
verified: 2026-09-29
sources: inline
---

# Platform APIs per rule

The concrete Compose, SwiftUI and CSS APIs that satisfy each rule in `design-standards.md`. This is the only place API names appear, so the rule file stays readable and API churn lands here.

| Rule | Compose | SwiftUI | Web |
| --- | --- | --- | --- |
| TYP-1 | `MaterialTheme.typography.bodyLarge` and the other roles | `.font(.body)` and the other text styles, `Font.custom(_:size:relativeTo:)`, `@ScaledMetric` | platform or brand type scale as tokens |
| A11Y-3 | `Modifier.minimumInteractiveComponentSize()`. Material 3 components apply it by default | | |
| A11Y-4 | | `.frame(minWidth: 44, minHeight: 44)` with `.contentShape(Rectangle())` | |
| A11Y-5 | | | `min-width: 24px; min-height: 24px` or the spacing exception |
| A11Y-7 | `sp` units for text, `@Preview(fontScale = 2f)` | `accessibility-extra-large` in previews, `dynamicTypeSize(...)` | `rem` units, test at 200% zoom |
| A11Y-8 | `contentDescription`, `null` for decorative, `Modifier.semantics { role, stateDescription, heading() }` | `accessibilityLabel`, `.accessibilityHidden(true)`, `.accessibilityAddTraits(.isHeader)` | `alt=""`, `aria-hidden="true"`, native elements before ARIA roles |
| A11Y-9 | Compose animations follow the animator duration scale, so the Remove animations setting stops them (community-documented, confirm against official docs). Read `Settings.Global.ANIMATOR_DURATION_SCALE` only for non-Compose animators | `@Environment(\.accessibilityReduceMotion)` | `@media (prefers-reduced-motion: reduce)` |
| AND-1 | `MaterialTheme.colorScheme.surfaceContainer`, `primary`, `onSurface` and the other roles | | |
| AND-2 | `enableEdgeToEdge()`, `Scaffold` content padding, `WindowInsets.safeDrawing`, `Modifier.imePadding()`, the `edge-to-edge` skill | | |
| AND-3 | `currentWindowAdaptiveInfo(supportLargeAndXLargeWidth = true).windowSizeClass`, the `adaptive` skill | | |
| AND-4 | `android:screenOrientation` is ignored at sw600dp from target 36. `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` is the temporary opt-out | | |
| AND-5 | `MaterialTheme.motionScheme`, `MotionScheme.expressive()`, `MotionScheme.standard()`, spatial and effects specs (confirm member names against the current material3 release) | | |
| AND-6 | `BackHandler`, `PredictiveBackHandler`, `OnBackPressedDispatcher`, Navigation 3 `NavigationBackHandler` | | |
| IOS-1 | | `Color(.systemBackground)`, `Color(.label)`, `Color(.secondarySystemBackground)`, asset catalog colours with dark and high-contrast variants | |
| IOS-2 | | system `toolbar` and `TabView` adopt glass. Custom glass through `glassEffect` behind `if #available(iOS 26, *)`. Content backgrounds use `.regularMaterial` | |
| IOS-3 | | `safeAreaInset(edge:alignment:spacing:content:)` (iOS 15), `safeAreaPadding` (iOS 17), `GeometryProxy.safeAreaInsets`, `ignoresSafeArea` for backgrounds only | |
| IOS-4 | | `.sensoryFeedback(_:trigger:)` (iOS 17), `UINotificationFeedbackGenerator` below iOS 17 | |
| WEB-1 | | | `<main>`, `<nav>`, `<header>`, `<footer>`, `<article>` |
| WEB-2 | | | `font-size: clamp(1rem, 0.9rem + 0.5vw, 2rem)` |
| WEB-3 | | | `--space-4: 1rem` and friends on `:root` |
| WEB-4 | | | `@container` with `container-type` on the parent |
