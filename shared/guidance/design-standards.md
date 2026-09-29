---
verified: 2026-09-29
sources:
  - https://developer.apple.com/design/human-interface-guidelines
  - https://m3.material.io
  - https://www.w3.org/TR/WCAG22/
  - https://developer.android.com/develop/ui
  - https://developer.mozilla.org/en-US/docs/Web
---

# Design standards

Rules for building and reviewing UI on Android, iOS and the web. Every rule has an ID, a tier and a source key.

- `T1` rules trace to Apple HIG, Material 3, WCAG 2.2, Android developer docs or MDN. A breach grades Blocker or Major, by user impact.
- `T2` rules are house preference with a named origin. A breach grades Nit unless the project instructions file opts the rule in by ID.
- Source keys resolve in the design standards skill, `references/sources.md`. The reason for each T2 rule is in `references/rationale.md`. The Compose, SwiftUI and CSS APIs for each rule are in `references/platform-apis.md`.
- A correctness defect stays a defect whatever the tier. A crash, a screen stuck on a spinner after a failure, or an error with no way forward grades as a bug.
- When a rule and its source disagree, the source wins. Report the disagreement.
- IDs are stable. A retired ID is never reused.

## Direction

- DIR-1 [T2 Anthropic-FD] Decide the purpose, tone and density of a screen before writing it. Dense utility screens and airy reading screens are both valid. Mixing the two by accident is the failure.
- DIR-2 [T2 Anthropic-FD] Avoid the defaults that models converge on, such as purple or blue gradients on white or dark cards and one sans face for everything on the web.
- DIR-3 [T2 House] Use a gradient only when the brand or the content motivates it, such as a brand surface in the design system or a scrim that keeps text legible over an image. Build it once as a design-system component and reuse it. JetSnack's gradient buttons and surfaces meet this rule.
- DIR-4 [T2 House] No decorative glow borders, no pill badge or eyebrow label over every header, and no emoji used as bullets.
- DIR-5 [T2 House] Do not nest cards inside cards. Group related content with spacing, type hierarchy and a background change before adding a container. A container gets one border or one elevation, with a radius from the design system.

## Spacing

- SPC-1 [T1 M3-SPACING] On Android, spacing follows the Material 3 8 dp scale. Icons, type baselines and other small elements may align to 4 dp. Values come from the project's spacing tokens.
- SPC-2 [T1 HIG-LAYOUT] HIG defines no spacing grid. On iOS, respect the system layout margins, the safe area and the default spacing of stacks and lists.
- SPC-3 [T2 House] On iOS and the web, keep custom spacing on a 4 or 8 unit token scale. Native components keep their built-in spacing and are not adjusted to fit the scale.
- SPC-4 [T2 House] Group by proximity. Related items sit 4 to 8 units apart, distinct items inside a component 12 to 16, and unrelated sections 24 or more.
- SPC-5 [T2 House] Every spacing value in layout code comes from a token. A literal such as 11 or 23 is a finding.

## Typography

- TYP-1 [T1 HIG-TYPOGRAPHY, M3-TYPE] Use the platform type scale. iOS uses the built-in text styles so Dynamic Type works. Android uses the Material 3 type roles through the project theme. Hierarchy comes from the roles the scale defines, so do not impose a size ratio between headings and body text.
- TYP-2 [T2 Anthropic-FD] Choose a display face only when the brand calls for it, and ship it through the design system with text scaling intact. The system face with defined roles is a deliberate choice.
- TYP-3 [T2 Bringhurst, Butterick, WCAG-1.4.8] Keep body text at 45 to 75 characters per line where the layout is wide enough to exceed it. Butterick's 45 to 90 is the outer bound. WCAG 1.4.8 caps lines at 80 characters at level AAA.
- TYP-4 [T1 HIG-TYPOGRAPHY, M3-TYPE] Keep the leading that each platform text style defines. Do not force a fixed line-height ratio onto native styles.
- TYP-5 [T1 WCAG-1.4.12] On the web, content survives a user setting line height to 1.5, paragraph spacing to 2, letter spacing to 0.12 and word spacing to 0.16 times the font size.

## Screen states

- STA-1 [T2 Hurff] Every data-driven screen designs loading, loaded, empty and error. It adds partial only where the screen shows cached or offline data.
- STA-2 [T2 House] Model the states with the platform rules. Android uses one sealed `UiState` and iOS one `enum State`. Empty is its own case when the screen can be empty. Partial is a case or flag on the loaded data.
- STA-3 [T2 House] Loading shows a skeleton that matches the loaded layout, or a small progress indicator for secondary content. No full-screen blocking spinner for content that arrives in parts.
- STA-4 [T2 House] Loaded handles long and short content, with truncation or wrapping decided for each text field.
- STA-5 [T2 House] Empty says why nothing is shown and offers the next action.
- STA-6 [T2 House] Error says what failed in plain words and offers a recovery action such as Retry. No raw error codes or stack traces.
- STA-7 [T2 House] Partial keeps the cached data on screen and shows a small banner or badge saying it may be out of date.

