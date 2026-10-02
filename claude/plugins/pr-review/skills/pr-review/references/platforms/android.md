---
verified: 2026-09-29
sources: inline
---

# Platform pack: Android

Grading criteria for reviewing an Android/Kotlin change. Load this pack when the repo is Android.
It supplies the standards vocabulary that findings cite and the recipes that turn a suspicion into
evidence. The platform-neutral review rules, which cover volatile facts, `Unverified` grading, pragmatism
guardrails and main-safety ownership, live in [`../protocol.md`](../protocol.md) §13 to §16. Their
extensions, which cover root cause not symptom, verification criteria, SHA ancestry and debug-variant
exclusion, live in §17 to §20. All of them apply here too.

For Kotlin changes, also load the [Kotlin language reference](../languages/kotlin.md). It supplies cross-platform domain modeling, boundary and compatibility criteria; this pack adds platform requirements.

## Standards-basis block

Paste this into the review's Standards basis section, then append the verification sentence
(template.md):

```markdown
Findings are graded against the published Android engineering guidance, cited per finding:
**[ARCH-RECS]** Architecture recommendations, https://developer.android.com/topic/architecture/recommendations (SR = strongly recommended, R = recommended) · **[ARCH-GUIDE]** https://developer.android.com/topic/architecture · **[COROUTINES]** Coroutines best practices, https://developer.android.com/kotlin/coroutines/coroutines-best-practices · **[COMPOSE-API]** Compose API guidelines, https://github.com/androidx/androidx/blob/androidx-main/compose/docs/compose-api-guidelines.md · **[COMPOSE-STABILITY]** https://developer.android.com/develop/ui/compose/performance/stability · **[NAV-TYPESAFE]** https://developer.android.com/guide/navigation/design/type-safety · **[EUM-LOADING]** initial-load guidance (cold flow + `stateIn`, not `LaunchedEffect`), https://proandroiddev.com/loading-initial-data-in-launchedeffect-vs-viewmodel-f1747c20ce62 · **[M3-DESIGN]** Material Design 3, https://m3.material.io · **[UI-STANDARDS]** tiered UI design rules, T2 graded Nit · **[WCAG22]** WCAG 2.2 AA · **OWASP MASVS** v2.1.0.
```

## Architecture: official guidance + NowInAndroid

Graded per `[ARCH-RECS]` (**SR** = strongly recommended, **R** = recommended). Verify each in
source, don't assume:

- **Layering (SR):** clearly defined UI layer and data layer. The domain layer is optional (R for big
  apps). Repositories exist **even for a single data source** (SR). Read the actual package/module
  structure and one repository.
- **UI never touches data sources directly (SR):** no DB/DataStore/SharedPreferences/Firebase
  access from Activities/Fragments/Composables. Grep UI-layer packages for data-source imports and
  quote offenders.
- **Unidirectional data flow (SR):** state flows down, events flow up. Each data type has one
  Single Source of Truth that alone mutates it and exposes immutable types.
- **Single-activity app (SR):** count `<activity>` entries in the manifest. Multiple activities is
  a graded finding only if navigation is actually fragmented across them.
- **Navigation route type-safety ([NAV-TYPESAFE]):** open the nav graph and grade how routes **and
  args** are typed. String routes / string-templated paths whose args come back via
  `NavBackStackEntry` with manual `toInt()`/`toBoolean()` casting are a graded finding. The current
  guidance is type-safe destinations, meaning `@Serializable` route objects/data classes + `toRoute<T>()`
  (stable since Navigation 2.8.0). Navigation 3 back stacks of typed route keys satisfy this directly, and Navigation 2
  is not a finding by itself. Migration is its own ticket ([NAV3]). This applies equally to a **home-grown route DSL**: grade whether
  *it* is typed and compile-time checked, not whether it uses the official API. Confirm the API's
  current state at review time (protocol.md §13).
- **Model per layer (R, complex apps):** network/DAO models mapped to simpler layer-local models
  rather than leaked to UI.
- **Offline-first ([NIA]):** local DB as SSOT with remote sync (WorkManager/backoff). This is a benchmark,
  not mandatory. Note where this repo sits.
- **Framework-free lower layers:** ViewModels and below hold no `Context`/`Activity`/UI classes
  (SR) and no `AndroidViewModel` (R).

