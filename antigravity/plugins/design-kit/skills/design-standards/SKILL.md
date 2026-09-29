---
name: design-standards
description: "Tiered UI design rules for Android, iOS and web, with sources, rationale and platform APIs. Use when building, redesigning or reviewing a screen, component or design system, or when asked about contrast, touch targets, spacing, type scale, screen states, motion, dark mode or UI that looks AI-generated."
metadata:
  verified: 2026-09-29
  sources: references/sources.md
---

# Design standards

The rules live in `~/.gemini/config/guidance/design-standards.md`. This skill adds the sources, the reasons and the APIs. If that rule file is missing, grade against the Tier 1 sources in `references/sources.md` only and say so.

1. Read the project instructions file, then the rule file. Note any T2 rule IDs the project opts in.
2. Name the platform, and the tone and density the screen commits to (DIR-1).
3. Build or review against the rule file one section at a time. Take each API from `references/platform-apis.md`. Do not restate rules from memory.
4. List the states the screen can reach (STA-1) and confirm that the state model has a case for each and the UI renders it.
5. Check accessibility on a device or simulator where you can, at the largest text size, with the screen reader, with reduced motion and in dark mode.
6. When a rule and a source in `references/sources.md` disagree, follow the source and report the rule ID, the source and its date.
7. Read `references/rationale.md` before overriding or arguing a T2 rule. T2 rules are defaults and grade Nit unless the project opts in.
8. Hand the diff to `ui-reviewer` through `invoke_subagent` before calling the work done.
