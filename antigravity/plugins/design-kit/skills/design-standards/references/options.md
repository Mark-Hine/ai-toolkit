---
verified: 2026-10-06
sources:
  - https://www.nngroup.com/articles/principles-visual-design/
  - https://www.nngroup.com/articles/ten-usability-heuristics/
  - https://arxiv.org/abs/2404.13076
  - https://research.google/pubs/the-role-of-visual-complexity-and-prototypicality-regarding-first-impression-of-websites-working-towards-understanding-aesthetic-judgments/
  - https://github.com/anthropics/skills/tree/main/skills/frontend-design
  - https://www.awwwards.com/terms/
  - https://www.awwwards.com/about-evaluation/
  - https://dribbble.com/terms
  - https://www.adobe.com/legal/terms.html
  - https://www.logolounge.com/trend/2026-logo-trend-report
  - https://www.underconsideration.com/brandnew/
---

# Options

How to brief, research, diverge, screen and present design options, so the user picks from real alternatives instead of approving the first idea (DIR-1, DIR-6, SYS-2).

## Brief

Write the brief before any option, and show it on the board.

- **Job.** What the screen or mark must do, in one sentence.
- **Audience.** Who uses it, and where and when.
- **Traits.** Three words the result must signal, such as calm, exact and warm.
- **Fixed.** Tokens, components and decisions from `DESIGN.md` that stay as they are.
- **Accepted when.** What the user will check before saying yes.

## Anchors

Each option starts from a different exemplar, so the options diverge instead of repeating one idea three times. Take anchors from these sources, in order:

1. The References section of `DESIGN.md`, which holds the anchors the user already chose.
2. Links and screenshots the user supplies.
3. Work the design community has already graded. Awwwards scores each site through a jury of at least 18 designers, weighted 40% design, 30% usability, 20% creativity and 10% content, plus votes from validated professional users. Brand New reviews identity work. The LogoLounge trend report covers current logo trends. Read their public pages for principles only.
4. The platform owner's own apps and design galleries for native work.

Respect each source's terms. Awwwards forbids reproducing its content. Dribbble's terms and Adobe's terms for Behance forbid scraping. Mobbin refuses automated reads. Use screenshots the user takes from these sites instead of fetching them, and never copy an exemplar's assets, layout or mark.

Record each anchor in one line: the link, what it does well, the principle borrowed, and what to avoid. When a research subagent gathers anchors, pin it to a research model (`sonnet` in Claude Code) and give it these source rules.

## Divergence

- Make three options for a screen, and three to five concepts for a brand mark.
- Make each option differ from the others on at least two of type, colour, layout, density and shape.
- Spend the distinctiveness on identity and keep structure conventional for the platform (DIR-6). People rate simple, familiar layouts as the most appealing, so a novel navigation pattern costs more than it earns.
- Give each option a one-sentence concept tied to the brief, and its token changes or the words "within the contract" when nothing changes.
- When two options converge on the same idea, replace one of them.

## Screening checklist

Apply the checklist to the before images and to each rendered option. It finds defects. It does not choose between sound options. Cite an image and a region in every finding, such as "A-home-desktop-light.png, hero headline".

| Check | Passes when | Source |
| --- | --- | --- |
| Hierarchy | Each view has one focal point, and the reading order matches the brief's priority | NN/g visual design principles |
| Scale | The view uses no more than three distinct sizes, and the most important element is the largest | NN/g visual design principles |
| Grouping | Related items sit closer than unrelated ones, on the spacing scale | Gestalt proximity, SPC-4 |
| Type | At most two families, sizes from the scale, body lines of 45 to 75 characters | TYP-1, TYP-3 |
| Colour | Each colour keeps the role `DESIGN.md` gives it, and the accent stays rare | the contract, AND-1, IOS-1 |
| Contract | No value or component outside `DESIGN.md` unless the change class allows it | SYS-2 |
| Defaults | None of the looks models default to, unless the brief or the contract asks for one | DIR-2, DIR-4, Anthropic frontend-design |
| States | Loading, empty and error states exist where data drives the screen | STA-1 |
| Consistency | Same words, icons and controls mean the same thing across screens | Nielsen heuristic 4 |
| Craft | Alignment holds, nothing clips, and contrast and targets meet A11Y-1 to A11Y-5 | A11Y rules |
| Identity | The product would not be mistaken for a competitor or a template | DIR-6 |

The default looks to screen for, from Anthropic's frontend-design skill and DIR-2 and DIR-4:
- Purple or blue gradients on white, and one sans face for everything.
- A warm cream background with a high-contrast serif and a terracotta accent.
- A near-black background with one acid-green or vermilion accent.
- Content cut into identical rounded cards with the same soft shadow.
- A tracked-out capital label over every heading, a single accented word in a headline, numbered markers on content that is not a sequence, and an arrow on every link.

## Board

Build the board as `capture.md` describes, then follow these rules:

- Put options in random order, labelled A, B and C. Show no ranking, scores or notes until the user picks.
- Ask the user to pick, combine or reject. A rejection with a reason starts a new round from the brief.
- After the pick, open the notes: the screening findings, and what each option would change in `DESIGN.md`.
- For a change to a shared token, component or brand asset, the board shows before and after for every affected screen, and the user's approval is required before the change lands (SYS-2).

## What not to trust

- **A model's score as the decision.** Models rate their own output higher than people do (Panickssery and others, 2024), so the user decides.
- **One model family judging its own work.** A second opinion comes from a different family.
- **Trend lists and install counts as evidence of quality.**

## Preference test

For a brand mark, the user can show the shortlist to 5 to 10 people from the audience, without labels or the agent's preference. Record the votes and the reasons in the Decisions entry.
