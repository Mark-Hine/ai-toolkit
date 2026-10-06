---
verified: 2026-10-06
sources: house
paths:
  - "**/DESIGN.md"
  - "**/*.{css,scss,sass,less}"
  - "**/tailwind.config.{js,cjs,mjs,ts}"
  - "**/*.tokens.json"
  - "**/ui/theme/*.kt"
  - "**/res/values*/{colors,themes,dimens}.xml"
  - "**/res/mipmap-*/**"
  - "**/*.colorset/Contents.json"
  - "**/*.appiconset/**"
  - "**/*.icon/**"
  - "**/{Theme,Color,Colors,Typography,Tokens}*.swift"
  - "**/*.svg"
  - "**/*.webmanifest"
  - "**/favicon.ico"
---

# Design files

This file belongs to a design system or a brand: a design contract, a token or theme file, a stylesheet, an icon or a logo. The rules are in the design standards, under SYS-1 to SYS-3 and the platform icon rules.

- Read the project's `DESIGN.md` before changing this file (SYS-1). If there is none, say so and offer the design-kit iterate skill to draft one.
- Classify the change as use, extend or change before writing it (SYS-2). A change to a shared token, a shared component or a brand asset needs a before and after board and the user's approval.
- Keep literal colours, sizes and spacing in the token files (AND-1, IOS-1, SPC-5).
- Send logo, icon, brand and redesign work to the design-kit iterate skill, which renders options and stops for the user's pick.