> **PRAGMATISM GUARDRAILS, DO NOT FLAG ([NIA-1273]):** NowInAndroid's maintainers explicitly
> defend these as correct, pragmatic choices. Do **not** raise findings for:
> - ViewModels calling repositories directly (no mandatory use-case indirection)
> - use cases without an interface each (interface-per-use-case is Clean-Architecture dogma, not
>   official guidance)
> - a missing/optional domain layer
> - dependency inversion applied at module/object boundaries rather than per architectural layer
> - a consistently applied one-off VM→UI event pipeline, with a buffered channel, lifecycle-aware
>   single-consumer collection and ephemeral effects only, despite the `[ARCH-RECS]` SR (see the
>   events bullet under *State, Compose & coroutines* for what to grade instead).
> Flag the *absence of layering discipline*, not the absence of Clean-Architecture ceremony.

## State, Compose & coroutines

**UI-state exposure ([ARCH-RECS], [EUM-LOADING]):**
- Single `uiState` property per screen, a `StateFlow` built with
  `stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), initial)` (R). The stop timeout keeps
  the upstream alive through a configuration change, so the screen does not refetch.
- **No asynchronous work launched from ViewModel `init {}` or the constructor, and no non-idempotent load from
  `LaunchedEffect` ([STATE-PRODUCTION], [EUM-LOADING], [HOUSE]).** Both are graded findings. The official alternatives are a cold flow
  with `stateIn` or an idempotent `initialize()` the UI calls. A `LaunchedEffect` that calls a non-idempotent load runs
  again when the composable re-enters composition. This is a house standard kept on purpose.
- Collect with `collectAsStateWithLifecycle()`, not `collectAsState()` (SR).
- **One-off VM→UI events are CONTESTED. Do not grade the pattern itself as a violation.**
  [ARCH-RECS] badges "Do not send events from the ViewModel to the UI" **SR**, and that is worth
  telling the author. But SR is defined there as *"implement this practice unless it clashes
  fundamentally with your approach"*, and [EVENT-ANTIPATTERNS], the sole authority behind the row,
  calls its own position *"opinionated"* and closes *"treat this as a guideline and adapt it to your
  requirements as needed"*. It also concedes the mitigation (`Dispatchers.Main.immediate`), rejecting
  it only because no lint check enforces it, which is a tooling gap, not a correctness defect. The ecosystem
  never converged: [KTX-2886], the request for a primitive that would have settled it, is open since
  2021 with the coroutines lead's `Main.immediate` solution as its top answer, and actively-maintained
  MVI frameworks ship the pattern as a first-class API ([ORBIT-SE] caches side effects when nothing is
  listening and collects them lifecycle-aware. MVIKotlin `Label`, FlowMVI `Action` and Ballast work likewise).
  Google's own samples ([NIA], architecture-samples, socialite) contain no VM→UI event channel at all.
  Cite that as the **exemplar**, never as proof of a defect.
  **What IS reviewable here.** Grade these, not the channel's existence:
  - **Collection that isn't lifecycle-aware**, meaning a bare `collect` in `lifecycleScope.launch`, or a
    `LaunchedEffect` without `repeatOnLifecycle`/`flowWithLifecycle`. `LaunchedEffect` is scoped to the
    **composition, not the lifecycle**, and Compose keeps the composition alive while STOPPED, so the
    effect body runs in the background: `startActivity` is blocked outright on Android 10+, and
    navigation lands mid-transition. This is the real bug and it has no defenders. Even
    [EVENT-ANTIPATTERNS]' own straw-man example is lifecycle-gated, and Google's recommended
    state-based navigation still wraps collection in `.flowWithLifecycle(lifecycle)` ([SAFE-COLLECT]).
  - **`MutableSharedFlow(replay = 0)` for events**, which is actually lossy when nothing is collecting.
    `Channel(BUFFERED)` + `receiveAsFlow()` is **not**. Keep the two distinct rather than lumping them.
  - **More than one collector on a single `Channel`.** `receiveAsFlow()` is single-consumer, so
    collectors split the stream arbitrarily.
  - **Events carrying anything that must survive process death** (payment result, auth outcome). That
    is state, and here the SR is simply right: *"State is, events happen."* A `Channel` cannot survive
    process death. `SavedStateHandle` can.
  - **Imperative UI commands** (`showDialog()`, `showTabletSheet()`) rather than semantic facts
    (`PaymentCompleted`). This is the least contested of the three antipatterns, since the right rendering
    differs by form factor.
  - Sending/collecting off `Dispatchers.Main.immediate` is worth an **N**, citing [KTX-2886].
