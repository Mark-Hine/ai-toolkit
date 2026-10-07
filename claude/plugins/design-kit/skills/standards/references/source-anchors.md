---
verified: 2026-10-07
sources: inline
---

# Design source anchors

Each source key in `design-standards.md` and `sources.md`, pinned to its page and to the sentence or two
the rule rests on. Grade from the rules and quote the anchor when a rule is disputed. Do not fetch a
page to grade a rule. `tools/source_anchors.py` confirms every quote against the live page and records
the date. The format and the maintenance steps are in the ai-toolkit repo, `docs/source-anchors.md`.

Quotes are verbatim and short, and each names its page. Copyright stays with the source's owner.

## Apple Human Interface Guidelines

### HIG-ACCESSIBILITY
- URL: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Quote: "iOS, iPadOS 44x44 pt 28x28 pt"
- Quote: "Ideally, give people the option to enlarge text by at least 200 percent (or 140 percent in watchOS apps)."
- Quote: "People who are prone to these effects can turn on the Reduce Motion accessibility setting."
- Confirmed: 2026-10-07 (apple-json)

### HIG-BUTTONS
- URL: https://developer.apple.com/design/human-interface-guidelines/buttons
- Quote: "As a general rule, a button needs a hit region of at least 44x44 pt — in visionOS, 60x60 pt — to ensure that people can select it easily, whether they use a fingertip, a pointer, their eyes, or a remote."
- Confirmed: 2026-10-07 (apple-json)

### HIG-MATERIALS
- URL: https://developer.apple.com/design/human-interface-guidelines/materials
- Quote: "Don’t use Liquid Glass in the content layer."
- Quote: "In contrast to Liquid Glass, the standard materials help with visual differentiation within the content layer."
- Confirmed: 2026-10-07 (apple-json)

### HIG-TYPOGRAPHY
- URL: https://developer.apple.com/design/human-interface-guidelines/typography
- Quote: "Consider using the built-in text styles."
- Quote: "Using text styles with the system fonts also ensures support for Dynamic Type and larger accessibility type sizes (where available), which let people choose the text size that works for them."
- Confirmed: 2026-10-07 (apple-json)

### HIG-HAPTICS
- URL: https://developer.apple.com/design/human-interface-guidelines/playing-haptics
- Quote: "Use haptics consistently throughout your app or game."
- Quote: "Avoid overusing haptics."
- Confirmed: 2026-10-07 (apple-json)

### HIG-APP-ICONS
- URL: https://developer.apple.com/design/human-interface-guidelines/app-icons
- Quote: "In iOS, iPadOS, and macOS, people can choose whether their Home Screen app icons are default, dark, clear, or tinted in appearance."
- Quote: "iOS, iPadOS, macOS Square Rounded rectangle (square) 1024x1024 px Layered"
- Confirmed: 2026-10-07 (apple-json)

### HIG-LAYOUT
- URL: https://developer.apple.com/design/human-interface-guidelines/layout
- Quote: "Respecting the safe area is essential to make sure system UI and hardware features like the Dynamic Island don’t obstruct content and controls."
- Confirmed: 2026-10-07 (apple-json)

### HIG-COLOR
- URL: https://developer.apple.com/design/human-interface-guidelines/color
- Quote: "Avoid hard-coding system color values in your app."
- Quote: "Each dynamic color is semantically defined by its purpose, rather than its appearance or color values."
- Confirmed: 2026-10-07 (apple-json)

## Material 3

### M3-SPACING
- URL: https://m3.material.io/styles/spacing/overview
- Quote: "Spacing units follow an 8dp scale."
- Confirmed: 2026-10-07 (browser)

### M3-TYPE
- URL: https://m3.material.io/styles/typography/type-scale-tokens
- Quote: "Material 3 has one type scale containing two sets of type styles: 15 baseline and 15 emphasized."
- Confirmed: 2026-10-07 (browser)

### M3-COLOR
- URL: https://m3.material.io/styles/color/roles
- Quote: "Pair and layer color roles as intended to ensure expected visual results and accessibility."
- Quote: "For example, on primary is used for text and icons against the primary fill color."
- Confirmed: 2026-10-07 (browser)

