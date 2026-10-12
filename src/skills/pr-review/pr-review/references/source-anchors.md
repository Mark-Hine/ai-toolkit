---
verified: 2026-10-07
sources: inline
---

# pr-review source anchors

Each source key the platform packs and `pci-dss.md` cite, pinned to its page and to the sentence or two the
pack relies on. Grade from the packs and quote the anchor when a finding's citation is disputed. Do not
fetch a page to grade a rule. Volatile facts, such as store deadlines and latest versions, are still looked
up at review time (protocol.md §13). `tools/source_anchors.py` in the ai-toolkit repo confirms every quote
against the live page and records the date. The format is in that repo's `docs/source-anchors.md`.

Quotes are verbatim and short, and each names its page. Copyright stays with the source's owner.

## Android pack

### ARCH-GUIDE
- URL: https://developer.android.com/topic/architecture
- Quote: "Considering common architectural principles, design each application with at least two layers:"
- Confirmed: 2026-10-07 (html)

### ARCH-RECS
- URL: https://developer.android.com/topic/architecture/recommendations
- Quote: "Strongly recommended: Implement this practice unless it clashes fundamentally with your approach."
- Confirmed: 2026-10-07 (html)

### MODULARIZATION
- URL: https://developer.android.com/topic/modularization
- Quote: "Modularization is a practice of organizing a codebase into loosely coupled and self contained parts."
- Confirmed: 2026-10-07 (html)

### NAV-TYPESAFE
- URL: https://developer.android.com/guide/navigation/design/type-safety
- Quote: "You can use built-in type safe APIs to provide compile-time type safety for your navigation graph."
- Confirmed: 2026-10-07 (html)

### NIA
- URL: https://github.com/android/nowinandroid
- Quote: "Now in Android is a fully functional Android app built entirely with Kotlin and Jetpack Compose."
- Confirmed: 2026-10-07 (html)

### NIA-1273
- URL: https://github.com/android/nowinandroid/discussions/1273
- Quote: "I'm an engineer on the Android DevRel team at Google and I'm the Tech Lead on this project."
- Confirmed: 2026-10-07 (html)

### JETSNACK
- URL: https://github.com/android/compose-samples/tree/main/Jetsnack
- Quote: "Jetsnack's major feature is demonstrating how to implement a custom design system."
- Confirmed: 2026-10-07 (html)

### STREAM-THEME
- URL: https://getstream.io/blog/designing-effective-compose/
- Quote: "Next, you should create a CompositionLocal to hold the design specifications."
- Confirmed: 2026-10-07 (html)

### COMPOSE-API
- URL: https://github.com/androidx/androidx/blob/androidx-main/compose/docs/compose-api-guidelines.md
- Quote: "Element functions MUST NOT accept multiple Modifier parameters."
- Confirmed: 2026-10-07 (html)

### COMPOSE-STABILITY
- URL: https://developer.android.com/develop/ui/compose/performance/stability
- Quote: "Compose considers types to be either stable or unstable."
- Confirmed: 2026-10-07 (html)

### A11Y
- URL: https://developer.android.com/develop/ui/compose/accessibility
- Quote: "Accessibility in Jetpack Compose"
- Confirmed: 2026-10-07 (html)

### EUM-LOADING
- URL: https://proandroiddev.com/loading-initial-data-in-launchedeffect-vs-viewmodel-f1747c20ce62
- Quote: none (offline)

### STATE-PRODUCTION
- URL: https://developer.android.com/topic/architecture/ui-layer/state-production
- Quote: "Don't launch asynchronous operations in the init block or constructor of a ViewModel."
- Quote: "define an idempotent initialize function to explicitly start the state production pipeline"
- Confirmed: 2026-10-07 (html)

### HOUSE
- URL: https://github.com/Mark-Hine/ai-toolkit/tree/main/claude/plugins/android-kit/skills/standards/references
- Quote: none (house)