- ViewModels at screen level only. Reusable components use plain state-holder classes (SR). State
  is hoisted, and composables are kept stateless where practical ([BANES-STABILITY]).

**Compose design system, correctness audit ([JETSNACK], [STREAM-THEME], [EFFECTIVE-COMPOSE], [COMPOSE-API]):**
Open the `:DesignSystem` module (or equivalent) and grade its *correctness*. Presence of a design-system
module is not a pass. It's the highest-value place to get theming, stability, and a11y right (every
screen consumes it). Check:
- **Token propagation:** tokens provided as **`CompositionLocal` snapshot state**
  (`staticCompositionLocalOf` + `CompositionLocalProvider`, JetSnack / stream-video-android pattern) with
  a `Theme.x` accessor + sensible default. **Flag top-level `val x = Manager.y` tokens or a global mutable
  theme singleton captured at class-load**, because a brand/theme switch neither propagates nor recomposes. Grep
  for hardcoded `Color(0xFF...)` / literal `dp`/`sp` outside the theme package and quote offenders.
- **App-level `Theme` wrapper:** a `<App>Theme { }` composable wraps `setContent`, or else components reading
  `MaterialTheme.*` fall through to **stock Material defaults**, not the brand. Note Material 2 vs 3 and
  **dark-theme support** (`darkColors`/`darkColorScheme`, `isSystemInDarkTheme`).
- **Component API guidelines ([COMPOSE-API], [EFFECTIVE-COMPOSE]):** a single `modifier: Modifier =
  Modifier` as the **first optional parameter** (not a field inside a `State` class), applied to the
  **topmost layout node only** and **not reused** across sibling/nested nodes, **slot APIs**
  (`content: @Composable () -> Unit`) over boolean/enum flags, **state hoisting** (no un-hoisted internal
  state), a composable that **emits content XOR returns a value**, and consolidate 5+ styling params into one
  `@Immutable` **style class**.
- **Component stability ([STRONG-SKIPPING], [STABILITY-FIX], [BANES-STABILITY]):** read the Kotlin version first. From
  2.0.20, strong skipping is on by default, so an unstable parameter does not make a composable non-skippable and a
  missing `@Immutable`, `@Stable` or immutable collection is not a finding by itself. Grade a measured problem, such as a
  source that emits new but equal instances every update. Below 2.0.20, grade non-skippable components that take an
  unstable state class, confirmed by compiler metrics.
- **Preview safety:** components render in `@Preview`. Network/image/IO is guarded by `LocalInspectionMode`
  fallbacks. Grade any component/preview catalog (e.g. Showkase) for *coverage*, not mere existence.
- **Component-level accessibility (see Accessibility below):** components bake in correct semantics:
  `Role`/`stateDescription` on toggleable/selectable, a `contentDescription` contract on icon/image
  slots, and `minimumInteractiveComponentSize`/48dp touch targets. A11y is won or lost in the DS.
- Where installed, invoke `compose-slot-api-pattern`, `compose-modifier-and-layout-style`,
  `compose-stability-diagnostics` for the matching sub-checks rather than re-deriving them.

**Compose stability & recomposition ([BANES-STABILITY]):**
- Method, not vibes: run Compose compiler metrics on a **release** build, filter
  restartable-but-not-skippable composables, look for parameters whose instances change on every
  emission, and check for screen-local UI models rather than data-layer types in
  composable signatures. Profile first (JankStats/Perfetto). Recomposition findings without a
  metric or quoted unstable parameter are `Unverified`.

**UI design ([UI-STANDARDS], [M3-DESIGN], [WCAG22]):**
- Grade UI against the tiered design rules, the `design-standards.md` file the toolkit installs (`~/.claude/rules/` on Claude Code, `guidance/` on Codex and Antigravity). The `design-standards` skill carries the sources, rationale and APIs. Cite the rule ID and source key in each finding. T1 breaches grade Blocker or Major by user impact, T2 breaches grade Nit unless the project opts the rule in. Android specifics are AND-1 to AND-6 (colour roles, edge to edge, five window size classes, orientation at target 36, motion scheme, predictive back), with A11Y-3 for the 48 dp target and A11Y-7 for 200% font scale.