### M3-MOTION
- URL: https://m3.material.io/styles/motion/overview/how-it-works
- Quote: "The physics system has two preset motion schemes: expressive and standard."
- Quote: "The physics system is replacing the previous system based on easing and duration."
- Confirmed: 2026-10-07 (browser)

## Android developer documentation

### AND-WSC
- URL: https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes
- Quote: "Window size classes are a set of opinionated viewport breakpoints that help you design, develop, and test responsive/adaptive layouts."
- Quote: "To support large and extra-large breakpoints, add the supportLargeAndXLargeWidth parameter set to true to the function call."
- Confirmed: 2026-10-07 (html)

### AND-16-LARGE
- URL: https://developer.android.com/about/versions/16/behavior-changes-16
- Quote: "For apps targeting Android 16 (API level 36), orientation, resizability, and aspect ratio restrictions no longer apply on displays with smallest width >= 600dp."
- Quote: "Additionally, onBackPressed is not called and KeyEvent.KEYCODE_BACK is not dispatched anymore."
- Confirmed: 2026-10-07 (html)

### AND-A11Y
- URL: https://developer.android.com/guide/topics/ui/accessibility/apps
- Quote: "For touch interfaces, we recommend that each interactive UI element have a focusable area, or touch target size, of at least 48dpx48dp."
- Quote: "For each UI element in your app, include a description that describes the element's purpose."
- Confirmed: 2026-10-07 (html)

### AND-EDGE
- URL: https://developer.android.com/develop/ui/compose/system/insets
- Quote: "Edge-to-edge is enforced on Android 15 and higher once your app targets SDK 35."
- Confirmed: 2026-10-07 (html)

### AND-FONT-SCALE
- URL: https://developer.android.com/about/versions/14/features#non-linear-font-scaling
- Quote: "Starting in Android 14, the system supports font scaling up to 200%, providing users with additional accessibility options."
- Quote: "Remember to always specify text sizes in sp units."
- Confirmed: 2026-10-07 (html)

### AND-ADAPTIVE-ICON
- URL: https://developer.android.com/develop/ui/views/launch/icon_design_adaptive
- Quote: "The 66x66 safe zone depicted is the area that is never clipped by a shaped mask defined by an OEM."
- Quote: "Starting with Android 16 QPR 2, Android automatically themes app icons for apps that don't provide their own."
- Confirmed: 2026-10-07 (html)

### AND-ANIM-SCALE
- URL: https://developer.android.com/reference/android/animation/ValueAnimator#areAnimatorsEnabled()
- Quote: "Returns whether animators are currently enabled, system-wide. By default, all animators are enabled."
- Quote: "This can change if either the user sets a Developer Option to set the animator duration scale to 0 or by Battery Savery mode being enabled (which disables all animations)."
- Confirmed: 2026-10-07 (html)

## WCAG 2.2

### WCAG-1.3.1
- URL: https://www.w3.org/TR/WCAG22/#info-and-relationships
- Quote: "Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text."
- Confirmed: 2026-10-07 (html)

### WCAG-1.4.3
- URL: https://www.w3.org/TR/WCAG22/#contrast-minimum
- Quote: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1, except for the following:"
- Quote: "Large-scale text and images of large-scale text have a contrast ratio of at least 3:1;"
- Confirmed: 2026-10-07 (html)

### WCAG-1.4.4
- URL: https://www.w3.org/TR/WCAG22/#resize-text
- Quote: "Except for captions and images of text, text can be resized without assistive technology up to 200 percent without loss of content or functionality."
- Confirmed: 2026-10-07 (html)

### WCAG-1.4.8
- URL: https://www.w3.org/TR/WCAG22/#visual-presentation
- Quote: "Width is no more than 80 characters or glyphs (40 if CJK)."
- Confirmed: 2026-10-07 (html)

### WCAG-1.4.11
- URL: https://www.w3.org/TR/WCAG22/#non-text-contrast
- Quote: "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s):"
- Confirmed: 2026-10-07 (html)

### WCAG-1.4.12
- URL: https://www.w3.org/TR/WCAG22/#text-spacing
- Quote: "no loss of content or functionality occurs by setting all of the following and by changing no other style property:"
- Quote: "Line height (line spacing) to at least 1.5 times the font size;"
- Confirmed: 2026-10-07 (html)

