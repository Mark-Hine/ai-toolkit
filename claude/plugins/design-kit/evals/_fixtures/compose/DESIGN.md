---
version: alpha
name: Ledgerly Android
description: The Ledgerly app for café owners on Android phones.
colors:
  primary: "#1F4E5F"
  on-primary: "#FFFFFF"
  surface: "#FAF8F5"
  on-surface: "#1C1B1A"
  tertiary: "#C8553D"
omitted:
  - section: typography
    reason: The Material 3 type roles in ui/theme/Type.kt are the source.
  - section: spacing
    reason: The Spacing object in ui/theme/Spacing.kt is the source.
  - section: rounded
    reason: The Material 3 shapes in ui/theme/Shape.kt are the source.
  - section: components
    reason: Material 3 components take their style from LedgerlyTheme.
---

# Ledgerly Android

## Overview

The Android app shows a café owner this week's margin and what needs paying. It is calm and exact, and it reads at a glance between services.

The Kotlin theme in `ui/theme/` is the source of truth. Screens take colours from `MaterialTheme.colorScheme`, type from `MaterialTheme.typography`, shapes from `MaterialTheme.shapes` and spacing from the `Spacing` object.

## Colors

Teal (`primary`) carries the brand and the main action. Clay (`tertiary`) marks money that needs attention and nothing else.

## Layout

Screens use a single column with `Spacing.md` margins and `Spacing.md` between cards.

## Components

Cards use `MaterialTheme.shapes.medium`. Buttons are Material 3 buttons in the theme's colours.

## Do's and Don'ts

- Do take every colour, text style, shape and spacing value from the theme.
- Don't write a literal `Color(0x...)`, `sp` or `dp` value in a screen.
- Don't use clay for anything except money that needs attention.
