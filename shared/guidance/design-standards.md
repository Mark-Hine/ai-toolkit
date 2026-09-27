# UI/UX Design Standards and Anti-Slop Guidelines

UI and UX standards to prevent generic AI interface output ("AI slop") and build intentional, accessible, platform-native interfaces across mobile and web.

## Anti-Slop Directives

- Commit to a clear aesthetic direction before generating UI: define purpose, tone (utilitarian/dense, editorial/minimal, technical/instrumented), visual weight, and platform idioms.
- Ban AI visual clichés: no unmotivated purple-to-blue or pink gradients on dark cards; no decorative neon glow borders; no floating pill badges or eyebrows stacked over every header; no emoji-bullet lists.
- Avoid container soup: do not nest cards inside cards inside cards with redundant borders, shadows, and inconsistent radii. Group elements using whitespace, typographic hierarchy, and subtle background differentiation rather than stacked containers.
- Avoid default typographic monoculture: do not leave interfaces on unstyled system sans-serif without role definitions. Pair an expressive headline with a clean, readable body style, and maintain intentional weight and size contrast.

## The 8-Point Spatial System

- Base spatial scale: use multiples of 8 (`8, 16, 24, 32, 48, 64 dp/pt`) for layout, component padding, and section margins. Use 4 dp/pt only for compact micro-spacing (icon-to-label gaps, tight badge padding).
- Group by proximity: related items stay close (4–8 dp/pt); distinct items within a component separate by 12–16 dp/pt; unrelated sections separate by 24–32+ dp/pt.
- Density commitment: commit deliberately to either a high-density utility layout (data tables, inspection tools) or an airy, spacious layout (consumer workflows, long-form reading). Never produce accidental, unconsidered padding like 11px or 23px.

## Typographic Hierarchy and Readability

- Scale contrast: headings must have at least a 2:1 visual weight/scale difference over body text to establish clear focal points.
- Line length and ergonomics: limit body text to 45–75 characters per line for comfortable reading. Ensure line height scales proportionally (1.4–1.6× font size for body text; 1.1–1.25× for titles).
- Native typography scales: use Apple SF Pro / New York text styles (`.font(.title)`, `.font(.body)`) on iOS, and Material Design 3 type scale (`MaterialTheme.typography`) on Android.

## The 5-State Completeness Law

Every interactive screen or data-driven component must explicitly design and handle five discrete states:

1. **Loading State**: use geometry-matching skeleton loaders or subtle progress bars. Never present a full-screen blocking spinner for partial or secondary content.
2. **Populated State**: the ideal data view with explicit text truncation (`ellipsis`), wrapping rules, and whitespace discipline under variable content lengths.
3. **Empty State**: present a purposeful icon or illustration, an honest explanation of why no content is visible, and a clear primary action to create or discover content.
4. **Error State**: explain what failed in plain language (no raw stack traces or error codes) and provide an immediate, actionable recovery mechanism (Retry, Reconnect, Dismiss).
5. **Partial / Degraded State**: preserve cached or offline data when a network request fails, accompanied by an unobtrusive status banner or inline badge.

## Accessibility and Ergonomics (WCAG 2.1 AA/AAA)

- Color contrast: maintain a minimum contrast ratio of 4.5:1 for standard body text against its background, and 3:1 for large text (>=18pt or bold >=14pt) and essential UI controls or borders.
- Interactive touch targets: minimum 44×44 pt on iOS and minimum 48×48 dp on Android. Add invisible padding if a visual element is smaller than the required hit area.
- Dynamic Type and Font Scaling: layouts must expand gracefully without clipping, truncation without ellipsis, or overlapping containers when users scale text up to 200%.
- Screen reader semantics: assign descriptive accessibility labels and roles to interactive elements. Explicitly hide purely decorative icons or backgrounds (`.accessibilityHidden(true)`, `contentDescription = null`).
- Motion sensitivity: respect system reduced-motion preferences (`@Environment(\.accessibilityReduceMotion)`, `LocalAccessibilityManager`). Replace bouncy transitions with clean fades or instant state changes.

## Platform Fidelity

### Android (Material Design 3 & Jetpack Compose)

- Use semantic M3 color roles (`MaterialTheme.colorScheme.primary`, `surfaceContainer`, `onSurface`, etc.). Never hardcode raw hex values (`Color(0xFF...)`).
- Full edge-to-edge layout: handle `WindowInsets.systemBars`, `imePadding()`, and display cutouts.
- Responsive breakpoints: design adaptively for Compact (<600dp), Medium (600–840dp), and Expanded (>840dp) window size classes. Never lock screen orientation.
- Native motion: use standard Material 3 easing curves and predictive back navigation animations.

### iOS (Human Interface Guidelines & SwiftUI)

- Use semantic system colors (`Color(.systemBackground)`, `Color(.label)`, `.secondarySystemBackground`) and materials (`.ultraThinMaterial`, `.regularMaterial`) that support light, dark, and high-contrast modes.
- Respect Safe Areas (`SafeAreaInsets`): never allow interactive content or readable text to clip behind the status bar, Dynamic Island, or home indicator.
- Native sensory feedback: trigger subtle, intentional haptics (`UIImpactFeedbackGenerator`, `SensoryFeedback`) on discrete success, warning, or state toggle actions.
- Navigation patterns: model navigation as data via `NavigationStack(path:)`, sheets, and alerts with typed routes.

### Web and Responsive Frontends

- Semantic structure: use standard HTML5 landmarks (`<main>`, `<nav>`, `<article>`, `<header>`, `<footer>`).
- Design tokens: define colors, radii, shadows, and spacing scales via CSS custom properties (`var(--space-md)`).
- Fluid layouts: use CSS container queries and fluid typography (`clamp()`) rather than brittle device-width breakpoints.
