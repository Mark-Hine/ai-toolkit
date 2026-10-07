---
verified: 2026-10-07
sources: inline
---

# Android source anchors

Each URL `official-docs.md` cites, pinned to its page and to a sentence from it. Use the registry to find a page and these anchors to quote it. Do not fetch a page to grade a rule. Volatile facts, such as store deadlines and latest versions, are still looked up when they are used. `tools/source_anchors.py` in the ai-toolkit repo confirms every quote against the live page and records the date, and that repo's `docs/source-anchors.md` describes the format.

Quotes are verbatim and short, and each names its page. Copyright stays with the source's owner.

### ARCH-GUIDE
- URL: https://developer.android.com/topic/architecture
- Quote: "Considering common architectural principles, design each application with at least two layers:"
- Confirmed: 2026-10-07 (html)

### ARCH-RECS
- URL: https://developer.android.com/topic/architecture/recommendations
- Quote: "Strongly recommended: Implement this practice unless it clashes fundamentally with your approach."
- Confirmed: 2026-10-07 (html)

### VM-EVENTS
- URL: https://developer.android.com/topic/architecture/ui-layer/events
- Quote: "UI events are actions that should be handled in the UI layer, either by the UI or by the ViewModel."
- Confirmed: 2026-10-07 (html)

### COROUTINES
- URL: https://developer.android.com/kotlin/coroutines/coroutines-best-practices
- Quote: "Don't hardcode Dispatchers when creating new coroutines or calling withContext."
- Quote: "Suspend functions should be main-safe, meaning they're safe to call from the main thread."
- Confirmed: 2026-10-07 (html)

### MODULARIZATION
- URL: https://developer.android.com/topic/modularization
- Quote: "Modularization is a practice of organizing a codebase into loosely coupled and self contained parts."
- Confirmed: 2026-10-07 (html)

### NAV-TYPESAFE
- URL: https://developer.android.com/guide/navigation/design/type-safety
- Quote: "You can use built-in type safe APIs to provide compile-time type safety for your navigation graph."
- Confirmed: 2026-10-07 (html)

### NAV3
- URL: https://developer.android.com/guide/navigation/navigation-3
- Quote: "Navigation 3 is a navigation library designed to work with Compose."
- Confirmed: 2026-10-07 (html)

### MIGRATION-GUIDE
- URL: https://developer.android.com/guide/navigation/navigation-3/migration-guide
- Quote: "This guide makes the following assumptions about you and your project:"
- Confirmed: 2026-10-07 (html)

### NAVIGATION3
- URL: https://developer.android.com/jetpack/androidx/releases/navigation3
- Quote: "Navigation3 is a new navigation library built specifically to handle Jetpack Compose in-app navigation."
- Confirmed: 2026-10-07 (html)

### DATASTORE
- URL: https://developer.android.com/topic/libraries/architecture/datastore
- Quote: "If you're using SharedPreferences to store data, consider migrating to DataStore instead."
- Confirmed: 2026-10-07 (html)

### SAFE-COLLECT
- URL: https://medium.com/androiddevelopers/a-safer-way-to-collect-flows-from-android-uis-23080b1f8bda
- Quote: none (offline)

### COMPOSE-STABILITY
- URL: https://developer.android.com/develop/ui/compose/performance/stability
- Quote: "Compose considers types to be either stable or unstable."
- Confirmed: 2026-10-07 (html)

### CUSTOM
- URL: https://developer.android.com/develop/ui/compose/designsystems/custom
- Quote: "To learn more about the lower-level constructs and APIs used by MaterialTheme and custom design systems, check out the Anatomy of a theme in Compose guide."
- Confirmed: 2026-10-07 (html)

### A11Y
- URL: https://developer.android.com/develop/ui/compose/accessibility
- Quote: "Accessibility in Jetpack Compose"
- Confirmed: 2026-10-07 (html)

### COMPOSE-API
- URL: https://github.com/androidx/androidx/blob/androidx-main/compose/docs/compose-api-guidelines.md
- Quote: "Element functions MUST NOT accept multiple Modifier parameters."
- Confirmed: 2026-10-07 (html)

### STRONG-SKIPPING
- URL: https://developer.android.com/develop/ui/compose/performance/stability/strongskipping
- Quote: "Strong Skipping is enabled by default in Kotlin 2.0.20."
- Confirmed: 2026-10-07 (html)

### STABILITY-FIX
- URL: https://developer.android.com/develop/ui/compose/performance/stability/fix
- Quote: "When working to fix issues with stability, you shouldn't attempt to make every composable skippable."
- Confirmed: 2026-10-07 (html)

### BANES-STABILITY
- URL: https://chrisbanes.me/posts/composable-metrics/
- Quote: "Restartable and skippable are Compose attributes for functions, whereas immutability & stability are attributes of object instances, specifically the objects which are passed to composable functions."
- Confirmed: 2026-10-07 (html)

