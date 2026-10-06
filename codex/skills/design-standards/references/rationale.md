---
verified: 2026-09-29
sources: house
---

# Design standards rationale

One section per Tier 2 rule ID in `design-standards.md`. Each gives the origin, what it says, and why the house keeps or narrows it. Tier 1 rules need no rationale because their source is the rule.

## DIR-1, DIR-2, TYP-2 (Anthropic-FD)

Anthropic's post on improving frontend design says an unguided model "will almost always conform to Inter fonts, purple gradients on white backgrounds, and minimal animations", and calls this distributional convergence. That is the evidence for DIR-1 and DIR-2. The post also tells web frontends never to use Inter, Roboto, Open Sans, Lato or default system fonts. Native apps are asked by HIG and Material 3 to use the system type scale, so TYP-2 narrows the font advice to display faces chosen for a brand and shipped through the design system. The system face with defined roles is a deliberate choice, not a default.

## DIR-3 (House)

The same post recommends layered gradients that match the overall aesthetic, so a blanket gradient ban would contradict its own source. The house bans only unmotivated gradients. JetSnack, the Android design-system blueprint this toolkit endorses, uses gradients as brand surfaces and buttons built once in its theme. It passes DIR-3.

## DIR-4, DIR-5 (House)

The 2026-09-29 audit found no external source for glow borders, pill badges or nested cards. They stay because they are the visible symptoms of the convergence DIR-2 describes, and they grade Nit by default.

## DIR-6 (Tuch-2012)

Tuch and others showed people websites for 50 ms. Pages with low visual complexity and high prototypicality were rated the most appealing, where prototypicality means the page looks like what people expect of its kind. Anthropic's post shows that model output converges in the identity layer, through default fonts, palettes and motion. So distinctiveness belongs in type, colour, imagery, iconography and voice, while navigation, layout and controls stay familiar.

## Contract precedence and regressions (House)

The design contract is the project's own decision record, so it outranks house taste and any skill's general advice. Anthropic's frontend-design skill tells an agent to create a compact token system and take aesthetic risk. In a project that already has a system, that advice is how continuity breaks. So the skill's advice applies only where the contract leaves a choice open. The contract never outranks a T1 rule, because a brand choice cannot waive contrast or target size.

An unrequested change to a shared token, component or brand asset alters screens outside the task. It grades Major as a regression whatever the tier of the rule it touches, the way the correctness clause treats a crash.

## SYS-1 to SYS-3 (Google-DM, Vercel-DM, House)

Google's DESIGN.md is an open format with YAML tokens, eight ordered prose sections and a CLI that lints, diffs and exports it. Unknown sections are preserved, so a project can add Brand marks and Decisions sections. The format gives no workflow for keeping the file and the code in sync, which is what SYS-2 adds.

Vercel generated pages with and without a design.md, a bounded stylesheet and deterministic checks, and counted 39 known failures against 91. The sample was three desktop scenarios, and the checks catch only failures someone has written down. The house treats the result as evidence for the contract and for SYS-3, not as a measure of taste. Vercel's advice to encode each correction in the layer that enforces it is SYS-3.

The use, extend and change classes and the approval board are house decisions. They exist because an agent that edits a shared token to finish one screen silently changes every other screen that uses it.

## SPC-3, SPC-4, SPC-5 (House)

Material 3 defines an 8 dp scale. HIG defines no grid at all. A 4 or 8 unit token scale on iOS and the web matches the Android scale, so one design file can serve every platform. SPC-4's proximity bands are a house convention. SPC-5 exists because a literal such as 11 or 23 is where accidental spacing shows up.

## TYP-3 (Bringhurst, Butterick, WCAG-1.4.8)

Bringhurst gives 45 to 75 characters as the classic range. Butterick gives 45 to 90 including spaces. WCAG 1.4.8 caps lines at 80 characters at level AAA. The rule is Tier 2 because AAA is not a conformance target here and because native layouts on phones rarely reach these widths.

## STA-1 to STA-7 (Hurff and House)

Hurff's UI Stack, from 2015, lists five states: Ideal, Empty, Error, Partial and Loading. His Partial means a screen with sparse content, such as one item in a list. The house renames Ideal to loaded and narrows Partial to cached or offline data, because no repo state model has a sparse case and cached data is where users get misled. Every repo state model already has loading, loaded, empty or error, so the canonical `HomeContent` samples in the Android and iOS references pass STA-1. The old "5-State Completeness Law" with a mandatory Degraded state was retired on 2026-09-29 because it contradicted those models.

STA-3's skeleton loaders are house preference. Neither HIG nor Material 3 requires them. HIG's loading guidance asks for placeholders and for loading to finish before people notice.

## A11Y-6 (WCAG-2.5.5)

WCAG 2.5.5 is level AAA. The AA floor is 24 by 24 CSS px in 2.5.8, which is A11Y-5. Touch layouts aim for the AAA size because the AA floor is small under a finger.

## WEB-6 (EM-FAVICON, House)

MDN names no required icon sizes and defers to each platform. The Evil Martians guide, updated in January 2026, recommends three browser files. They are a 32 px ICO, an SVG with a dark mode media query and a 180 px Apple touch icon. A web app manifest adds 192, 512 and maskable 512 px icons. The house adds the single master SVG so every size stays the same mark.

## WEB-3, WEB-4 (House)

MDN documents custom properties and container queries as mechanisms, not mandates. The house prefers them because tokens as custom properties keep one source of truth and container queries let a component adapt without knowing the page. Media queries still own page-level layout, so "instead of breakpoints" would be too strong.
