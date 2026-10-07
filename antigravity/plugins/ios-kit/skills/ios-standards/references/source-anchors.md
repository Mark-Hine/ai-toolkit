---
verified: 2026-10-07
sources: inline
---

# iOS source anchors

Each URL `official-docs.md` cites, pinned to its page and to a sentence from it. Use the registry to find a page and these anchors to quote it. Do not fetch a page to grade a rule. Volatile facts, such as store deadlines and latest versions, are still looked up when they are used. `tools/source_anchors.py` in the ai-toolkit repo confirms every quote against the live page and records the date, and that repo's `docs/source-anchors.md` describes the format.

Quotes are verbatim and short, and each names its page. Copyright stays with the source's owner.

### API-DESIGN-GUIDELINES
- URL: https://www.swift.org/documentation/api-design-guidelines/
- Quote: "These design guidelines explain how to make sure that your code feels like a part of the larger Swift ecosystem."
- Confirmed: 2026-10-07 (browser)

### SWIFT-CONCURRENCY
- URL: https://docs.swift.org/latest/documentation/the-swift-programming-language/concurrency/
- Quote: "Swift has built-in support for writing asynchronous and parallel code in a structured way."
- Confirmed: 2026-10-07 (browser)

### SE-0461
- URL: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md
- Quote: "This proposal changes the behavior of nonisolated async functions to run on the caller's actor by default, and introduces an explicit way to state that an async function always switches off of an actor to run."
- Confirmed: 2026-10-07 (html)

### SE-0466
- URL: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md
- Quote: "The -default-isolation flag can be used to control the default actor isolation for all code in the module."
- Confirmed: 2026-10-07 (html)

### SWIFT-6-2-RELEASED
- URL: https://www.swift.org/blog/swift-6.2-released/
- Quote: "Thank you to everyone who shared their experiences, frustrations, and insights that guided the design of Swift 6.2, especially the approachable concurrency model."
- Confirmed: 2026-10-07 (browser)

### THEBASICS
- URL: https://docs.swift.org/latest/documentation/the-swift-programming-language/thebasics/
- Quote: "Force unwrapping a nil value triggers a runtime error."
- Confirmed: 2026-10-07 (browser)

### SWIFT6-MIGRATION
- URL: https://www.swift.org/migration/documentation/migrationguide/
- Quote: "Swift’s concurrency system, introduced in Swift 5.5, makes asynchronous and parallel code easier to write and understand."
- Confirmed: 2026-10-07 (browser)

### ASYNCSTREAM
- URL: https://developer.apple.com/documentation/swift/asyncstream
- Quote: "By default, the buffer limit is Int.max, which means the value is unbounded."
- Confirmed: 2026-10-07 (apple-json)

### 0314-ASYNC-STREAM
- URL: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0314-async-stream.md
- Quote: "By default, every element yielded to an AsyncStream’s continuation is buffered until consumed by iteration."
- Confirmed: 2026-10-07 (html)

### SWIFT-FORMAT
- URL: https://github.com/swiftlang/swift-format
- Quote: "As of Swift 5.8, swift-format depends on the version of SwiftSyntax whose parser has been rewritten in Swift and no longer has dependencies on libraries in the Swift toolchain."
- Confirmed: 2026-10-07 (html)

### SWIFTLINT
- URL: https://github.com/realm/SwiftLint
- Quote: "A tool to enforce Swift style and conventions."
- Confirmed: 2026-10-07 (html)

### MANAGING-MODEL-DATA-IN-YOUR-APP
- URL: https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app
- Quote: "Create connections between your app’s data model and views."
- Confirmed: 2026-10-07 (apple-json)

### MIGRATING-FROM-THE-OBSERVABLE-OBJECT-PRO
- URL: https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro
- Quote: "Update your existing app to leverage the benefits of Observation in Swift."
- Confirmed: 2026-10-07 (apple-json)

### SWIFTUI-DATAFLOW
- URL: https://developer.apple.com/documentation/swiftui/model-data
- Quote: "The framework provides tools, like state variables and bindings, for connecting your app’s data to the user interface."
- Confirmed: 2026-10-07 (apple-json)

### TASK-NAME-PRIORITY-FILE-LINE
- URL: https://developer.apple.com/documentation/swiftui/view/task(name:priority:file:line:_:)
- Quote: "The task priority to use when creating the asynchronous task."
- Confirmed: 2026-10-07 (apple-json)

### 10019
- URL: https://developer.apple.com/videos/play/wwdc2021/10019/
- Quote: "Then Jessica will show you how to connect your concurrent data model to your SwiftUI views and introduce some great new APIs that take advantage of Swift’s new concurrency tools."
- Confirmed: 2026-10-07 (html)

### VIEW
- URL: https://developer.apple.com/documentation/swiftui/view
- Quote: "A type that represents part of your app’s user interface and provides modifiers that you use to configure views."
- Confirmed: 2026-10-07 (apple-json)