### BOM-MAPPING
- URL: https://developer.android.com/develop/ui/compose/bom/bom-mapping
- Quote: "The URL on the Group Release Note column is updated depending on which BOM version is selected from the drop-down."
- Confirmed: 2026-10-07 (html)

### GRADLE-PLUGIN
- URL: https://developer.android.com/build/releases/gradle-plugin
- Quote: "The maximum API level that Android Gradle plugin 9.4 supports is API level 37."
- Confirmed: 2026-10-07 (html)

### AGP-BUILD
- URL: https://developer.android.com/build/optimize-your-build
- Quote: "The configuration cache lets Gradle record information about the build tasks graph and reuse it in subsequent builds, so Gradle doesn't have to reconfigure the whole build again."
- Confirmed: 2026-10-07 (html)

### MIGRATE-TO-CATALOGS
- URL: https://developer.android.com/build/migrate-to-catalogs
- Quote: "This page provides basic information about migrating your Android app to version catalogs."
- Confirmed: 2026-10-07 (html)

### ENABLE-APP-OPTIMIZATION
- URL: https://developer.android.com/topic/performance/app-optimization/enable-app-optimization
- Quote: "If you're using Bazel, you can integrate R8 into your build pipeline to shrink, obfuscate, and optimize your app."
- Confirmed: 2026-10-07 (html)

### GRADLE-DOCS
- URL: https://docs.gradle.org/current/userguide/best_practices_general.html
- Quote: "General Gradle Best Practices"
- Confirmed: 2026-10-07 (html)

### VERSION-CATALOGS
- URL: https://docs.gradle.org/current/userguide/version_catalogs.html
- Quote: "Version catalogs are conventionally declared using a libs.versions.toml file located in the gradle subdirectory of the root build."
- Confirmed: 2026-10-07 (html)

### KSP
- URL: https://kotlinlang.org/docs/ksp-overview.html
- Quote: "Kotlin Symbol Processing (KSP) is a source code generation framework for Kotlin."
- Confirmed: 2026-10-07 (html)

### RELEASES
- URL: https://kotlinlang.org/docs/releases.html
- Quote: "This page explains the Kotlin release cycle and the different types of releases we ship."
- Confirmed: 2026-10-07 (html)

### BASELINE-PROF
- URL: https://developer.android.com/topic/performance/baselineprofiles/overview
- Quote: "By shipping a Baseline Profile in an app or library, Android Runtime (ART) can optimize specified code paths through Ahead-of-Time (AOT) compilation, providing performance enhancements for every new user and every app update."
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

### SECURITY-CONFIG
- URL: https://developer.android.com/privacy-and-security/security-config
- Quote: "The Network Security Configuration feature lets you customize your app's network security settings in a safe, declarative configuration file without modifying app code."
- Confirmed: 2026-10-07 (html)

### INTENT-REDIRECTION
- URL: https://developer.android.com/privacy-and-security/risks/intent-redirection
- Quote: "Android 16 introduces a new API that allows apps to opt out of launch security protections."
- Confirmed: 2026-10-07 (html)

### OSV
- URL: https://osv.dev
- Quote: "An easy-to-use API is available to query for all known vulnerabilities by either a commit hash, or a package version."
- Confirmed: 2026-10-07 (html)

### TARGET-SDK
- URL: https://developer.android.com/google/play/requirements/target-sdk
- Quote: "When you upload an APK, it must meet Google Play's target API level requirements."
- Confirmed: 2026-10-07 (html)

### VERSIONS
- URL: https://developer.android.com/about/versions
- Quote: "Android 16 continues our mission of building a private and secure platform"
- Confirmed: 2026-10-07 (html)

### PLAY-INTEGRITY
- URL: https://developer.android.com/google/play/integrity/overview
- Quote: "The Play Integrity API helps you check that user actions and server requests are coming from your genuine app, installed by Google Play, running on a genuine and certified Android device."
- Confirmed: 2026-10-07 (html)

### PLAY-USERDATA
- URL: https://support.google.com/googleplay/android-developer/answer/13327111
- Quote: "If your app allows users to create an account from within your app, our User data policy requires that it must also allow users to request for their account to be deleted."
- Confirmed: 2026-10-07 (html)

### PLAY-VITALS
- URL: https://developer.android.com/google/play/vitals
- Quote: "Core vitals are the most important metrics in Android vitals, and affect the visibility of your app on Google Play."
- Confirmed: 2026-10-07 (html)

### PAGE-SIZES
- URL: https://developer.android.com/guide/practices/page-sizes
- Quote: "all apps targeting Android 15 (API level 35) and higher must support 16 KB memory page sizes on 64-bit devices on Google Play."
- Confirmed: 2026-10-07 (html)