### STRONG-SKIPPING
- URL: https://developer.android.com/develop/ui/compose/performance/stability/strongskipping
- Quote: "Strong Skipping is enabled by default in Kotlin 2.0.20."
- Confirmed: 2026-10-07 (html)

### STABILITY-FIX
- URL: https://developer.android.com/develop/ui/compose/performance/stability/fix
- Quote: "When working to fix issues with stability, you shouldn't attempt to make every composable skippable."
- Confirmed: 2026-10-07 (html)

### NAV3
- URL: https://developer.android.com/guide/navigation/navigation-3
- Quote: "Navigation 3 is a navigation library designed to work with Compose."
- Confirmed: 2026-10-07 (html)

### UI-STANDARDS
- URL: https://github.com/Mark-Hine/ai-toolkit/blob/main/shared/guidance/design-standards.md
- Quote: none (house)

### M3-DESIGN
- URL: https://m3.material.io
- Quote: "Google's latest open source design system"
- Confirmed: 2026-10-07 (browser)

### WCAG22
- URL: https://www.w3.org/TR/WCAG22/
- Quote: "Web Content Accessibility Guidelines (WCAG) 2.2 covers a wide range of recommendations for making web content more accessible."
- Confirmed: 2026-10-07 (html)

### VM-EVENTS
- URL: https://developer.android.com/topic/architecture/ui-layer/events
- Quote: "UI events are actions that should be handled in the UI layer, either by the UI or by the ViewModel."
- Confirmed: 2026-10-07 (html)

### EVENT-ANTIPATTERNS
- URL: https://manuelvivo.dev/viewmodel-events-antipatterns
- Quote: "Note: This antipattern could be mitigated by using Dispatchers.Main.immediate when sending and receiving events."
- Confirmed: 2026-10-07 (html)

### KTX-2886
- URL: https://github.com/Kotlin/kotlinx.coroutines/issues/2886
- Quote: "Primitive or Channel that guarantees the delivery and processing of items"
- Confirmed: 2026-10-07 (html)

### ORBIT-SE
- URL: https://github.com/orbit-mvi/orbit-mvi/blob/main/website/docs/Core/index.md
- Quote: "Side effects are cached by default if no observers are listening."
- Confirmed: 2026-10-07 (html)

### SAFE-COLLECT
- URL: https://medium.com/androiddevelopers/a-safer-way-to-collect-flows-from-android-uis-23080b1f8bda
- Quote: none (offline)

### COROUTINES
- URL: https://developer.android.com/kotlin/coroutines/coroutines-best-practices
- Quote: "Don't hardcode Dispatchers when creating new coroutines or calling withContext."
- Quote: "Suspend functions should be main-safe, meaning they're safe to call from the main thread."
- Confirmed: 2026-10-07 (html)

### BANES-STABILITY
- URL: https://chrisbanes.me/posts/composable-metrics/
- Quote: "Restartable and skippable are Compose attributes for functions, whereas immutability & stability are attributes of object instances, specifically the objects which are passed to composable functions."
- Confirmed: 2026-10-07 (html)

### PLAY-INTEGRITY
- URL: https://developer.android.com/google/play/integrity/overview
- Quote: "The Play Integrity API helps you check that user actions and server requests are coming from your genuine app, installed by Google Play, running on a genuine and certified Android device."
- Confirmed: 2026-10-07 (html)

### DATASTORE
- URL: https://developer.android.com/topic/libraries/architecture/datastore
- Quote: "If you're using SharedPreferences to store data, consider migrating to DataStore instead."
- Confirmed: 2026-10-07 (html)

### MASVS
- URL: https://mas.owasp.org/MASVS/
- Quote: "MASVS-CRYPTO: Cryptographic functionality used to protect sensitive data."
- Confirmed: 2026-10-07 (html)

### MASTG
- URL: https://mas.owasp.org/MASTG/
- Quote: "It describes technical processes for verifying the controls listed in the OWASP MASVS through the weaknesses defined by the OWASP MASWE."
- Confirmed: 2026-10-07 (html)