## Accessibility

- A11Y-1 [T1 WCAG-1.4.3, HIG-ACCESSIBILITY] Text contrast is at least 4.5:1. Large text, 18 pt or 14 pt bold and above, needs at least 3:1.
- A11Y-2 [T1 WCAG-1.4.11] Controls, focus indicators and meaningful graphics have at least 3:1 contrast against adjacent colours.
- A11Y-3 [T1 AND-A11Y] Android touch targets are at least 48 by 48 dp, padded when the visual element is smaller.
- A11Y-4 [T1 HIG-BUTTONS, HIG-ACCESSIBILITY] iOS buttons have a hit region of at least 44 by 44 pt. The HIG minimum for any control is 28 by 28 pt.
- A11Y-5 [T1 WCAG-2.5.8] Web pointer targets are at least 24 by 24 CSS px, or meet the spacing exception.
- A11Y-6 [T2 WCAG-2.5.5] Touch layouts on the web aim for 44 by 44 CSS px, the AAA size.
- A11Y-7 [T1 WCAG-1.4.4, HIG-ACCESSIBILITY, AND-FONT-SCALE] Text scales to 200% without clipping, overlap or lost content. Check the largest accessibility text size on iOS and 200% font scale on Android.
- A11Y-8 [T1 WCAG-4.1.2, HIG-ACCESSIBILITY, AND-A11Y] Every interactive element has a name and role that a screen reader announces. Decorative images and icons are hidden from assistive technology.
- A11Y-9 [T1 HIG-ACCESSIBILITY, AND-ANIM-SCALE, MDN-REDUCED-MOTION] Honour the system reduced-motion setting. That is Reduce Motion on iOS, Remove animations on Android and `prefers-reduced-motion` on the web. Replace large movement, zoom and parallax with fades or instant changes. WCAG 2.3.3 asks for this at AAA.

## Android

- AND-1 [T1 M3-COLOR] Colours come from Material 3 colour roles through the project theme. No raw colour values in UI code.
- AND-2 [T1 AND-EDGE] Draw edge to edge and handle system bar, IME and display cutout insets.
- AND-3 [T1 AND-WSC] Adapt layout to the width window size classes. They are Compact under 600 dp, Medium 600 to 839 dp, Expanded 840 to 1199 dp, Large 1200 to 1599 dp and Extra-large 1600 dp and wider. Opt in to Large and Extra-large when the layout uses them.
- AND-4 [T1 AND-16-LARGE] Do not rely on orientation or resizability locks on large screens. From target SDK 36, Android ignores orientation, resizability and aspect-ratio restrictions on displays with a smallest width of 600 dp or more. The temporary opt-out ends at target SDK 37. Displays below 600 dp smallest width keep the manifest value.
- AND-5 [T1 M3-MOTION] Use the Material 3 motion scheme, whose springs cover spatial and effects motion, instead of hand-tuned easing curves and durations.
- AND-6 [T1 AND-16-LARGE] Support predictive back. From target SDK 36 on Android 16, predictive back animations are on by default and `onBackPressed` is no longer called, so back handling uses the supported back APIs.

## iOS

- IOS-1 [T1 HIG-COLOR] Use semantic system colours, or design-system colours that define light, dark and increased-contrast variants.
- IOS-2 [T1 HIG-MATERIALS] From iOS 26, standard bars and controls adopt Liquid Glass automatically. Do not use Liquid Glass in the content layer. Use standard materials for content backgrounds, and apply glass to custom controls sparingly.
- IOS-3 [T1 HIG-LAYOUT] Keep controls and readable text inside the safe area. Backgrounds may extend under the status bar, Dynamic Island and home indicator.
- IOS-4 [T1 HIG-HAPTICS] Use haptics sparingly and consistently, for discrete events such as a success, a warning or a toggle. Each haptic maps to one cause.

## Web

- WEB-1 [T1 MDN-LANDMARKS, WCAG-1.3.1] Structure pages with landmark elements, such as `main`, `nav`, `header`, `footer` and `article`.
- WEB-2 [T1 WCAG-1.4.4, MDN-CLAMP] Fluid type uses `clamp()` with a `rem` minimum and a maximum at least twice the minimum, so browser zoom still reaches 200%.
- WEB-3 [T2 House] Define colour, radius, shadow and spacing tokens as CSS custom properties.
- WEB-4 [T2 House] Use container queries for component layout. Media queries still own page layout.