### NAVIGATIONPATH
- URL: https://developer.apple.com/documentation/swiftui/navigationpath
- Quote: "A type-erased list of data representing the content of a navigation stack."
- Confirmed: 2026-10-07 (apple-json)

### VIEW-ACCESSIBILITY
- URL: https://developer.apple.com/documentation/swiftui/view-accessibility
- Quote: "Make your SwiftUI apps accessible to everyone, including people with disabilities."
- Confirmed: 2026-10-07 (apple-json)

### APPLYING-CUSTOM-FONTS-TO-TEXT
- URL: https://developer.apple.com/documentation/swiftui/applying-custom-fonts-to-text
- Quote: "SwiftUI’s adaptive text display scales the font automatically using Dynamic Type."
- Confirmed: 2026-10-07 (apple-json)

### HIG
- URL: https://developer.apple.com/design/human-interface-guidelines
- Quote: "The HIG contains guidance and best practices that can help you design a great experience for any Apple platform."
- Confirmed: 2026-10-07 (apple-json)

### TESTING
- URL: https://developer.apple.com/documentation/testing
- Quote: "Create and run tests for your Swift packages and Xcode projects."
- Confirmed: 2026-10-07 (apple-json)

### MIGRATINGFROMXCTEST
- URL: https://developer.apple.com/documentation/testing/migratingfromxctest
- Quote: "Migrate an existing test method or test class written using XCTest."
- Confirmed: 2026-10-07 (apple-json)

### ASYNCHRONOUS-TESTS-AND-EXPECTATIONS
- URL: https://developer.apple.com/documentation/xctest/asynchronous-tests-and-expectations
- Quote: "Verify that asynchronous code behaves as expected."
- Confirmed: 2026-10-07 (apple-json)

### PERFORMACCESSIBILITYAUDIT-FOR
- URL: https://developer.apple.com/documentation/xcuiautomation/xcuiapplication/performaccessibilityaudit(for:_:)
- Quote: "performAccessibilityAudit(for:_:)"
- Confirmed: 2026-10-07 (apple-json)

### SUBMIT-REQS
- URL: https://developer.apple.com/news/upcoming-requirements/
- Quote: "Apps uploaded to App Store Connect must be built with Xcode 26 or later using an SDK for iOS 26"
- Confirmed: 2026-10-07 (html)

### SYSTEM-REQUIREMENTS
- URL: https://developer.apple.com/xcode/system-requirements
- Quote: "SDK: The version of SDKs included in this version of Xcode."
- Confirmed: 2026-10-07 (html)

### XCODE-RELEASE-NOTES
- URL: https://developer.apple.com/documentation/xcode-release-notes
- Quote: "Learn about changes to Xcode."
- Confirmed: 2026-10-07 (apple-json)

### ADDING-PACKAGE-DEPENDENCIES-TO-YOUR-APP
- URL: https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app
- Quote: "Integrate package dependencies to share code between projects, or leverage code from other developers."
- Confirmed: 2026-10-07 (apple-json)

### EDITING-A-PACKAGE-DEPENDENCY-AS-A-LOCAL-
- URL: https://developer.apple.com/documentation/xcode/editing-a-package-dependency-as-a-local-package
- Quote: "Override a package dependency and edit its content by adding it as a local package."
- Confirmed: 2026-10-07 (apple-json)

### SPM
- URL: https://www.swift.org/documentation/package-manager/
- Quote: "Swift Package Manager as a library"
- Confirmed: 2026-10-07 (browser)

### XCODE-BUILD
- URL: https://developer.apple.com/documentation/xcode/build-settings-reference
- Quote: "A detailed list of individual Xcode build settings that control or change the way a target is built."
- Confirmed: 2026-10-07 (apple-json)

### XCODE-MAN-PAGES
- URL: https://keith.github.io/xcode-man-pages/
- Quote: "Xcode's man pages"
- Confirmed: 2026-10-07 (html)

### COCOAPODS-SPECS-REPO
- URL: https://blog.cocoapods.org/CocoaPods-Specs-Repo/
- Quote: "Infrastructure like the Specs repo and the CDN would still operate as long as GitHub and jsDelivr continue to exist, which is pretty likely to be a very long time."
- Confirmed: 2026-10-07 (html)

### POD-INSTALL-VS-UPDATE
- URL: https://guides.cocoapods.org/using/pod-install-vs-update.html
- Quote: "The aim of this guide is to explain when you should use pod install and when you should use pod update."
- Confirmed: 2026-10-07 (html)

### LAUNCH-TIME
- URL: https://developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time
- Quote: "Certain code in an app must run before iOS runs your app’s main() function, adding to the launch time."
- Confirmed: 2026-10-07 (apple-json)