### PINNING
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
- Quote: "Given that most certificates today are only good for 90 days, using public key pinning can also make the timeline for updating pinsets longer, as you can pin a key where the certificate has not even been issued yet."
- Confirmed: 2026-10-07 (html)

### TOP10-2024
- URL: https://owasp.org/projects/mobile-top-10
- Quote: "OWASP Mobile Top 10 - An OWASP lab project"
- Confirmed: 2026-10-07 (html)

### PCI-DSS
- URL: https://www.pcisecuritystandards.org/document_library/
- Quote: "PCI DSS Summary of Changes v4.0 to v4.0.1"
- Confirmed: 2026-10-07 (html)

### KOTLIN-NULL-SAFETY
- URL: https://kotlinlang.org/docs/null-safety.html
- Quote: "However, if the value is null, the !! operator forces it to be treated as non-nullable, which results in an NPE."
- Confirmed: 2026-10-07 (html)

### KOTLIN-CASTS
- URL: https://kotlinlang.org/docs/typecasts.html
- Quote: "If a cast fails with the as operator, a ClassCastException is thrown at runtime."
- Confirmed: 2026-10-07 (html)

### KOTLIN-ENUMS
- URL: https://kotlinlang.org/docs/enum-classes.html
- Quote: "If there is no enum constant with the specified name, valueOf() throws an IllegalArgumentException."
- Confirmed: 2026-10-07 (html)

### KOTLIN-SEALED
- URL: https://kotlinlang.org/docs/sealed-classes.html
- Quote: "In such cases, you don't need to add an else clause:"
- Confirmed: 2026-10-07 (html)

### OSV
- URL: https://osv.dev
- Quote: "An easy-to-use API is available to query for all known vulnerabilities by either a commit hash, or a package version."
- Confirmed: 2026-10-07 (html)

### PLAY-USERDATA
- URL: https://support.google.com/googleplay/android-developer/answer/13327111
- Quote: "If your app allows users to create an account from within your app, our User data policy requires that it must also allow users to request for their account to be deleted."
- Confirmed: 2026-10-07 (html)

### PLAY-VITALS
- URL: https://developer.android.com/google/play/vitals
- Quote: "Core vitals are the most important metrics in Android vitals, and affect the visibility of your app on Google Play."
- Confirmed: 2026-10-07 (html)

### GRADLE-DOCS
- URL: https://docs.gradle.org/current/userguide/best_practices_general.html
- Quote: "General Gradle Best Practices"
- Confirmed: 2026-10-07 (html)

### AGP-BUILD
- URL: https://developer.android.com/build/optimize-your-build
- Quote: "The configuration cache lets Gradle record information about the build tasks graph and reuse it in subsequent builds, so Gradle doesn't have to reconfigure the whole build again."
- Confirmed: 2026-10-07 (html)

### BASELINE-PROF
- URL: https://developer.android.com/topic/performance/baselineprofiles/overview
- Quote: "By shipping a Baseline Profile in an app or library, Android Runtime (ART) can optimize specified code paths through Ahead-of-Time (AOT) compilation, providing performance enhancements for every new user and every app update."
- Confirmed: 2026-10-07 (html)

### KSP
- URL: https://kotlinlang.org/docs/ksp-overview.html
- Quote: "Kotlin Symbol Processing (KSP) is a source code generation framework for Kotlin."
- Confirmed: 2026-10-07 (html)

## Generic pack

### CIS
- URL: https://www.cisecurity.org/cis-benchmarks
- Quote: "Are you new to the CIS Benchmarks?"
- Confirmed: 2026-10-07 (html)

### API-TOP10
- URL: https://owasp.org/projects/api-security-project
- Quote: "API Security Top 10 2023"
- Confirmed: 2026-10-07 (html)

### ASVS
- URL: https://owasp.org/projects/asvs
- Quote: "The OWASP Application Security Verification Standard (ASVS) Project provides a basis for testing web application technical security controls and also provides developers with a list of requirements for secure development."
- Confirmed: 2026-10-07 (html)

