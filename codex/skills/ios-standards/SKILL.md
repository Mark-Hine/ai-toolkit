---
name: ios-standards
description: "Index of official Apple/Swift/Xcode docs, Apple sample apps (Landmarks, Backyard Birds, Food Truck) and iOS house patterns (state, UI events)."
---

Read the project AGENTS.md and applicable global guidance first. Fall back to CLAUDE.md if AGENTS.md is absent. Follow the global rules for optional tools, specialist agents and Git actions.

# iOS standards reference

Use this to pick the authoritative source for a question, then fetch it with web fetch. Do not answer deadline,
deprecation, App Store requirement or version questions from memory.

| Question | Read |
|---|---|
| State ownership, @Observable vs ObservableObject, environment | [official-docs.md](references/official-docs.md) §SwiftUI, then [apple-samples.md](references/apple-samples.md) |
| One-shot model → UI events (navigation, alerts, toasts) | [ui-events.md](references/ui-events.md) (house pattern and how it differs from the Android rule) |
| Too many closures on a view | [ui-events.md](references/ui-events.md) §Actions struct |
| Design system, tokens, component API, previews | [apple-samples.md](references/apple-samples.md) |
| Concurrency, @MainActor, Swift 6 language mode | [official-docs.md](references/official-docs.md) §Swift |
| Testing (Swift Testing vs XCTest), accessibility | [official-docs.md](references/official-docs.md) §Testing, §Accessibility |
| Xcode, SwiftPM, CocoaPods, App Store submission gates | [official-docs.md](references/official-docs.md) §Build |
| Security controls, Keychain, ATS, privacy manifests | [official-docs.md](references/official-docs.md) §Security |
| Starting a per-repo `AGENTS.md` | [project-agents-md-template.md](references/project-agents-md-template.md) |
| MCP servers, community skills, lint hooks, xcresulttool | [official-docs.md](references/official-docs.md) §Community tooling |

Guardrails when applying any reference to this repo:
- Target repos are often hybrid legacy apps (UIKit + SwiftUI, CocoaPods + SwiftPM). Recommend the blueprint pattern for new
  code; do not propose rewriting working UIKit screens unless the ticket is a migration.
- Apple publishes no architecture doctrine. Sample apps show `@Observable` models injected through the environment, model
  code in separate Swift packages and navigation as data; treat that as consensus, not a rule. MV vs MVVM, a domain layer
  and a view model per view are choices; grade consistency with the codebase, not the choice.
- A reference may need a newer deployment target or Xcode than the repo (`@Observable` iOS 17+, Swift Testing Xcode 16+,
  Liquid Glass iOS 26+). State the version the source targets and the repo's gap.
