---
verified: 2026-09-29
sources: inline
---

# Design standards sources

Every source key used in `design-standards.md`, what it is authoritative for, and when it was last read. A row marked "to fetch" was cited from a search snippet or an earlier read and needs a full re-read before its rule is graded above Nit in a dispute.

## Apple Human Interface Guidelines

Base URL `https://developer.apple.com/design/human-interface-guidelines/`. Pages render client-side. The JSON form `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json` returns the text.

| Key | Page | Authoritative for | Verified |
| --- | --- | --- | --- |
| HIG-ACCESSIBILITY | `/accessibility` | 44 pt default control size, 28 pt minimum, contrast table, Reduce Motion, text enlargement to at least 200% | 2026-09-29 |
| HIG-BUTTONS | `/buttons` | a hit region of at least 44 by 44 pt | 2026-09-29 |
| HIG-MATERIALS | `/materials` | do not use Liquid Glass in the content layer, standard materials for content | 2026-09-29 |
| HIG-TYPOGRAPHY | `/typography` | built-in text styles, the size and leading table | 2026-09-29 |
| HIG-HAPTICS | `/playing-haptics` | use haptics consistently and sparingly | 2026-09-29 |
| HIG-APP-ICONS | `/app-icons` | 1024 by 1024 px layers in Icon Composer, the default, dark, clear and tinted appearances, effects the system adds, text only when essential | 2026-10-06 |
| HIG-LAYOUT | `/layout` | safe areas, layout margins, no spacing grid | 2026-10-06 |
| HIG-COLOR | `/color` | semantic colours, dark and increased-contrast variants | 2026-10-06 |

## Material 3

Base URL `https://m3.material.io/`. Pages render client-side and return only a title to a plain fetch. A search snippet or a browser read is needed for the text.

| Key | Page | Authoritative for | Verified |
| --- | --- | --- | --- |
| M3-SPACING | `/foundations/layout/grids-spacing/spacing` | "Spacing units follow an 8dp scale", icons align to a 4dp grid, type to a 4dp baseline | 2026-09-29, snippet |
| M3-TYPE | `/styles/typography/type-scale-tokens` | the type roles, cross-checked against the Compose Material 3 typography page | 2026-09-29 |
| M3-COLOR | `/styles/color/roles` | colour roles | 2026-10-06, through the Compose Material 3 page |
| M3-MOTION | `/styles/motion/overview/how-it-works` | motion schemes, spatial and effects springs | to fetch |

## Android developer documentation

Base URL `https://developer.android.com/`.

| Key | Page | Authoritative for | Verified |
| --- | --- | --- | --- |
| AND-WSC | `/develop/ui/compose/layouts/adaptive/use-window-size-classes` | five width classes and `supportLargeAndXLargeWidth` | 2026-09-29 |
| AND-16-LARGE | `/about/versions/16/behavior-changes-16` | orientation and resizability locks ignored at sw600dp for target 36, opt-out ends at 37, predictive back default | 2026-09-29 |
| AND-A11Y | `/guide/topics/ui/accessibility/apps` | 48 dp targets, labels | 2026-10-06 |
| AND-EDGE | `/develop/ui/compose/system/insets` | edge to edge and insets | 2026-10-06 |
| AND-FONT-SCALE | `/about/versions/14/features#non-linear-font-scaling` | font scaling to 200% | 2026-10-06 |
| AND-ADAPTIVE-ICON | `/develop/ui/views/launch/icon_design_adaptive` | 108 by 108 dp layers, a logo of 48 to 66 dp inside the masked viewport, the monochrome layer for themed icons, automatic theming from Android 16 QPR 2 | 2026-10-06 |
| AND-ANIM-SCALE | `/reference/android/provider/Settings.Global#ANIMATOR_DURATION_SCALE` | the Remove animations scale | to fetch |

## WCAG 2.2

W3C Recommendation, current edition dated 2024-12-12. Verified 2026-09-29. One key per success criterion.

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

| Key | URL | Verified |
| --- | --- | --- |
| MDN-LANDMARKS | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements#content_sectioning | to fetch |
| MDN-REDUCED-MOTION | https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion | to fetch |
| MDN-CLAMP | https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/clamp | 2026-09-29 |
| MDN-CONTAINER | https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries | to fetch |
| MDN-APP-ICONS | https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/How_to/Define_app_icons | 2026-10-06 |
| MDN-CUSTOM-PROPS | https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties | to fetch |

## Tier 2 origins

| Key | Source | Verified |
| --- | --- | --- |
| Anthropic-FD | https://claude.com/blog/improving-frontend-design-through-skills (2025-11-12), on distributional convergence in model-generated frontends | 2026-09-29 |
| Hurff | https://www.scotthurff.com/posts/why-your-user-interface-is-awkward-youre-ignoring-the-ui-stack/ (2015-08-17), the UI Stack | 2026-09-29 |
| Butterick | https://practicaltypography.com/line-length.html | 2026-09-29 |
| Bringhurst | The Elements of Typographic Style, a book with no URL | n/a |
| Google-DM | https://github.com/google-labs-code/design.md, the DESIGN.md format (alpha) and its `@google/design.md` CLI, read through `design.md spec` at version 0.4.0 | 2026-10-06 |
| Vercel-DM | https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md (2026-08-31), design.md guidance plus a bounded stylesheet plus deterministic checks, 39 against 91 known failures | 2026-10-06 |
| Tuch-2012 | https://research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/, Tuch and others in the International Journal of Human-Computer Studies 70(11), DOI 10.1016/j.ijhcs.2012.06.003 | 2026-10-06, abstract |
| EM-FAVICON | https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs, now titled "How to Favicon in 2026: Three files that fit most needs" and updated 2026-01-21 | 2026-10-06 |
| House | An ai-toolkit decision. The reason is in `rationale.md` | n/a |