### CHEATSHEETS
- URL: https://cheatsheetseries.owasp.org/
- Quote: "These cheat sheets were created by various application security professionals who have expertise in specific topics."
- Confirmed: 2026-10-07 (html)

### SEMVER
- URL: https://semver.org/
- Quote: "Semantic Versioning 2.0.0"
- Confirmed: 2026-10-07 (html)

### TOP10
- URL: https://owasp.org/projects/top-ten
- Quote: "The OWASP Top 10 is a standard awareness document for developers and web application security."
- Confirmed: 2026-10-07 (html)

## iOS pack

### SWIFTUI-DATAFLOW
- URL: https://developer.apple.com/documentation/swiftui/model-data
- Quote: "The framework provides tools, like state variables and bindings, for connecting your app’s data to the user interface."
- Confirmed: 2026-10-07 (apple-json)

### BACKYARD-BIRDS
- URL: https://github.com/apple/sample-backyard-birds
- Quote: "The sample implements its data model using SwiftData for persistence, and integrates seamlessly with SwiftUI using the Observable protocol."
- Confirmed: 2026-10-07 (html)

### FOOD-TRUCK
- URL: https://github.com/apple/sample-food-truck
- Quote: "The Food Truck sample project contains two types of app targets:"
- Confirmed: 2026-10-07 (html)

### SWIFT-CONCURRENCY
- URL: https://docs.swift.org/latest/documentation/the-swift-programming-language/concurrency/
- Quote: "Swift has built-in support for writing asynchronous and parallel code in a structured way."
- Confirmed: 2026-10-07 (browser)

### SWIFT6-MIGRATION
- URL: https://www.swift.org/migration/documentation/migrationguide/
- Quote: "Swift’s concurrency system, introduced in Swift 5.5, makes asynchronous and parallel code easier to write and understand."
- Confirmed: 2026-10-07 (browser)

### SE-0461
- URL: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md
- Quote: "This proposal changes the behavior of nonisolated async functions to run on the caller's actor by default, and introduces an explicit way to state that an async function always switches off of an actor to run."
- Confirmed: 2026-10-07 (html)

### SE-0466
- URL: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md
- Quote: "The -default-isolation flag can be used to control the default actor isolation for all code in the module."
- Confirmed: 2026-10-07 (html)

### SPM
- URL: https://www.swift.org/documentation/package-manager/
- Quote: "Swift Package Manager as a library"
- Confirmed: 2026-10-07 (browser)

### XCODE-BUILD
- URL: https://developer.apple.com/documentation/xcode/build-settings-reference
- Quote: "A detailed list of individual Xcode build settings that control or change the way a target is built."
- Confirmed: 2026-10-07 (apple-json)

### SWIFTLINT
- URL: https://github.com/realm/SwiftLint
- Quote: "A tool to enforce Swift style and conventions."
- Confirmed: 2026-10-07 (html)

### HIG
- URL: https://developer.apple.com/design/human-interface-guidelines
- Quote: "The HIG contains guidance and best practices that can help you design a great experience for any Apple platform."
- Confirmed: 2026-10-07 (apple-json)

### A11Y.ios
- URL: https://developer.apple.com/documentation/accessibility
- Quote: "Learn more about how to support different types of accessibility needs in your app using Apple’s wide range of accessibility APIs."
- Confirmed: 2026-10-07 (apple-json)

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

### APP-ATTEST
- URL: https://developer.apple.com/documentation/devicecheck
- Quote: "The server-to-server APIs also let you verify that the token you receive comes from your app on an Apple device."
- Confirmed: 2026-10-07 (apple-json)

### PRIVACY-MANIFEST
- URL: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
- Quote: "By default, the file is named PrivacyInfo.xcprivacy; this is the required file name for bundled privacy manifests."
- Confirmed: 2026-10-07 (apple-json)

