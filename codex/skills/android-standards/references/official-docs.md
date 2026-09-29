---
verified: 2026-09-29
sources: inline
---

# Official documentation registry

Canonical URLs. Prefer `android docs search "<term>"` first. Use these for web browsing fallback and for citing.

## Architecture
- Guide to app architecture: https://developer.android.com/topic/architecture
- Recommendations (Strongly Recommended / Recommended grades): https://developer.android.com/topic/architecture/recommendations
- UI layer events (state-based alternatives to event channels): https://developer.android.com/topic/architecture/ui-layer/events
- Coroutines best practices (inject dispatchers, main-safe data layer): https://developer.android.com/kotlin/coroutines/coroutines-best-practices
- Modularization: https://developer.android.com/topic/modularization and /topic/modularization/patterns
- Navigation 2 type-safe routes (`@Serializable` routes, `toRoute<T>()`): https://developer.android.com/guide/navigation/design/type-safety
- Navigation 3, a Compose-only back stack the app owns, with scenes for adaptive layouts: https://developer.android.com/guide/navigation/navigation-3 · migration guide (one atomic change, compileSdk 36, composable destinations, typed routes): https://developer.android.com/guide/navigation/navigation-3/migration-guide · releases, check for the current stable: https://developer.android.com/jetpack/androidx/releases/navigation3
- DataStore (no built-in encryption, so pair with Keystore/Tink for secrets): https://developer.android.com/topic/libraries/architecture/datastore
- Safer flow collection from UIs: https://medium.com/androiddevelopers/a-safer-way-to-collect-flows-from-android-uis-23080b1f8bda

## Compose
- Stability: https://developer.android.com/develop/ui/compose/performance/stability
- Custom design systems: https://developer.android.com/develop/ui/compose/designsystems/custom
- Accessibility: https://developer.android.com/develop/ui/compose/accessibility
- Compose API guidelines: https://github.com/androidx/androidx/blob/androidx-main/compose/docs/compose-api-guidelines.md
- Strong skipping (default from Kotlin 2.0.20, what it changes for unstable parameters and lambdas): https://developer.android.com/develop/ui/compose/performance/stability/strongskipping
- Fixing stability, and when not to bother: https://developer.android.com/develop/ui/compose/performance/stability/fix
- Composable metrics (Chris Banes, predates strong skipping): https://chrisbanes.me/posts/composable-metrics/
- Compose BOM to library version mapping: https://developer.android.com/develop/ui/compose/bom/bom-mapping

## Build
- AGP release notes: https://developer.android.com/build/releases/gradle-plugin
- AGP and Gradle/JDK compatibility table: https://developer.android.com/build/releases/gradle-plugin#compatibility
- Optimize your build: https://developer.android.com/build/optimize-your-build
- Migrate to version catalogs: https://developer.android.com/build/migrate-to-catalogs
- Shrink, obfuscate, optimize (R8): https://developer.android.com/build/shrink-code
- Gradle best practices: https://docs.gradle.org/current/userguide/best_practices_general.html
- Gradle version catalogs: https://docs.gradle.org/current/userguide/version_catalogs.html
- KSP overview and Kotlin compatibility: https://kotlinlang.org/docs/ksp-overview.html
- Kotlin releases: https://kotlinlang.org/docs/releases.html
- Baseline profiles: https://developer.android.com/topic/performance/baselineprofiles/overview

## Security
- OWASP MASVS v2.1.0: https://mas.owasp.org/MASVS/
- OWASP MASTG (cert pinning MASTG-KNOW-0015, missing pinning MASTG-TEST-0244): https://mas.owasp.org/MASTG/
- OWASP Pinning Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
- OWASP Mobile Top 10 2024: https://owasp.org/www-project-mobile-top-10/
- Network security config: https://developer.android.com/privacy-and-security/security-config
- Intent security: https://developer.android.com/privacy-and-security/risks/intent-redirection
- OSV vulnerability database (purl batch query): https://osv.dev

## Play and platform
- Target API level requirements: https://developer.android.com/google/play/requirements/target-sdk
- Behaviour changes by release (check the page for the current target): https://developer.android.com/about/versions
- Play Integrity: https://developer.android.com/google/play/integrity/overview
- Play User Data policy (account deletion): https://support.google.com/googleplay/android-developer/answer/13327111
- App vitals: https://developer.android.com/topic/performance/vitals
- 16 KB page size support: https://developer.android.com/guide/practices/page-sizes