**Coroutines & Flow ([ARCH-RECS], [ARCH-GUIDE], [NIA], [COROUTINES]):**
- Layers communicate via coroutines/Flow (SR). ViewModels receive Flows and launch work in
  `viewModelScope` suspend calls (SR).
- **Main-safety is the data layer's job, not the ViewModel's** ([COROUTINES]): main-safety belongs
  to whichever class does the blocking work. In practice that is the repository/data-source **suspend
  functions**, which move work off the main thread with `withContext(injectedDispatcher)` so callers
  don't have to. A ViewModel launches in `viewModelScope` (= `Dispatchers.Main.immediate`) and calls
  already-main-safe suspend functions. **`withContext(Dispatchers.IO/Default)` inside a ViewModel is
  a smell** that main-safety leaked up from the data layer. **Don't hardcode `Dispatchers`**. Inject
  them (testability). Note: an *injected* IO dispatcher used in a VM is not itself the defect (that
  satisfies "don't hardcode"). The finding is doing main-safety in the VM at all rather than in the
  data layer. Grade it as a minor style issue, not a bug (per the pragmatism guardrails above). Also
  check for `runBlocking`, stored `CoroutineScope`s, `GlobalScope`, and broad `try/catch` around
  suspend calls.
- Data layer exposes streams (NIA convention `get*Stream()` / `observe*()`) rather than one-shot
  snapshots where the UI needs updates.

**Testing ([ARCH-RECS], all SR unless noted):** unit tests for ViewModels (incl. Flows),
repositories, and data sources, plus UI navigation tests. **Prefer fakes over mocks** (`Fake*` naming is
optional). Feed test-coverage findings with these expectations.


## Security: MASVS v2.1.0 control map (+ Top 10 2024 cross-map)

**Framework ([MASVS], [MASTG]):** OWASP MASVS v2.1.0 is the verification standard (8 groups, 24
controls). MASTG supplies atomic tests (`MASTG-TEST-xxxx`). Cite test IDs
in Refs where known. **Declare the target MAS profile in the review**: L1 = baseline for all apps,
**L2 = defense-in-depth for sensitive-data apps (finance/health, typically the right target
here)**, and R = resilience add-on where the threat model warrants it. Grade each control
Pass/Fail/Partial/Unverified with `file:line` evidence.

