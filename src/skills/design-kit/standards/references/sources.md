---
verified: 2026-09-29
sources: inline
---

# Design standards sources

Every source key used in `design-standards.md` and what it is authoritative for. The sentence each key rests on, and the date it was last confirmed on the live page, are in [`source-anchors.md`](source-anchors.md). Grade from the rules and quote the anchor in a dispute. Do not fetch a page to grade a rule.

## Apple Human Interface Guidelines

Base URL `https://developer.apple.com/design/human-interface-guidelines/`. Pages render client-side. The JSON form `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json` returns the text.

| Key | Page | Authoritative for |
| --- | --- | --- |
| HIG-ACCESSIBILITY | `/accessibility` | 44 pt default control size, 28 pt minimum, contrast table, Reduce Motion, text enlargement to at least 200% |
| HIG-BUTTONS | `/buttons` | a hit region of at least 44 by 44 pt |
| HIG-MATERIALS | `/materials` | do not use Liquid Glass in the content layer, standard materials for content |
| HIG-TYPOGRAPHY | `/typography` | built-in text styles, the size and leading table |
| HIG-HAPTICS | `/playing-haptics` | use haptics consistently and sparingly |
| HIG-APP-ICONS | `/app-icons` | 1024 by 1024 px layers in Icon Composer, the default, dark, clear and tinted appearances, effects the system adds, text only when essential |
| HIG-LAYOUT | `/layout` | safe areas, layout margins, no spacing grid |
| HIG-COLOR | `/color` | semantic colours, dark and increased-contrast variants |

## Material 3

Base URL `https://m3.material.io/`. Pages render client-side and return only a title to a plain fetch. A search snippet or a browser read is needed for the text.

| Key | Page | Authoritative for |
| --- | --- | --- |
| M3-SPACING | `/styles/spacing/overview` | "Spacing units follow an 8dp scale" |
| M3-TYPE | `/styles/typography/type-scale-tokens` | the type roles, cross-checked against the Compose Material 3 typography page |
| M3-COLOR | `/styles/color/roles` | colour roles |
| M3-MOTION | `/styles/motion/overview/how-it-works` | motion schemes, spatial and effects springs |

## Android developer documentation

Base URL `https://developer.android.com/`.

| Key | Page | Authoritative for |
| --- | --- | --- |
| AND-WSC | `/develop/ui/compose/layouts/adaptive/use-window-size-classes` | five width classes and `supportLargeAndXLargeWidth` |
| AND-16-LARGE | `/about/versions/16/behavior-changes-16` | orientation and resizability locks ignored at sw600dp for target 36, opt-out ends at 37, predictive back default |
| AND-A11Y | `/guide/topics/ui/accessibility/apps` | 48 dp targets, labels |
| AND-EDGE | `/develop/ui/compose/system/insets` | edge to edge and insets |
| AND-FONT-SCALE | `/about/versions/14/features#non-linear-font-scaling` | font scaling to 200% |
| AND-ADAPTIVE-ICON | `/develop/ui/views/launch/icon_design_adaptive` | 108 by 108 dp layers, a logo of 48 to 66 dp inside the masked viewport, the monochrome layer for themed icons, automatic theming from Android 16 QPR 2 |
| AND-ANIM-SCALE | `/reference/android/animation/ValueAnimator#areAnimatorsEnabled()` | the system-wide animator switch that the Remove animations setting turns off |

## WCAG 2.2

W3C Recommendation, current edition dated 2024-12-12. One key per success criterion.

| Key | URL |
| --- | --- |
| WCAG-1.3.1 | https://www.w3.org/TR/WCAG22/#info-and-relationships |
| WCAG-1.4.3 | https://www.w3.org/TR/WCAG22/#contrast-minimum |
| WCAG-1.4.4 | https://www.w3.org/TR/WCAG22/#resize-text |
| WCAG-1.4.8 | https://www.w3.org/TR/WCAG22/#visual-presentation |
| WCAG-1.4.11 | https://www.w3.org/TR/WCAG22/#non-text-contrast |
| WCAG-1.4.12 | https://www.w3.org/TR/WCAG22/#text-spacing |
| WCAG-2.3.3 | https://www.w3.org/TR/WCAG22/#animation-from-interactions |
| WCAG-2.5.5 | https://www.w3.org/TR/WCAG22/#target-size-enhanced |
| WCAG-2.5.8 | https://www.w3.org/TR/WCAG22/#target-size-minimum |
| WCAG-4.1.2 | https://www.w3.org/TR/WCAG22/#name-role-value |

## MDN and web.dev

| Key | URL |
| --- | --- |
| MDN-LANDMARKS | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements#content_sectioning |
| MDN-REDUCED-MOTION | https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion |
| MDN-CLAMP | https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/clamp |
| MDN-CONTAINER | https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries |
| MDN-APP-ICONS | https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/How_to/Define_app_icons |
| MDN-CUSTOM-PROPS | https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties |

## Tier 2 origins

| Key | Source |
| --- | --- |
| Anthropic-FD | https://claude.com/blog/improving-frontend-design-through-skills (2025-11-12), on distributional convergence in model-generated frontends |
| Hurff | https://www.scotthurff.com/posts/why-your-user-interface-is-awkward-youre-ignoring-the-ui-stack/ (2015-08-17), the UI Stack |
| Butterick | https://practicaltypography.com/line-length.html |
| Bringhurst | The Elements of Typographic Style, a book with no URL |
| Google-DM | https://github.com/google-labs-code/design.md, the DESIGN.md format (alpha) and its `@google/design.md` CLI, read through `design.md spec` at version 0.4.0 |
| Vercel-DM | https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md (2026-08-31), design.md guidance plus a bounded stylesheet plus deterministic checks, 39 against 91 known failures |
| Tuch-2012 | https://research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/, Tuch and others in the International Journal of Human-Computer Studies 70(11), DOI 10.1016/j.ijhcs.2012.06.003 |
| EM-FAVICON | https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs, now titled "How to Favicon in 2026: Three files that fit most needs" and updated 2026-01-21 |
| House | An ai-toolkit decision. The reason is in `rationale.md` |
