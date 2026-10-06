---
version: alpha
name: Ledgerly
description: Bookkeeping for independent cafés. Calm, exact and warm, like a well-kept ledger.
colors:
  primary: "#1F4E5F"
  on-primary: "#FFFFFF"
  surface: "#FAF8F5"
  card: "#FFFFFF"
  on-surface: "#1C1B1A"
  muted: "#6B6560"
  accent: "#C8553D"
  border: "#E4DED7"
typography:
  display:
    fontFamily: Fraunces
    fontSize: 2.5rem
    fontWeight: 600
    lineHeight: 1.15
  title:
    fontFamily: Fraunces
    fontSize: 1.25rem
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: Source Sans 3
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: Source Sans 3
    fontSize: 0.875rem
    fontWeight: 600
    lineHeight: 1.4
rounded:
  sm: 4px
  md: 8px
  full: 9999px
spacing:
  "1": 0.25rem
  "2": 0.5rem
  "3": 0.75rem
  "4": 1rem
  "6": 1.5rem
  "8": 2rem
  "12": 3rem
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
  card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
  input:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
  divider:
    backgroundColor: "{colors.border}"
    height: 1px
  footer:
    textColor: "{colors.muted}"
    typography: "{typography.label}"
  status-dot-attention:
    backgroundColor: "{colors.accent}"
    rounded: "{rounded.full}"
    size: 8px
---

# Ledgerly

## Overview

Ledgerly is bookkeeping for owners of independent cafés, who check their numbers between services on a phone or an old laptop. The interface is calm and exact. Warmth comes from the serif display face and the clay accent, never from decoration.

Code tokens in `tokens.css` are the source of truth, and every value in this file mirrors one of them. `components.css` uses only those tokens.

## Colors

Deep teal (`primary`) carries the brand and every primary action. Clay (`accent`) marks money that needs attention, such as an unpaid invoice, and nothing else. Text sits on the warm `surface` or on white `card` panels.

## Typography

Fraunces sets display headings and card titles. Source Sans 3 sets body text and labels. Body text stays at 1rem with a 1.6 line height.

## Layout

Content sits in one centred column at most 68rem wide. Feature cards flow in a grid with a minimum width of 20rem. Every gap, padding and margin comes from the `spacing` scale.

## Elevation & Depth

Cards use the one soft shadow token. Nothing else casts a shadow.

## Shapes

Buttons, cards and inputs share the `md` radius. The `full` radius is reserved for avatars and status dots.

## Components

The primary button is teal with white label text. Cards are white with a hairline border, the `md` radius and the card shadow. Inputs match the cards. Dividers and card borders use the `border` colour. The footer uses muted label text. A clay status dot marks an amount that needs attention.

## Do's and Don'ts

- Do use the spacing scale for every gap, padding and margin.
- Do keep the accent for money that needs attention.
- Don't add a colour, font or radius outside the tokens.
- Don't use gradients or glow effects.

## Brand marks

The logo is `logo.svg`, a rounded teal square with a white L. It appears in the header at 32 px and as the favicon.

## Decisions

- 2026-09-12: Teal replaced the earlier blue, because owners read the blue as a bank and not as their own tool.