### ATT
- URL: https://developer.apple.com/documentation/apptrackingtransparency
- Quote: "Your app needs to use the App Tracking Transparency framework if it collects data about people and shares it with other companies to track them across apps and websites."
- Confirmed: 2026-10-07 (apple-json)

### SUBMIT-REQS
- URL: https://developer.apple.com/news/upcoming-requirements/
- Quote: "Apps uploaded to App Store Connect must be built with Xcode 26 or later using an SDK for iOS 26"
- Confirmed: 2026-10-07 (html)

### LAUNCH-TIME
- URL: https://developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time
- Quote: "Certain code in an app must run before iOS runs your app’s main() function, adding to the launch time."
- Confirmed: 2026-10-07 (apple-json)

### APP-SIZE
- URL: https://developer.apple.com/documentation/xcode/reducing-your-app-s-size
- Quote: "During development, the only way to get accurate download and installation sizes for your app is to create an app size report on your Mac."
- Confirmed: 2026-10-07 (apple-json)

### SWIFT-BOOK
- URL: https://docs.swift.org/latest/documentation/the-swift-programming-language/
- Quote: "The Swift Programming Language"
- Confirmed: 2026-10-07 (browser)

### OSLOG
- URL: https://developer.apple.com/documentation/os/logger
- Quote: "When you include an interpolated string or custom object in your message, the system redacts the value of that string or object by default."
- Confirmed: 2026-10-07 (apple-json)

### METRICKIT
- URL: https://developer.apple.com/documentation/metrickit
- Quote: "MetricKit provides on-device app diagnostics and power and performance metrics the system captures."
- Confirmed: 2026-10-07 (apple-json)

## React and Next.js pack

### REACT-RULES
- URL: https://react.dev/reference/rules
- Quote: "This section describes the rules you need to follow to write idiomatic React code."
- Confirmed: 2026-10-07 (html)

### REACT-HOOKS-RULES
- URL: https://react.dev/reference/rules/rules-of-hooks
- Quote: "Instead, always use Hooks at the top level of your React function, before any early returns."
- Confirmed: 2026-10-07 (html)

### REACT-NO-EFFECT
- URL: https://react.dev/learn/you-might-not-need-an-effect
- Quote: "If there is no external system involved (for example, if you want to update a component’s state when some props or state change), you shouldn’t need an Effect."
- Confirmed: 2026-10-07 (html)

### REACT-SYNC-EFFECTS
- URL: https://react.dev/learn/synchronizing-with-effects
- Quote: "Writing fetch calls inside Effects is a popular way to fetch data, especially in fully client-side apps."
- Confirmed: 2026-10-07 (html)

### REACT-KEYS
- URL: https://react.dev/learn/rendering-lists#why-does-react-need-keys
- Quote: "You need to give each array item a key — a string or a number that uniquely identifies it among other items in that array:"
- Confirmed: 2026-10-07 (html)

### REACT-VERSIONS
- URL: https://react.dev/versions
- Quote: "In 2023, we launched our new docs for React 18 as react.dev."
- Confirmed: 2026-10-07 (html)

### NEXT-STATIC
- URL: https://nextjs.org/docs/pages/guides/static-exports
- Quote: "Guides: Static Exports"
- Confirmed: 2026-10-07 (html)

### NEXT-ENV
- URL: https://nextjs.org/docs/pages/guides/environment-variables
- Quote: "Non- NEXT_PUBLIC_ environment variables are only available in the Node.js environment, meaning they aren't accessible to the browser"
- Confirmed: 2026-10-07 (html)

### NEXT-TS-CONFIG
- URL: https://nextjs.org/docs/pages/api-reference/config/next-config-js/typescript
- Quote: "next.config.js Options: typescript"
- Confirmed: 2026-10-07 (html)

### NEXT-ESLINT-CONFIG
- URL: https://nextjs.org/docs/15/app/api-reference/config/next-config-js/eslint
- Quote: "When ESLint is detected in your project, Next.js fails your production build (next build) when errors are present."
- Confirmed: 2026-10-07 (html)

