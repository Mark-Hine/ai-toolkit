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

## Second opinion

A model from a different family screens the board before the user picks, because a model grading its own family's work favours it. The second opinion finds defects and describes strengths. The user still decides.

**Which CLI.** Use the first CLI on the "Second-opinion CLIs" line of the agent's `machine.md` that runs a different model family from the agent using this skill. Claude Code asks Gemini or a GPT model, Codex asks Gemini or Claude, and Antigravity asks Claude or a GPT model. Always name the model, because some CLIs offer several families. When no CLI is listed or it fails to sign in, skip the step and report "Second opinion: Unverified" with the reason.

**Consent.** The board images leave the machine for another vendor. Ask the user before the first send in each session, and skip without asking when the project instructions forbid external review, as work on unreleased designs may.

**Command.** Run it from the iteration folder, read-only and with a time limit. Never pass a flag that skips permissions or allows writes.

| CLI | Read-only call |
| --- | --- |
| Antigravity CLI | `agy -p "<prompt>" --mode plan --sandbox --model gemini-3.1-pro-high --output-format json --json-schema second-opinion.schema.json --print-timeout 300s` |
| Claude Code | `claude -p "<prompt>" --permission-mode plan --allowedTools Read --model opus --output-format json --json-schema "$(cat second-opinion.schema.json)"` |
| Codex | `codex exec --sandbox read-only -m <gpt model> --image board.png --output-schema second-opinion.schema.json "<prompt>"` |

Model names change. Take the current one from the CLI's own model list.

**Prompt.** Send the brief, the checks that apply and the image paths, and leave out the code and `DESIGN.md`. A prompt for a brand mark board reads like this:

```text
You are giving a second opinion on logo options. The user will choose, so describe and do not decide for them.
Brief: <job, audience, traits, what is fixed>.
Open board.png in this folder. It shows the current mark and options A, B and C at several sizes, on light, dark,
brand and photo grounds, in one colour and blurred, and in a header and a tab.
For each option, list defects with the image, the region and the check that fails (distinctive, works small,
one colour, visible on every ground, simple, platform safe), then its strengths and its fit to the brief.
Last, name the option you would pick and why. Do not edit any file.
```

For screens, replace the checks with the screening checklist above. Write the schema beside the board as `second-opinion.schema.json`:

```json
{
  "type": "object",
  "properties": {
    "options": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "label": { "type": "string" },
          "defects": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "image": { "type": "string" },
                "region": { "type": "string" },
                "check": { "type": "string" },
                "finding": { "type": "string" }
              },
              "required": ["image", "region", "check", "finding"]
            }
          },
          "strengths": { "type": "array", "items": { "type": "string" } },
          "fit": { "type": "string" }
        },
        "required": ["label", "defects", "strengths", "fit"]
      }
    },
    "preference": {
      "type": "object",
      "properties": { "label": { "type": "string" }, "reason": { "type": "string" } },
      "required": ["label", "reason"]
    }
  },
  "required": ["options", "preference"]
}
```

**Use.** Save the reply as `second-opinion.md` beside the board, naming the CLI and model.

- Before the pick, check each defect against the image yourself. Fix or drop an option whose defect you confirm, and say which.
- Keep its preference in the closed notes until the user picks, so the pick stays blind.
- When its preference differs from the user's pick for a reason the user has not weighed, say so once and ask whether to switch.

**Failure.** A timeout, an error, a failed sign-in or a reply that does not match the schema skips the step. Report "Second opinion: Unverified" with the reason and carry on. The second opinion never blocks the loop.

## What not to trust

- **A model's score as the decision.** Models rate their own output higher than people do (Panickssery and others, 2024), so the user decides.
- **One model family judging its own work.** A second opinion comes from a different family.
- **Trend lists and install counts as evidence of quality.**

## Preference test

For a brand mark, the user can show the shortlist to 5 to 10 people from the audience, without labels or the agent's preference. Record the votes and the reasons in the Decisions entry.
