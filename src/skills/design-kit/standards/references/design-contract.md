---
verified: 2026-10-06
sources:
  - https://github.com/google-labs-code/design.md
  - https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md
  - https://code.claude.com/docs/en/memory
  - https://tailwindcss.com/docs/theme
  - https://github.com/schoero/eslint-plugin-better-tailwindcss
  - https://github.com/AndyOGo/stylelint-declaration-strict-value
  - https://stylelint.io/user-guide/rules/no-duplicate-selectors/
  - https://github.com/realm/SwiftLint
  - https://detekt.dev/docs/rules/style/
---

# Design contract

A project keeps its design system in a root `DESIGN.md` that every agent reads before UI work (SYS-1 to SYS-3). The format is Google's DESIGN.md, version alpha, checked with the `@google/design.md` CLI. This file covers what the format leaves open: drafting the file, keeping one source of values, loading it, recording changes and enforcing it with lint.

## An existing contract

When the project instructions already name a contract, such as `docs/DESIGN.md`, that file is the contract, whatever its format. Keep it where it is. Offer to add what it lacks, such as the YAML tokens or the Brand marks, References and Decisions sections, and add them only when the user agrees.

## Drafting the file

When a project has no `DESIGN.md`, draft one from the code before any design work.

1. Find the token sources. Look for CSS custom properties, a Tailwind `@theme` block or config, DTCG `*.tokens.json` files, the Compose theme (`Color.kt`, `Theme.kt`, `Type.kt`, `Shape.kt` and any spacing object) and SwiftUI colour assets and theme files.
2. Find the components the product reuses, such as buttons, inputs, cards and navigation, and the brand assets: logo files, favicons and app icons.
3. Fill the template from what the code does today, not from what it should do. List values that disagree, such as 14 greys or off-scale spacing, as open questions instead of choosing for the user.
4. Run `npx @google/design.md lint DESIGN.md` when Node is available, and fix every error.
5. Show the draft and its open questions to the user. Change nothing else until they confirm it.
6. Offer the pointer line for the project instructions file.

## Template

The YAML holds the values and the sections hold the reasons. Brand marks, Motion, References and Decisions are extra sections, which the format preserves. Keep the whole file to about 150 lines, because the pointer line loads it into every session.

```markdown
---
version: alpha
name: <Product>
description: <who it is for, in one sentence>
colors:
  primary: "#..."
  on-primary: "#..."
  surface: "#..."
  on-surface: "#..."
typography:
  body:
    fontFamily: <family>
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.6
rounded:
  md: 8px
spacing:
  "4": 1rem
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
---

# <Product>

## Overview
Audience, purpose, tone and density (DIR-1). Name the source of values.

## Colors
The role of each colour, and where it is never used.

## Typography
Faces, roles and the scale.

## Layout
Grid, content widths and the spacing scale.

## Elevation & Depth
Shadows, or how the flat design shows hierarchy.

## Shapes
Which radius each kind of element uses.

## Components
The components the product reuses and their variants.

## Do's and Don'ts
Rules written as checks someone can observe, including corrections the user has given.

## Brand marks
Master file, clear space, minimum size, colour versions and misuses.

## Motion
Durations and easing, or the platform motion scheme.

## References
The exemplars chosen as taste anchors, each with a link and what it is for.

## Decisions
- YYYY-MM-DD: what changed, what was rejected and why.
```

The format's dimensions accept only px, em and rem. A native project lists the sections it cannot express under `omitted`, names its theme file as the reason, and keeps its colours in the YAML:

```yaml
omitted:
  - section: typography
    reason: The Material 3 type roles in ui/theme/Type.kt are the source.
  - section: spacing
    reason: The Spacing object in ui/theme/Spacing.kt is the source.
```

## One source of values

Every value lives in one place, and the Overview names it.

- **Code is the source.** Token files in the code hold the values and the YAML mirrors them. A change edits both in the same commit. This suits native apps and most existing web projects.
- **DESIGN.md is the source.** The YAML holds the values and the CLI generates the code tokens, for example `npx @google/design.md export --format css-tailwind DESIGN.md > src/styles/theme.css` for a Tailwind v4 `@theme` block. `css-vars` emits plain custom properties and `dtcg` feeds a token pipeline such as Style Dictionary. Mark the generated file as generated and never edit it by hand. This suits new web projects.

## Loading the contract

Reference the file from the project instructions so it loads before any UI work:

| Agent | Line in the project instructions |
| --- | --- |
| Claude Code | `@DESIGN.md` on its own line in `CLAUDE.md`. Claude Code loads the file at launch, and also expands `@DESIGN.md` inside an `AGENTS.md` it reads |
| Codex and Antigravity | "Read `DESIGN.md` before any UI change and follow SYS-1 to SYS-3." in `AGENTS.md` |