### NEXT-CSP
- URL: https://nextjs.org/docs/app/guides/content-security-policy
- Quote: "During rendering, Next.js parses the Content-Security-Policy header and extracts the nonce using the 'nonce-{value}' pattern."
- Confirmed: 2026-10-07 (html)

### NEXT-SECURITY-PROGRAM
- URL: https://nextjs.org/blog/next-security-release-program
- Quote: "As part of that process, today we are formalizing a security release program for Next.js."
- Confirmed: 2026-10-07 (html)

### REDUX-STYLE
- URL: https://redux.js.org/style-guide/
- Quote: "This is the official style guide for writing Redux code."
- Confirmed: 2026-10-07 (html)

### TESTING-PRINCIPLES
- URL: https://testing-library.com/docs/guiding-principles/
- Quote: "It should be generally useful for testing the application components in the way the user would use it."
- Confirmed: 2026-10-07 (html)

### TESTING-QUERIES
- URL: https://testing-library.com/docs/queries/about/#priority
- Quote: "Based on the Guiding Principles, your test should resemble how users interact with your code (component, page, etc.) as much as possible."
- Confirmed: 2026-10-07 (html)

### TS-STRICT
- URL: https://www.typescriptlang.org/tsconfig/#strict
- Quote: "The strict flag enables a wide range of type checking behavior that results in stronger guarantees of program correctness."
- Confirmed: 2026-10-07 (html)

### ARIA-APG
- URL: https://www.w3.org/WAI/ARIA/apg/
- Quote: "Learn how to make accessible web components and widgets with ARIA roles, states and properties and by implementing keyboard support."
- Confirmed: 2026-10-07 (html)

### ASVS5
- URL: https://github.com/OWASP/ASVS/tree/v5.0.0/5.0
- Quote: "ASVS/5.0 at v5.0.0"
- Confirmed: 2026-10-07 (html)

### OWASP-XSS
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- Quote: "Cross-Site Scripting (XSS) is a misnomer."
- Confirmed: 2026-10-07 (html)

### OWASP-HTML5
- URL: https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html
- Quote: "Do not store session identifiers in local storage as the data is always accessible by JavaScript."
- Confirmed: 2026-10-07 (html)

### OWASP-CLICKJACK
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
- Quote: "The use of this attribute should be considered as part of a defense-in-depth approach, and it should not be relied upon as the sole protective measure against Clickjacking."
- Confirmed: 2026-10-07 (html)

### MDN-XFO
- URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options
- Quote: "The HTTP X-Frame-Options response header can be used to indicate whether a browser should be allowed to render the document in a <frame>, <iframe>, <embed> or <object>."
- Confirmed: 2026-10-07 (html)

### MDN-FRAME-ANCESTORS
- URL: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors
- Quote: "Setting this directive to 'none' is similar to X-Frame-Options: deny (which is also supported in older browsers)."
- Confirmed: 2026-10-07 (html)

### MDN-POSTMESSAGE
- URL: https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
- Quote: "The window.postMessage() method safely enables cross-origin communication between Window objects;"
- Confirmed: 2026-10-07 (html)

### OAUTH-BROWSER-BCP
- URL: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps
- Quote: "OAuth 2.0 for Browser-Based Applications"
- Confirmed: 2026-10-07 (html)

### RFC8252
- URL: https://datatracker.ietf.org/doc/html/rfc8252
- Quote: "OAuth 2.0 for Native Apps"
- Confirmed: 2026-10-07 (html)

### RFC9700
- URL: https://www.rfc-editor.org/rfc/rfc9700
- Quote: "Best Current Practice for OAuth 2.0 Security"
- Confirmed: 2026-10-07 (html)

### PNPM-OVERRIDES
- URL: https://pnpm.io/settings/dependency-resolution#overrides
- Quote: "This field allows you to instruct pnpm to override any dependency in the dependency graph, including peer dependencies."
- Confirmed: 2026-10-07 (html)