| Control | What it requires | Static-check recipe (open & quote) |
|---|---|---|
| STORAGE-1 | Sensitive data stored securely | Where tokens/PII actually live (plain `SharedPreferences`/files/Room = Fail, and external storage writes). Grade against the **current** recommended at-rest approach. **Verify at review time (protocol.md §13). `EncryptedSharedPreferences`/`security-crypto` is deprecated, so its use is a graded finding, not a pass**. The current guidance is Keystore-backed DataStore + Tink (confirm). DataStore has no built-in encryption, so it is the non-secret store paired with Keystore/Tink. Refs: MASVS-STORAGE-1 · [DATASTORE] · [MASVS] |
| STORAGE-2 | No sensitive-data leakage | `android:allowBackup` + `data_extraction_rules.xml`/`fullBackupContent`, `Log.*`/`Timber`/`println` with sensitive vars, `FLAG_SECURE` on sensitive screens, and **in-memory residency of secrets**. PIN/password/key material held in an immutable `String` stays in the heap until GC and is recoverable from a dump. The target is `CharArray`/`ByteArray` zero-filled in a `finally` immediately after use. Grade the **whole path** (input field → repository → crypto call), not one variable. Where a Compose `TextField`/`String` boundary makes end-to-end wiping impossible, grade the **residency window** and say so. Never give a clean pass, and never propose a fix that can't be built |
| CRYPTO-1 | Strong, correctly-used crypto | `Cipher.getInstance` args (ECB/DES/RC4/NoPadding), MD5/SHA-1 for security, `Random()` vs `SecureRandom`, static IVs |
| CRYPTO-2 | Sound key management | Hardcoded keys/secrets (BuildConfig, constants, high-entropy strings), `AndroidKeyStore` usage and `setUserAuthenticationRequired` |
| AUTH-1 | Secure auth/authz protocols | Token issuance/refresh/rotation wiring (pairs with token-refresh trace) and session invalidation on logout |
| AUTH-2 | Secure local authentication | `BiometricPrompt` bound to a `CryptoObject` (not a bare boolean callback), deprecated `FingerprintManager` and PIN hashing |
| AUTH-3 | Extra auth for sensitive ops | Step-up auth before payments/credential changes. Trace one sensitive flow |
| NETWORK-1 | All traffic secured | `android:usesCleartextTraffic` and `network_security_config.xml` (`cleartextTrafficPermitted`, user-cert trust anchors, debug-overrides) + manifest wiring. Reconcile vs hosts the app actually calls |
| NETWORK-2 | Identity pinning (done safely) + request integrity for owned endpoints | **Grade in context. Pinning is optional defense-in-depth, not mandatory. Don't reward mere presence or punish mere absence.** _Present_ (`<pin-set>` / OkHttp `CertificatePinner`): verify it covers the **real hosts the app actually calls** (pinning hosts never called = Fail/theatre), has **≥1 backup pin**, and an **`<pin-set expiration>` or remotely-updatable path** so rotation can't brick installs without a store release. An empty `checkServerTrusted` in a custom `X509TrustManager` = **Critical**. _Absent_: **not an automatic Fail**. OWASP/Google now often discourage pinning (CT vs downtime risk, and it breaks under corporate TLS-inspection). Verify current stance at review time (protocol.md §13). Also: are **money-movement / credential-change requests signed or attested beyond a bearer token**? Put the safe-rotation implementation (SPKI, hybrid, signed remote pins + kill-switch, per [PINNING]) in the finding's PR comment and `verify_fixed_when`. Refs: MASVS-NETWORK-2 · MASTG-KNOW-0015 · [PINNING] · [MASVS] |
| PLATFORM-1 | Secure IPC | `android:exported` on all components, provider exports, protecting `android:permission`, mutable `PendingIntent` without `FLAG_IMMUTABLE`, intent-redirection (`getIntent()` extras forwarded unvalidated) |
| PLATFORM-2 | Secure WebViews | `setJavaScriptEnabled`, `addJavascriptInterface`, `setAllowFileAccess*`/`UniversalAccess`, `loadUrl` with untrusted input, `setWebContentsDebuggingEnabled` in release |
| PLATFORM-3 | Secure UI usage | **Keyboard cache:** Compose `KeyboardOptions(keyboardType = KeyboardType.Password/NumberPassword, autoCorrectEnabled = false)` and View `InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS` / `IME_FLAG_NO_PERSONALIZED_LEARNING`. Name the sensitive fields you checked and their actual state. **Overlay / tapjacking:** `filterTouchesWhenObscured` **and** `Window.setHideOverlayWindows(true)` (API 31+) on windows rendering balances/OTP/PIN. Sensitive data in `AndroidManifest` task snapshots. Screen capture lives in STORAGE-2 (`FLAG_SECURE`), so cross-reference rather than re-checking |
| CODE-1 | Up-to-date platform version | `minSdk`/`targetSdk`. **Look up the current Play target-API requirement + effective date at review time (protocol.md §13), don't assert from memory**. Grade `targetSdk` below it as a **hard Play-update gate** (dated finding, e.g. "targetSdk N required for Play updates from <date>"), not merely "behind". Feeds currency findings |
| CODE-2 | Enforced app updates / incident response | In-app update / **force-update** mechanism, and a remote **feature kill-switch** for production incident response (remote-config-gated). For a regulated/fintech app treat absence as a graded finding, and check the mechanism is wired, not just declared. A **certificate-pinning kill-switch** is a specific case of this (see NETWORK-2). It must be **signed/authenticated** (an unauthenticated toggle is a one-switch bypass) and fail back to default PKI trust + CT, never to disabled TLS validation |
| CODE-3 | No known-vulnerable components | Dependency versions vs known CVEs, and SCA tooling in CI (dependency-check/Snyk/Renovate) |
| CODE-4 | Input validation | SQL concatenation (`rawQuery`/`execSQL` + `+`), deep-link/`Uri` param handling, unsafe deserialization |
| RESILIENCE-1 | Platform-integrity validation | Device attestation / root-tamper wiring. Read it, don't grep-match. **SafetyNet Attestation is decommissioned (verify current status, protocol.md §13) → any reliance on it is broken, not merely dated. The current mechanism is the Play Integrity API.** Also check verdicts are **enforced server-side**, not client-only (trivially bypassable). Refs: MASVS-RESILIENCE-1 · [PLAY-INTEGRITY] · [MASVS] |
| RESILIENCE-2 | Anti-tampering | Signature/integrity checks and R8 `minifyEnabled` on release |
| RESILIENCE-3 | Anti-static-analysis | Obfuscation config (`proguard-rules.pro` keep-rule breadth), string/asset protection |
| RESILIENCE-4 | Anti-dynamic-analysis | Debugger/emulator/hook detection, `android:debuggable` and `StrictMode` debug-only |
| PRIVACY-1 | Minimal data/resource access | `<uses-permission>` audit of dangerous permissions vs actual feature need, and `QUERY_ALL_PACKAGES` |
| PRIVACY-2 | Prevent user identification | Device identifiers (`ANDROID_ID`, IMEI, MAC, ad ID) collection & linkage |
| PRIVACY-3 | Transparency | Data-collection disclosure vs actual SDK behavior (analytics/marketing SDKs found in the dependency inventory) |
| PRIVACY-4 | User data control | Deletion/opt-out paths for collected data |