### WCAG-2.3.3
- URL: https://www.w3.org/TR/WCAG22/#animation-from-interactions
- Quote: "Motion animation triggered by interaction can be disabled, unless the animation is essential to the functionality or the information being conveyed."
- Confirmed: 2026-10-07 (html)

### WCAG-2.5.5
- URL: https://www.w3.org/TR/WCAG22/#target-size-enhanced
- Quote: "The size of the target for pointer inputs is at least 44 by 44 CSS pixels except when:"
- Confirmed: 2026-10-07 (html)

### WCAG-2.5.8
- URL: https://www.w3.org/TR/WCAG22/#target-size-minimum
- Quote: "The size of the target for pointer inputs is at least 24 by 24 CSS pixels, except when:"
- Confirmed: 2026-10-07 (html)

### WCAG-4.1.2
- URL: https://www.w3.org/TR/WCAG22/#name-role-value
- Quote: "For all user interface components (including but not limited to: form elements, links and components generated by scripts), the name and role can be programmatically determined;"
- Confirmed: 2026-10-07 (html)

## MDN

### MDN-LANDMARKS
- URL: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements#content_sectioning
- Quote: "Content sectioning elements allow you to organize the document content into logical pieces."
- Confirmed: 2026-10-07 (html)

### MDN-REDUCED-MOTION
- URL: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion
- Quote: "The prefers-reduced-motion CSS media feature is used to detect if a user has enabled a setting on their device to minimize the amount of non-essential motion."
- Confirmed: 2026-10-07 (html)

### MDN-CLAMP
- URL: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/clamp
- Quote: "When clamp() is used for controlling text size, make sure that the maximum allowed value is a relative length unit that is no less than twice the minimum allowed value"
- Confirmed: 2026-10-07 (html)

### MDN-CONTAINER
- URL: https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries
- Quote: "Container queries enable you to apply styles to an element based on certain attributes of its container:"
- Confirmed: 2026-10-07 (html)

### MDN-APP-ICONS
- URL: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/How_to/Define_app_icons
- Quote: "The safe zone is the area that's guaranteed to always be visible when the mask is applied and is defined as a circle which diameter is 80% of the icon's minimum dimension."
- Confirmed: 2026-10-07 (html)

### MDN-CUSTOM-PROPS
- URL: https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties
- Quote: "Custom properties (sometimes referred to as CSS variables or cascading variables) are entities defined by CSS authors that represent specific values to be reused throughout a document."
- Confirmed: 2026-10-07 (html)

## Tier 2 origins

### Anthropic-FD
- URL: https://claude.com/blog/improving-frontend-design-through-skills
- Quote: "Claude has strong design understanding, but distributional convergence obscures it without guidance."
- Confirmed: 2026-10-07 (html)

### Hurff
- URL: https://www.scotthurff.com/posts/why-your-user-interface-is-awkward-youre-ignoring-the-ui-stack/
- Quote: "That's because following the rules of the UI Stack and the five states helps you create a cohesive interface that’s forgiving, helpful, and human."
- Confirmed: 2026-10-07 (html)

### Butterick
- URL: https://practicaltypography.com/line-length.html
- Quote: "Aim for an average line length of 45–90 characters, including spaces."
- Confirmed: 2026-10-07 (html)

### Bringhurst
- URL: https://en.wikipedia.org/wiki/The_Elements_of_Typographic_Style
- Quote: none (book)

### Google-DM
- URL: https://github.com/google-labs-code/design.md
- Quote: "A DESIGN.md file combines machine-readable design tokens (YAML front matter) with human-readable design rationale (markdown prose)."
- Confirmed: 2026-10-07 (html)

### Vercel-DM
- URL: https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md
- Quote: "Judgment changes go into design.md as prose, reusable mechanics go into the stylesheet, and anything that we can check mechanically becomes a deterministic check in code."
- Confirmed: 2026-10-07 (html)

### Tuch-2012
- URL: https://research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/
- Quote: "Overall, websites with low VC and high PT were perceived as highly appealing."
- Confirmed: 2026-10-07 (html)

### EM-FAVICON
- URL: https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs
- Quote: "How to Favicon in 2026: Three files that fit most needs"
- Confirmed: 2026-10-07 (html)

### House
- URL: https://github.com/Mark-Hine/ai-toolkit/blob/main/claude/plugins/design-kit/skills/standards/references/rationale.md
- Quote: none (house)
