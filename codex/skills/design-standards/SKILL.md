---
name: design-standards
description: "UI/UX design standards and anti-slop guidelines: visual hierarchy, 8-point spatial grid, 5-state completeness, accessibility, and platform fidelity."
---

Read the project AGENTS.md and applicable global guidance first. When modifying UI components or screens, adhere to these anti-slop standards and native platform heuristics.

# UI/UX design standards

Use this playbook whenever creating, redesigning, or auditing user interfaces, screens, or reusable design-system components.

## Procedure

1. **Context and Aesthetic Commitment**:
   - Identify the target platform: Android (Jetpack Compose / Material Design 3), iOS (SwiftUI / Apple HIG), or Web/Desktop.
   - Establish a deliberate visual direction: commit to a clear tone (utilitarian/dense, editorial/minimal, technical/instrumented) and visual hierarchy before generating code or layouts.
   - Run the anti-slop checklist: veto generic purple/pink gradients, card soup, floating pill badges, emoji bullets, and unstyled typography defaults.

2. **Spatial Layout and Density**:
   - Align all margins, padding, and gaps to the 8-point spatial grid (`8, 16, 24, 32, 48, 64 dp/pt`), using 4 dp/pt solely for compact micro-spacing.
   - Group related elements by proximity (4–8 dp/pt) rather than wrapping every section in a nested card container.
   - Commit strictly to an intentional visual density: either high-density utility or airy breathing room. Never allow arbitrary or accidental padding (such as 11px or 23px).

3. **Typographic Hierarchy**:
   - Ensure a minimum 2:1 scale contrast between headings and body text.
   - Limit body text width to 45–75 characters per line for reading comfort.
   - Use native typography scales: Apple SF Pro / New York text styles on iOS; Material Design 3 type scale on Android; fluid typography with `clamp()` on Web.

4. **Verify the 5-State Completeness Law**:
   Explicitly design and implement all five user states for every interactive or data-driven view:
   - **Loading**: geometry-matching skeleton loaders or subtle progress bars. No full-screen blocking spinners for partial data.
   - **Populated**: standard view with robust truncation (`ellipsis`) and wrapping rules under variable content lengths.
   - **Empty**: contextual illustration/icon, clear explanation of why no content is present, and an actionable primary CTA.
   - **Error**: human-readable explanation of what happened (no raw stack traces or codes) with an immediate recovery action (Retry, Reconnect).
   - **Partial / Degraded**: graceful fallback when offline or services fail, displaying cached data with an unobtrusive status indicator.

5. **Accessibility and Ergonomics Audit**:
   - Contrast: verify minimum 4.5:1 contrast for normal text and 3:1 for large text or interactive controls.
   - Touch targets: enforce minimum 44×44 pt on iOS and minimum 48×48 dp on Android.
   - Dynamic Type / Scaling: verify that text expands up to 200% without clipping or layout breakage.
   - Screen reader semantics: ensure all interactive elements carry descriptive labels; mark purely decorative items hidden (`.accessibilityHidden(true)`, `contentDescription = null`).
   - Motion: honor system reduced-motion preferences with clean fades or instant state changes.

6. **Platform Fidelity**:
   - Android: semantic M3 color roles (`surfaceContainer`, `primary`, `onSurface`), full edge-to-edge layout with `WindowInsets`, responsive window size classes, native predictive back motion.
   - iOS: semantic system colors, native materials (`.ultraThinMaterial`), Safe Area insets, native haptic feedback, typed navigation data models.
   - Web: semantic HTML5 landmarks, CSS custom properties for tokens, container queries.

7. **Review**:
   - Delegate the resulting diff or component to `ui-reviewer` for independent grading against anti-slop criteria before declaring complete.
