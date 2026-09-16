# Official documentation registry

Canonical URLs for WebFetch and citing. Apple pages render client-side; if a fetch returns nothing, retry via
`https://developer.apple.com/tutorials/data/documentation/<path>.json` or WebSearch the page title. Verified 2026-09-04.

## Swift
- API Design Guidelines: https://www.swift.org/documentation/api-design-guidelines/
- The Swift Programming Language, Concurrency (structured tasks, actors, `Task.detached` caveats): https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/
- The Basics (optionals; "Force unwrapping a nil value triggers a runtime error"): https://docs.swift.org/swift-book/documentation/the-swift-programming-language/thebasics/
- Swift 6 / strict-concurrency migration guide (staged, per-module adoption): https://www.swift.org/migration/documentation/migrationguide/
  · enabling complete checking: /swift-6-concurrency-migration-guide/enabledataracesafety · strategy: /swift-6-concurrency-migration-guide/migrationstrategy
- AsyncStream (buffering policy, default unbounded): https://developer.apple.com/documentation/swift/asyncstream · design (SE-0314): https://github.com/swiftlang/swift-evolution/blob/main/proposals/0314-async-stream.md
- swift-format (bundled with the Swift 6 toolchain): https://github.com/swiftlang/swift-format
- SwiftLint (`force_unwrapping` is opt-in; `force_cast`/`force_try` on by default): https://github.com/realm/SwiftLint

## SwiftUI
- Managing model data in your app (`@Observable`, `@State`, `@Environment`): https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app
- Migrating from ObservableObject to `@Observable` (iOS 17+): https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro
- Model data overview (single source of truth): https://developer.apple.com/documentation/swiftui/model-data
- `task(name:priority:file:line:_:)` ("If the task doesn't finish before SwiftUI removes the view or the view changes identity, SwiftUI cancels the task"): https://developer.apple.com/documentation/swiftui/view/task(name:priority:file:line:_:)
- WWDC21 "Discover concurrency in SwiftUI" (`@MainActor` on the observable model): https://developer.apple.com/videos/play/wwdc2021/10019/
- Presentation as data: `alert(_:isPresented:actions:)`, `sheet(item:onDismiss:content:)`, `navigationDestination(item:destination:)`
  under https://developer.apple.com/documentation/swiftui/view — the system resets the binding on dismiss.
- `NavigationStack` / `NavigationPath` (programmatic navigation as data): https://developer.apple.com/documentation/swiftui/navigationpath
- Accessibility modifiers: https://developer.apple.com/documentation/swiftui/view-accessibility
- Custom fonts and Dynamic Type (`@ScaledMetric`): https://developer.apple.com/documentation/swiftui/applying-custom-fonts-to-text
- HIG: https://developer.apple.com/design/human-interface-guidelines · Buttons (44×44 pt hit region): /buttons · Alerts (use sparingly): /alerts · Accessibility: /accessibility

## Testing
- Swift Testing (Xcode 16+, `@Test`, `#expect`, `#require`, `@Suite`, parallel by default, `.serialized`): https://developer.apple.com/documentation/testing
- Migrating from XCTest (both frameworks can share a target): https://developer.apple.com/documentation/testing/migratingfromxctest
- XCTest asynchronous tests and expectations: https://developer.apple.com/documentation/xctest/asynchronous-tests-and-expectations
- UI-test accessibility audit (`performAccessibilityAudit`, iOS 17+, module XCUIAutomation): https://developer.apple.com/documentation/xcuiautomation/xcuiapplication/performaccessibilityaudit(for:_:)

## Build
- App Store upcoming requirements (minimum Xcode/SDK to upload; from 2026-04-28 Xcode 26 + iOS 26 SDK): https://developer.apple.com/news/upcoming-requirements/
- Xcode ↔ macOS ↔ SDK table: https://developer.apple.com/support/xcode/ · Xcode release notes: https://developer.apple.com/documentation/xcode-release-notes
- Adding package dependencies (version rules; commit `Package.resolved`): https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app
- Editing a package dependency as a local package: https://developer.apple.com/documentation/xcode/editing-a-package-dependency-as-a-local-package
- Swift Package Manager: https://www.swift.org/documentation/package-manager/ (`swift package describe|show-dependencies|update`)
- Build settings reference: https://developer.apple.com/documentation/xcode/build-settings-reference
- `xcodebuild` / `simctl` man pages (mirror): https://keith.github.io/xcode-man-pages/xcodebuild.1.html · https://keith.github.io/xcode-man-pages/simctl.1.html
- CocoaPods: maintenance mode since 2024-08; trunk read-only from 2026-12-02: https://blog.cocoapods.org/CocoaPods-Specs-Repo/ · install vs update: https://guides.cocoapods.org/using/pod-install-vs-update.html
- Reducing launch time / app size: https://developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time · https://developer.apple.com/documentation/xcode/reducing-your-app-s-size

## Security and privacy
- OWASP MASVS v2.1.0: https://mas.owasp.org/MASVS/ · MASTG: https://mas.owasp.org/MASTG/ · Mobile Top 10 2024: https://owasp.org/www-project-mobile-top-10/
- OWASP Pinning Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
- Keychain Services (accessibility classes, `SecAccessControl`): https://developer.apple.com/documentation/security/keychain-services
- CryptoKit: https://developer.apple.com/documentation/cryptokit · LocalAuthentication: https://developer.apple.com/documentation/localauthentication
- App Transport Security exceptions: https://developer.apple.com/documentation/security/preventing-insecure-network-connections
- Privacy manifests and required-reason APIs: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
  · SDKs that must ship one: https://developer.apple.com/support/third-party-SDK-requirements/
- App Tracking Transparency: https://developer.apple.com/documentation/apptrackingtransparency · DeviceCheck / App Attest: https://developer.apple.com/documentation/devicecheck
- OSV vulnerability database (reads `Package.resolved` via osv-scanner): https://osv.dev

## Community tooling worth knowing (not Apple, verify before relying on it)
- SwiftUI Agent Skill by Paul Hudson, `twostraws/swiftui-agent-skill`, ~4.7k stars. Catalogue of LLM SwiftUI mistakes (navigation, deprecated APIs, accessibility, performance). Install beside this plugin with `npx skills add https://github.com/twostraws/swiftui-agent-skill --skill swiftui-pro`; the rules here defer to it on SwiftUI API detail. https://github.com/twostraws/swiftui-agent-skill
- XcodeBuildMCP, ~6.4k stars, MCP server wrapping `xcodebuild`/`simctl` with UI automation on the simulator. Optional; the playbooks work with plain `xcodebuild` and `xcrun simctl`. https://github.com/getsentry/XcodeBuildMCP
- Sosumi, Apple docs, HIG and WWDC transcripts as Markdown for agents, MCP at `sosumi.ai/mcp`. Use when WebFetch of developer.apple.com returns the JS shell. https://github.com/nshipster/sosumi.ai
- Xcode 26.3 ships native agent integration over MCP (docs search, project settings, Previews). https://www.apple.com/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/
- Tuist MCP and skill for `Project.swift` work, only in Tuist repos. https://tuist.dev/en/docs/guides/features/agentic-coding/mcp
- `xcresulttool`: `xcrun xcresulttool get test-results summary --path <bundle>` is the current form; `get --format json` needs `--legacy` since Xcode 16. https://developer.apple.com/forums/thread/763888
- SwiftFormat/SwiftLint on edit: this plugin's `hooks/swift-lint.sh` runs them after each `.swift` edit when the repo has `.swiftformat` or `.swiftlint.yml` and the binary is installed.