### APP-SIZE
- URL: https://developer.apple.com/documentation/xcode/reducing-your-app-s-size
- Quote: "During development, the only way to get accurate download and installation sizes for your app is to create an app size report on your Mac."
- Confirmed: 2026-10-07 (apple-json)

### MASVS
- URL: https://mas.owasp.org/MASVS/
- Quote: "MASVS-CRYPTO: Cryptographic functionality used to protect sensitive data."
- Confirmed: 2026-10-07 (html)

### MASTG
- URL: https://mas.owasp.org/MASTG/
- Quote: "It describes technical processes for verifying the controls listed in the OWASP MASVS through the weaknesses defined by the OWASP MASWE."
- Confirmed: 2026-10-07 (html)

### TOP10-2024
- URL: https://owasp.org/projects/mobile-top-10
- Quote: "OWASP Mobile Top 10 - An OWASP lab project"
- Confirmed: 2026-10-07 (html)

### PINNING
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
- Quote: "Given that most certificates today are only good for 90 days, using public key pinning can also make the timeline for updating pinsets longer, as you can pin a key where the certificate has not even been issued yet."
- Confirmed: 2026-10-07 (html)

### KEYCHAIN
- URL: https://developer.apple.com/documentation/security/keychain-services
- Quote: "The keychain services API helps you solve this problem by giving your app a mechanism to store small bits of user data in an encrypted database called a keychain."
- Confirmed: 2026-10-07 (apple-json)

### CRYPTOKIT
- URL: https://developer.apple.com/documentation/cryptokit
- Quote: "In addition to working with keys stored in memory, you can also use private keys stored in and managed by the Secure Enclave."
- Confirmed: 2026-10-07 (apple-json)

### LOCALAUTH
- URL: https://developer.apple.com/documentation/localauthentication
- Quote: "Authenticate users biometrically or with a passphrase they already know."
- Confirmed: 2026-10-07 (apple-json)

### ATS
- URL: https://developer.apple.com/documentation/security/preventing-insecure-network-connections
- Quote: "On Apple platforms, a networking security feature called App Transport Security (ATS) improves privacy and data integrity for all apps and app extensions."
- Confirmed: 2026-10-07 (apple-json)

### PRIVACY-MANIFEST
- URL: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
- Quote: "By default, the file is named PrivacyInfo.xcprivacy; this is the required file name for bundled privacy manifests."
- Confirmed: 2026-10-07 (apple-json)

### THIRD-PARTY-SDK-REQUIREMENTS
- URL: https://developer.apple.com/support/third-party-SDK-requirements/
- Quote: "When you adopt a new version of a third-party SDK in your app, Xcode will validate that it was signed by the same developer, improving the integrity of your software supply chain."
- Confirmed: 2026-10-07 (html)

### ATT
- URL: https://developer.apple.com/documentation/apptrackingtransparency
- Quote: "Your app needs to use the App Tracking Transparency framework if it collects data about people and shares it with other companies to track them across apps and websites."
- Confirmed: 2026-10-07 (apple-json)

### APP-ATTEST
- URL: https://developer.apple.com/documentation/devicecheck
- Quote: "The server-to-server APIs also let you verify that the token you receive comes from your app on an Apple device."
- Confirmed: 2026-10-07 (apple-json)

### OSV
- URL: https://osv.dev
- Quote: "An easy-to-use API is available to query for all known vulnerabilities by either a commit hash, or a package version."
- Confirmed: 2026-10-07 (html)

### SWIFTUI-AGENT-SKILL
- URL: https://github.com/twostraws/swiftui-agent-skill
- Quote: "SwiftUI Pro was originally created by Paul Hudson, who writes free Swift tutorials over at Hacking with Swift."
- Confirmed: 2026-10-07 (html)

### MOBILEBUILDMCP
- URL: https://github.com/getsentry/MobileBuildMCP
- Quote: "MobileBuildMCP ships as a single package with two modes: a CLI for direct terminal use and an MCP server for AI coding agents."
- Confirmed: 2026-10-07 (html)

### SOSUMI-AI
- URL: https://github.com/nshipster/sosumi.ai
- Quote: "It converts a single Apple Developer page to Markdown only when requested by a user."
- Confirmed: 2026-10-07 (html)

### XCODE-26-POINT-3-UNLOCKS-THE-POWER-OF-AG
- URL: https://www.apple.com/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/
- Quote: "Xcode 26.3 introduces support for agentic coding, a new way in Xcode for developers to build apps using coding agents such as Anthropic’s Claude Agent and OpenAI’s Codex."
- Confirmed: 2026-10-07 (html)

### MCP
- URL: https://tuist.dev/en/docs/guides/features/agentic-coding/mcp
- Quote: "Most tools are read-only and scoped to authenticated Tuist project data."
- Confirmed: 2026-10-07 (html)

### 763888
- URL: https://developer.apple.com/forums/thread/763888
- Quote: none (offline)
