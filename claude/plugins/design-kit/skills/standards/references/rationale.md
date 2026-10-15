---
verified: 2026-09-29
sources: house
---

# Design standards rationale

One section per Tier 2 rule ID in `design-standards.md`. Each gives the origin, what it says, and why the house keeps or narrows it. Tier 1 rules need no rationale because their source is the rule.

## DIR-1, DIR-2, TYP-2 (Anthropic-FD)

Anthropic's post on improving frontend design says an unguided model "will almost always conform to Inter fonts, purple gradients on white backgrounds, and minimal animations", and calls this distributional convergence. That is the evidence for DIR-1 and DIR-2. The post also tells web frontends never to use Inter, Roboto, Open Sans, Lato or default system fonts. Native apps are asked by HIG and Material 3 to use the system type scale, so TYP-2 narrows the font advice to display faces chosen for a brand and shipped through the design system. The system face with defined roles is a deliberate choice, not a default.

The frontend-design skill that grew out of the post (Anthropic-FDS, re-read on 2026-10-15) dropped the font ban for an instruction to choose typefaces deliberately. It lists the looks models now default to, such as warm cream with a serif and a terracotta accent, near-black with one acid accent, broadsheet hairlines and the identical-card kit. DIR-2 carries that list. The skill says each look is legitimate for some briefs, so DIR-2 yields when the brief or the contract asks for one.

## DIR-3 (House)

The same post recommends layered gradients that match the overall aesthetic, so a blanket gradient ban would contradict its own source. The house bans only unmotivated gradients. JetSnack, the Android design-system blueprint this toolkit endorses, uses gradients as brand surfaces and buttons built once in its theme. It passes DIR-3.

## DIR-4, DIR-5 (House, Anthropic-FDS)

The 2026-09-29 audit found no external source for glow borders, pill badges or nested cards. They stay because they are the visible symptoms of the convergence DIR-2 describes, and they grade Nit by default. Anthropic's frontend-design skill now gives DIR-4 its principle. It says "Visual structure is information", and that numbered markers fit only content that is a sequence. Its list of template chrome supplies DIR-4's examples.

## DIR-6 (Tuch-2012)

Tuch and others showed people websites for 50 ms. Pages with low visual complexity and high prototypicality were rated the most appealing, where prototypicality means the page looks like what people expect of its kind. Anthropic's post shows that model output converges in the identity layer, through default fonts, palettes and motion. So distinctiveness belongs in type, colour, imagery, iconography and voice, while navigation, layout and controls stay familiar.

## DIR-7 (HIG-MOTION, Anthropic-FDS)

HIG says "Don’t add motion for the sake of adding motion", asks apps to avoid custom motion on frequent interactions, and asks that people can cancel motion. Anthropic's frontend-design skill adds that a fade-in on every section and a hover effect on every card read as AI-generated, and that one orchestrated moment lands better than scattered effects. Motion that answers a person's action is welcome in both. The rule is Tier 2 because HIG words it as advice. A11Y-9 and AND-5 still govern reduced motion and the Material motion scheme.

## Contract precedence and regressions (House)

The design contract is the project's own decision record, so it outranks house taste and any skill's general advice. Anthropic's frontend-design skill tells an agent to create a compact token system and take aesthetic risk. In a project that already has a system, that advice is how continuity breaks. So the skill's advice applies only where the contract leaves a choice open. The contract never outranks a T1 rule, because a brand choice cannot waive contrast or target size.

An unrequested change to a shared token, component or brand asset alters screens outside the task. It grades Major as a regression whatever the tier of the rule it touches, the way the correctness clause treats a crash.

## SYS-1 to SYS-3 (Google-DM, Vercel-DM, House)

Google's DESIGN.md is an open format with YAML tokens, eight ordered prose sections and a CLI that lints, diffs and exports it. Unknown sections are preserved, so a project can add Brand marks and Decisions sections. The format gives no workflow for keeping the file and the code in sync, which is what SYS-2 adds. A project whose instructions already name a contract elsewhere, such as `docs/DESIGN.md`, keeps it there, because its instructions and history link to that path.

Vercel generated pages with and without a design.md, a bounded stylesheet and deterministic checks, and counted 39 known failures against 91. The sample was three desktop scenarios, and the checks catch only failures someone has written down. The house treats the result as evidence for the contract and for SYS-3, not as a measure of taste. Vercel's advice to encode each correction in the layer that enforces it is SYS-3.

The use, extend and change classes and the approval board are house decisions. They exist because an agent that edits a shared token to finish one screen silently changes every other screen that uses it.

## SPC-3, SPC-4, SPC-5 (House)

Material 3 defines an 8 dp scale. HIG defines no grid at all. A 4 or 8 unit token scale on iOS and the web matches the Android scale, so one design file can serve every platform. SPC-4's proximity bands are a house convention. SPC-5 exists because a literal such as 11 or 23 is where accidental spacing shows up.

## TYP-3 (Bringhurst, Butterick, WCAG-1.4.8)

Bringhurst gives 45 to 75 characters as the classic range. Butterick gives 45 to 90 including spaces. WCAG 1.4.8 caps lines at 80 characters at level AAA. The rule is Tier 2 because AAA is not a conformance target here and because native layouts on phones rarely reach these widths.

## STA-1 to STA-7 (Hurff and House)

Hurff's UI Stack, from 2015, lists five states: Ideal, Empty, Error, Partial and Loading. His Partial means a screen with sparse content, such as one item in a list. The house renames Ideal to loaded and narrows Partial to cached or offline data, because no repo state model has a sparse case and cached data is where users get misled. Every repo state model already has loading, loaded, empty or error, so the canonical `HomeContent` samples in the Android and iOS references pass STA-1. The old "5-State Completeness Law" with a mandatory Degraded state was retired on 2026-09-29 because it contradicted those models.

STA-3's skeleton loaders are house preference. Neither HIG nor Material 3 requires them. HIG's loading guidance asks for placeholders and for loading to finish before people notice.

## COPY-1 to COPY-4 (HIG-WRITING, M3-WRITING, Anthropic-FDS)

Interface copy had no rule, so native work got none of the writing guidance in Anthropic's frontend-design skill. HIG's Writing page asks for verbs on buttons and links, consistent labels through a flow, one capitalisation style for each element type, error messages placed near the problem that say how to fix it, and no "we". Material 3 asks for sentence case on all UI text, including buttons. The platforms differ on case, so COPY-3 follows each platform. The rules are Tier 2 because both sources phrase them as advice, and poor copy rarely blocks a task. They grade Nit unless a project opts in. The house writing style governs prose about the product, and these rules govern text inside it.

## A11Y-6 (WCAG-2.5.5)

WCAG 2.5.5 is level AAA. The AA floor is 24 by 24 CSS px in 2.5.8, which is A11Y-5. Touch layouts aim for the AAA size because the AA floor is small under a finger.

## WEB-6 (EM-FAVICON, House)

MDN names no required icon sizes and defers to each platform. The Evil Martians guide, updated in January 2026, recommends three browser files. They are a 32 px ICO, an SVG with a dark mode media query and a 180 px Apple touch icon. A web app manifest adds 192, 512 and maskable 512 px icons. The house adds the single master SVG so every size stays the same mark.

## WEB-3, WEB-4 (House)

MDN documents custom properties and container queries as mechanisms, not mandates. The house prefers them because tokens as custom properties keep one source of truth and container queries let a component adapt without knowing the page. Media queries still own page-level layout, so "instead of breakpoints" would be too strong.