**OWASP Mobile Top 10 (2024) cross-map** (check owasp.org for a newer edition before citing it. The Top 10 is the
awareness list, MASVS is the verification standard). Emit as
a compact table pointing each M-risk at the MASVS rows above rather than re-checking:
M1 Credentials→CRYPTO-2/AUTH-1 · M2 Supply Chain→CODE-3 · M3 Auth/Authz→AUTH-1/2/3 ·
M4 Input/Output Validation→CODE-4 · M5 Insecure Communication→NETWORK-1/2 ·
M6 Privacy→PRIVACY-1..4 · M7 Binary Protections→RESILIENCE-1..4 ·
M8 Misconfiguration→PLATFORM-1/STORAGE-2 · M9 Data Storage→STORAGE-1/2 · M10 Crypto→CRYPTO-1/2.

## Accessibility

- **Accessibility ([A11Y]).** A static pass
  can't replace TalkBack, but grade these against the code (a regulated/finance app faces WCAG-grade
  expectations). **Touch targets:** interactive components ≥ 48dp / `Modifier.minimumInteractiveComponentSize()`
  (flag icon-only buttons without it). **`contentDescription` contract:** non-null on meaningful
  icons/images, `null` only for decorative (quote the ratio + offenders on clickable elements).
  **Semantics:** `Role` + `stateDescription` on toggleable/selectable, `mergeDescendants`/
  `clearAndSetSemantics` on composite rows, `heading()`/`paneTitle` for structure, `onClickLabel` on
  clickables whose visible text doesn't describe the action. **Font scaling:** text in `sp` (not `dp`),
  and `maxLines`+ellipsis on scalable text that truncates at large scale. **Custom actions** for
  gesture-only interactions. Anything needing a device pass goes under "Unverified (needs a trace)" with
  the TalkBack / Accessibility-Scanner run that would confirm it.

## Source registry (canonical URLs for Refs lines)