Add the T2 IDs the project opts in to, such as "This project opts in to SYS-1 and SYS-2.", so a breach grades Major instead of Nit.

## Recording a change

Classify each UI change before writing it (SYS-2):

| Class | Example | What it needs |
| --- | --- | --- |
| Use | Pad a card with an existing spacing token | Nothing beyond the change |
| Extend | Add a warning colour or a button size | The new token or component in `DESIGN.md` in the same change |
| Change | Make every button pill-shaped, or alter the primary colour | A before and after board of every affected screen, the user's approval, then `DESIGN.md` and a Decisions entry in the same change |

A Decisions entry is one line with the date, what changed, what was rejected and why. Keep the ten most recent entries and let git history keep the rest.

To list the token changes for a review, compare the committed file with the edited one:

```bash
git show HEAD:DESIGN.md > /tmp/DESIGN.before.md
npx @google/design.md diff /tmp/DESIGN.before.md DESIGN.md
```

## Lint recipes

Lint stops a literal from landing when no agent is watching (SYS-3). Offer the recipe that fits the stack, and add it only when the user agrees.

**Tailwind v4.** Clear the default palette so off-system colours do not exist as utilities:

```css
@import "tailwindcss";

@theme {
  --color-*: initial;
  --color-primary: #1f4e5f;
  --color-surface: #faf8f5;
}
```

Arbitrary values such as `bg-[#c8553d]` still compile, so ban them with eslint-plugin-better-tailwindcss:

```js
// eslint.config.js
import betterTailwindcss from "eslint-plugin-better-tailwindcss";

export default [
  {
    plugins: { "better-tailwindcss": betterTailwindcss },
    settings: { "better-tailwindcss": { entryPoint: "src/global.css" } },
    rules: {
      "better-tailwindcss/no-restricted-classes": ["error", {
        restrict: [{ pattern: "\\[.+\\]", message: "Use a design token, not an arbitrary value (SYS-3)." }],
      }],
    },
  },
];
```

**Plain CSS.** stylelint-declaration-strict-value requires a variable for the listed properties everywhere except the token file. The two core duplicate rules catch a later pass that appends an override instead of editing the rule it changes. A repeat inside a different media query is allowed, and the rules suit plain CSS, not SCSS or Less:

```json
{
  "plugins": ["stylelint-declaration-strict-value"],
  "rules": {
    "no-duplicate-selectors": true,
    "declaration-block-no-duplicate-properties": true,
    "scale-unlimited/declaration-strict-value": [
      ["/color$/", "background", "fill", "stroke", "font-family", "border-radius", "box-shadow", "/^(margin|padding|gap)/"],
      { "ignoreVariables": true, "ignoreFunctions": false, "ignoreValues": ["inherit", "currentColor", "transparent", "none", "0", "auto", "/^calc\\(/"] }
    ]
  },
  "overrides": [
    { "files": ["**/tokens.css"], "rules": { "scale-unlimited/declaration-strict-value": null } }
  ]
}
```

**SwiftUI.** SwiftLint regex rules flag literal colours and fixed font sizes outside the theme folder. The ios-kit Swift lint hook runs SwiftLint after each edit when the project has a `.swiftlint.yml`, so these rules apply while an agent works:

```yaml
custom_rules:
  design_literal_color:
    name: "Literal colour"
    regex: "Color\\(\\s*(red:|hue:|white:|hex:)|#colorLiteral"
    excluded:
      - ".*/Theme/.*"
    message: "Take colours from the design system (IOS-1, SYS-3)."
    severity: error
  design_fixed_font_size:
    name: "Fixed font size"
    regex: "\\.system\\(size:"
    excluded:
      - ".*/Theme/.*"
    message: "Use a text style or a scaled design-system font (TYP-1, SYS-3)."
    severity: warning
```

**Compose.** A CI step that needs no type resolution fails on a literal colour or text size outside the theme package:

```bash
! grep -rnE 'Color\(0x|[0-9]+\.sp\b' --include='*.kt' app/src/main | grep -v '/ui/theme/'
```

Projects that already run detekt with type resolution can forbid `androidx.compose.ui.graphics.Color(kotlin.Long)` through `style>ForbiddenMethodCall` instead.

## Turning feedback into rules

When the user corrects a design choice, fix the instance, then encode the correction where it is enforced (SYS-3):

| Correction | Where it goes |
| --- | --- |
| "Stop using that blue" | Remove the colour token so it cannot be used, then add a Don't |
| "Buttons are always this radius" | A component token in the YAML and the radius in the lint recipe |
| "No gradients" | A Don't, plus a lint rule when the stack can express one |
| "That page feels cramped" | The spacing tokens the layout should use, recorded under Layout |

Write a Do or Don't in the user's words only when no token, constraint or lint rule can express the correction.