### TURBOREPO
- URL: https://turborepo.dev/docs
- Quote: "Turborepo is the build system for coding agents."
- Confirmed: 2026-10-07 (html)

## Spring Boot pack

### BOOT-REF
- URL: https://docs.spring.io/spring-boot/
- Quote: "You can use Spring Boot to create Java applications that can be started by using java -jar or more traditional war deployments."
- Confirmed: 2026-10-07 (html)

### BOOT-SUPPORT
- URL: https://spring.io/projects/spring-boot#support
- Quote: "Learn more about Day 0 access to security patches via Enterprise support."
- Confirmed: 2026-10-07 (html)

### MVC-ERRORS
- URL: https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-exceptionhandler.html
- Quote: "Support for @ExceptionHandler methods in Spring MVC is built on the DispatcherServlet level, HandlerExceptionResolver mechanism."
- Confirmed: 2026-10-07 (html)

### RFC9457
- URL: https://www.rfc-editor.org/rfc/rfc9457
- Quote: "Problem Details for HTTP APIs"
- Confirmed: 2026-10-07 (html)

### DI-CTOR
- URL: https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html
- Quote: "Since you can mix constructor-based and setter-based DI, it is a good rule of thumb to use constructors for mandatory dependencies and setter methods or configuration methods for optional dependencies."
- Confirmed: 2026-10-07 (html)

### SEC-OAUTH2
- URL: https://docs.spring.io/spring-security/reference/servlet/oauth2/index.html
- Quote: "In most cases, Spring Security requires only minimal configuration to secure an application with OAuth2."
- Confirmed: 2026-10-07 (html)

### OPENFEIGN
- URL: https://docs.spring.io/spring-cloud-openfeign/reference/spring-cloud-openfeign.html
- Quote: "Spring Cloud adds support for Spring MVC annotations and for using the same HttpMessageConverters used by default in Spring Web."
- Confirmed: 2026-10-07 (html)

### ACTUATOR-ENDPOINTS
- URL: https://docs.spring.io/spring-boot/reference/actuator/endpoints.html
- Quote: "By default, only the health endpoint is exposed over HTTP and JMX."
- Confirmed: 2026-10-07 (html)

### EXTERNAL-CONFIG
- URL: https://docs.spring.io/spring-boot/reference/features/external-config.html
- Quote: "Externalized Configuration"
- Confirmed: 2026-10-07 (html)

### BOOT-TESTING
- URL: https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html
- Quote: "Testing Spring Boot Applications"
- Confirmed: 2026-10-07 (html)

### ORACLE-SECCODE
- URL: https://www.oracle.com/java/technologies/javase/seccodeguide.html
- Quote: "Secure Coding Guidelines for Java SE"
- Confirmed: 2026-10-07 (html)

### API-TOP10-2023
- URL: https://api-security.owasp.org/editions/2023/en/0x11-t10
- Quote: "OWASP Top 10 API Security Risks – 2023"
- Confirmed: 2026-10-07 (html)

### LOGGING-CS
- URL: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- Quote: "The remainder of this cheat sheet primarily discusses security event logging."
- Confirmed: 2026-10-07 (html)

### RFC7636
- URL: https://www.rfc-editor.org/rfc/rfc7636
- Quote: "Proof Key for Code Exchange by OAuth Public Clients"
- Confirmed: 2026-10-07 (html)

### OIDC-CORE
- URL: https://openid.net/specs/openid-connect-core-1_0.html
- Quote: "OpenID Connect 1.0 is a simple identity layer on top of the OAuth 2.0 protocol."
- Confirmed: 2026-10-07 (html)

### GRADLE-INSIGHT
- URL: https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html
- Quote: "Gradle provides the built-in dependencies task to render a dependency tree from the command line."
- Confirmed: 2026-10-07 (html)

### LICENSE-PLUGIN
- URL: https://github.com/hierynomus/license-gradle-plugin
- Quote: "Manage your license(s)"
- Confirmed: 2026-10-07 (html)