| Key | Source |
|---|---|
| [ARCH-GUIDE] | https://developer.android.com/topic/architecture |
| [ARCH-RECS] | https://developer.android.com/topic/architecture/recommendations |
| [MODULARIZATION] | https://developer.android.com/topic/modularization (+ /patterns) |
| [NAV-TYPESAFE] | https://developer.android.com/guide/navigation/design/type-safety (+ /type-safe-destinations), `@Serializable` routes + `toRoute<T>()`, stable since Navigation 2.8.0 |
| [NIA] | https://github.com/android/nowinandroid (ArchitectureLearningJourney.md, ModularizationLearningJourney.md) |
| [NIA-1273] | https://github.com/android/nowinandroid/discussions/1273 |
| [JETSNACK] | https://github.com/android/compose-samples/tree/main/Jetsnack + https://developer.android.com/develop/ui/compose/designsystems/custom |
| [STREAM-THEME] | https://getstream.io/blog/designing-effective-compose/ (stream-video-android CompositionLocal theming) |
| [EFFECTIVE-COMPOSE] | https://getstream.io/blog/designing-effective-compose/ + https://getstream.io/blog/jetpack-compose-guidelines/ |
| [COMPOSE-API] | https://github.com/androidx/androidx/blob/androidx-main/compose/docs/compose-api-guidelines.md |
| [COMPOSE-STABILITY] | https://getstream.io/blog/jetpack-compose-stability/ + https://developer.android.com/develop/ui/compose/performance/stability |
| [A11Y] | https://developer.android.com/develop/ui/compose/accessibility (+ /semantics, /testing) |
| [EUM-LOADING] | https://proandroiddev.com/loading-initial-data-in-launchedeffect-vs-viewmodel-f1747c20ce62, a community post that supports the cold-flow form as a preference |
| [STATE-PRODUCTION] | https://developer.android.com/topic/architecture/ui-layer/state-production. Official: do not launch asynchronous operations in the init block. Use a cold flow with `stateIn` or an idempotent `initialize()` |
| [HOUSE] | A deliberate house standard of this toolkit (see the `android-kit` standards references: `ui-events.md`, `jetsnack.md`, `nia.md`). Graded as a finding by design |
| [STRONG-SKIPPING] | https://developer.android.com/develop/ui/compose/performance/stability/strongskipping, default from Kotlin 2.0.20 |
| [STABILITY-FIX] | https://developer.android.com/develop/ui/compose/performance/stability/fix, "you shouldn't attempt to make every composable skippable" |
| [NAV3] | https://developer.android.com/guide/navigation/navigation-3 · migration: https://developer.android.com/guide/navigation/navigation-3/migration-guide |
| [UI-STANDARDS] | The toolkit's `design-standards.md` rule file (shared/guidance/design-standards.md in ai-toolkit), tiered rules with IDs. Sources per key in the design-standards skill, `references/sources.md` |
| [M3-DESIGN] | https://m3.material.io. Cite the page per finding (colour roles, grids and spacing, type scale, motion) |
| [WCAG22] | https://www.w3.org/TR/WCAG22/ (W3C Recommendation, 2024-12-12), cite the success criterion per finding |
| [VM-EVENTS] | https://developer.android.com/topic/architecture/ui-layer/events, the state-based alternatives (`userMessage` + `userMessageShown()`, `flowWithLifecycle`, `dropUnlessResumed`) |
| [EVENT-ANTIPATTERNS] | https://manuelvivo.dev/viewmodel-events-antipatterns (2022-06-01), the authority behind the SR row. Note its own "opinionated" framing, the "adapt it to your requirements" disclaimer, and the conceded `Dispatchers.Main.immediate` mitigation |
| [KTX-2886] | https://github.com/Kotlin/kotlinx.coroutines/issues/2886, Elizarov's `Main.immediate` solution (top-voted). It is **open since Aug 2021**, i.e. the ecosystem never settled this |
| [ORBIT-SE] | https://github.com/orbit-mvi/orbit-mvi/blob/main/website/docs/Core/index.md (+ /Compose/index.md), side effects cached when no observer is listening, collected lifecycle-aware |
| [SAFE-COLLECT] | https://medium.com/androiddevelopers/a-safer-way-to-collect-flows-from-android-uis-23080b1f8bda. Channel-backed flows are not safe to collect without lifecycle awareness |
| [COROUTINES] | https://developer.android.com/kotlin/coroutines/coroutines-best-practices. Main-safety is the data layer's job. Inject dispatchers, and avoid GlobalScope/hardcoded Dispatchers |
| [BANES-STABILITY] | https://chrisbanes.me/posts/composable-metrics/ |
| [PLAY-INTEGRITY] | https://developer.android.com/google/play/integrity/overview, device/app/account integrity verdicts (replaces the decommissioned SafetyNet Attestation). Enforce server-side |
| [DATASTORE] | https://developer.android.com/topic/libraries/architecture/datastore, modern replacement for SharedPreferences. It has **no built-in encryption**, so pair with Android Keystore/Tink for secrets (STORAGE-1) |
| [MASVS] | https://mas.owasp.org/MASVS/ (v2.1.0) |
| [MASTG] | https://mas.owasp.org/MASTG/ (cite the version shown on the site at review time), incl. MASTG-KNOW-0015 (cert pinning), MASTG-TEST-0244 (missing pinning, Android) |
| [PINNING] | https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html, OWASP Pinning Cheat Sheet (public-key/SPKI pins, backup pins, expiration safety-valve, when NOT to pin) |
| [TOP10-2024] | https://owasp.org/projects/mobile-top-10 |
| [GRADLE-DOCS] | https://docs.gradle.org/current/userguide/best_practices_general.html (+ version_catalogs.html, configuration_cache.html) |
| [AGP-BUILD] | https://developer.android.com/build/optimize-your-build (+ /migrate-to-catalogs, /shrink-code) |
| [BASELINE-PROF] | https://developer.android.com/topic/performance/baselineprofiles/overview |
| [KSP] | https://kotlinlang.org/docs/ksp-overview.html |

<!-- Source links. Keep in sync with the table above (primary URL per key) so [KEY] references
     render as links wherever this pack's content is pasted -->
[ARCH-GUIDE]: https://developer.android.com/topic/architecture
[ARCH-RECS]: https://developer.android.com/topic/architecture/recommendations
[MODULARIZATION]: https://developer.android.com/topic/modularization
[NAV-TYPESAFE]: https://developer.android.com/guide/navigation/design/type-safety
[NIA]: https://github.com/android/nowinandroid
[NIA-1273]: https://github.com/android/nowinandroid/discussions/1273
[JETSNACK]: https://github.com/android/compose-samples/tree/main/Jetsnack
[STREAM-THEME]: https://getstream.io/blog/designing-effective-compose/
[EFFECTIVE-COMPOSE]: https://getstream.io/blog/designing-effective-compose/
[COMPOSE-API]: https://github.com/androidx/androidx/blob/androidx-main/compose/docs/compose-api-guidelines.md
[COMPOSE-STABILITY]: https://developer.android.com/develop/ui/compose/performance/stability
[A11Y]: https://developer.android.com/develop/ui/compose/accessibility
[EUM-LOADING]: https://proandroiddev.com/loading-initial-data-in-launchedeffect-vs-viewmodel-f1747c20ce62
[STATE-PRODUCTION]: https://developer.android.com/topic/architecture/ui-layer/state-production
[HOUSE]: https://github.com/Mark-Hine/ai-toolkit/tree/main/claude/plugins/android-kit/skills/standards/references
[STRONG-SKIPPING]: https://developer.android.com/develop/ui/compose/performance/stability/strongskipping
[STABILITY-FIX]: https://developer.android.com/develop/ui/compose/performance/stability/fix
[NAV3]: https://developer.android.com/guide/navigation/navigation-3
[UI-STANDARDS]: https://github.com/Mark-Hine/ai-toolkit/blob/main/shared/guidance/design-standards.md
[M3-DESIGN]: https://m3.material.io
[WCAG22]: https://www.w3.org/TR/WCAG22/
[VM-EVENTS]: https://developer.android.com/topic/architecture/ui-layer/events
[EVENT-ANTIPATTERNS]: https://manuelvivo.dev/viewmodel-events-antipatterns
[KTX-2886]: https://github.com/Kotlin/kotlinx.coroutines/issues/2886
[ORBIT-SE]: https://github.com/orbit-mvi/orbit-mvi/blob/main/website/docs/Core/index.md
[SAFE-COLLECT]: https://medium.com/androiddevelopers/a-safer-way-to-collect-flows-from-android-uis-23080b1f8bda
[COROUTINES]: https://developer.android.com/kotlin/coroutines/coroutines-best-practices
[BANES-STABILITY]: https://chrisbanes.me/posts/composable-metrics/
[PLAY-INTEGRITY]: https://developer.android.com/google/play/integrity/overview
[DATASTORE]: https://developer.android.com/topic/libraries/architecture/datastore
[MASVS]: https://mas.owasp.org/MASVS/
[MASTG]: https://mas.owasp.org/MASTG/
[PINNING]: https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
[TOP10-2024]: https://owasp.org/projects/mobile-top-10
[GRADLE-DOCS]: https://docs.gradle.org/current/userguide/best_practices_general.html
[AGP-BUILD]: https://developer.android.com/build/optimize-your-build
[BASELINE-PROF]: https://developer.android.com/topic/performance/baselineprofiles/overview
[KSP]: https://kotlinlang.org/docs/ksp-overview.html
