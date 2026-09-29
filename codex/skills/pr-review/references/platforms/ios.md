---
verified: 2026-09-29
sources: inline
---

# Platform pack: iOS

Grading criteria for reviewing an iOS/Swift change. Load this pack when the repo is iOS. It
supplies the standards vocabulary that findings cite and the recipes that turn a suspicion into
evidence. The platform-neutral review rules live in [`../protocol.md`](../protocol.md) §13 to §16.
They cover volatile facts, `Unverified` grading, pragmatism guardrails and main-safety ownership.
Their extensions live in §17 to §20 and cover root cause not symptom, verification criteria, SHA
ancestry and debug-variant exclusion. All of them apply here too.

**Severity cap (important):** Apple publishes no architecture doctrine, so the architecture section
below is *synthesised consensus*, marked **(C)**. Grade those items against the codebase's own
patterns ("inconsistent with itself"), not against doctrine, and cap severity accordingly. See
protocol.md §4. The cap does not apply to MASVS/security items or to verified defects.

## Standards-basis block

Paste this into the review's Standards basis section, then append the verification sentence
(template.md):

```markdown
Findings are graded against published guidance, cited per finding: **[SWIFTUI-DATAFLOW]** Apple's SwiftUI model-data documentation (state ownership, single source of truth), https://developer.apple.com/documentation/swiftui/model-data · **[SWIFT-CONCURRENCY]** the Swift book's concurrency chapter, https://docs.swift.org/latest/documentation/the-swift-programming-language/concurrency/ · **[HIG]** Human Interface Guidelines (44 pt targets, alerts, dark mode, typography), https://developer.apple.com/design/human-interface-guidelines · **[UI-STANDARDS]** tiered UI design rules, T2 graded Nit · **[A11Y]** Apple accessibility documentation, https://developer.apple.com/documentation/accessibility · **[SWIFTLINT]** https://github.com/realm/SwiftLint · **OWASP MASVS** v2.1.0 · **[WCAG22]** WCAG 2.2 AA. Apple publishes no official architecture doctrine, so architecture items are graded as *consensus*. Where the only authority is consensus, we grade the code against **its own patterns in the same PR** rather than doctrine, and severity is capped accordingly.
```

## Architecture, synthesised (no official Apple equivalent)

**Authority note (read before grading):** Apple publishes no equivalent of Android's official
architecture-recommendations page. This benchmark is **synthesised** from Apple's SwiftUI data-flow
documentation ([SWIFTUI-DATAFLOW]), Apple's own sample apps (Backyard Birds and Food Truck,
[BACKYARD-BIRDS] and [FOOD-TRUCK]) and stated community consensus. Fruta uses pre-Observation APIs
and informs structure only. Its items therefore carry **less
authority than the security section below**, so grade accordingly. Prefer "inconsistent with itself"
findings over "inconsistent with a doctrine", and cap severity where the only authority is
consensus. Items are marked **(C)** = consensus (Apple-documented pattern and/or broad community
agreement). There is no SR/R grading to inherit, so do not invent one in findings.

- **Single source of truth per piece of state (C, Apple-documented):** every piece of state has
  exactly one owner. Everything else reads it via observation or a `Binding`. A view copying a
  model property into its own `@State` and syncing manually is a graded finding. Read one screen
  end-to-end and name the owner of each state value.
- **State ownership placement (C, Apple-documented):** `@State` / `@StateObject` / `@Observable`
  instantiation lives at the owning view. Children receive plain values or `Binding`s, not fresh
  copies. An `@ObservedObject` initialised inline per body evaluation (object recreated on every
  update) is a defect. Quote it.
- **Unidirectional data flow (C):** state flows down the view tree, events flow up (closures /
  bound actions), and no child mutates a parent's state through shared mutable references.
- **Side effects in cancellation-aware contexts (C):** async work launched from `.task { }` /
  `.task(id:)` (tied to view identity/lifetime) rather than fire-and-forget `Task { }` in
  `onAppear` or view-model `init`. The latter outlive the screen and race re-entry. See the concurrency notes below.
- **Dependency injection at the composition root (C):** dependencies assembled once at the
  app/scene entry point and passed down (initialiser injection or `@Environment` values), not
  `Singleton.shared` reach-ins from deep views and view models. Grep for `.shared` in feature code
  and quote the offenders worth flagging.
- **Navigation as data (C):** routes modelled as values (route enums, `NavigationPath`,
  `navigationDestination(for:)`) rather than imperative pushes or per-view presentation booleans
  scattered ad hoc. Deep links then reduce to constructing the same route values. A home-grown
  router is fine. Grade whether *it* is typed and centralised, not whether it uses the official API.
- **Persistence & networking behind protocol seams (C):** views/view models depend on protocol
  types (or injected closures), with URLSession/SwiftData/Core Data conformances supplied at the
  root, the seam that makes previews and tests possible. Read one repository/service and its
  consumers.
- **`@MainActor` discipline at the UI boundary (C):** types that publish UI state are `@MainActor`
  (or isolate their mutations to it), and no `DispatchQueue.main.async` is sprinkled through view
  models to patch isolation after the fact. See the concurrency notes below.

> **PRAGMATISM GUARDRAILS, DO NOT FLAG:** this benchmark is synthesised consensus, not doctrine,
> so do **not** raise findings for:
> - absence of TCA / VIPER / Clean-Architecture ceremony in an app that doesn't need it
> - the absence of a view model per view. **MV vs MVVM is a live, unresolved community debate**,
>   so flag *inconsistency within this codebase*, never the choice itself
> - a missing domain/use-case layer in a small app
> - SwiftUI views talking to a repository directly, **where the codebase does this consistently**
> Flag the *absence of state-ownership and seam discipline*, not the absence of architectural
> ceremony.

## State, SwiftUI & concurrency

**UI-state exposure ([SWIFTUI-DATAFLOW]):**
- One observable state value per screen (an `@Observable` / `ObservableObject` exposing a single
  state struct or enum), not scattered independent `@Published` fragments the view must mentally
  join. **Sentinel initial values** (`isLoading = false` + empty array pretending to be "loaded")
  are a graded finding. Model loading/empty/error as explicit cases.
- **No initial data loading in view-model `init` and no fire-and-forget `Task {}` in `onAppear`**.
  Both are graded findings. The fix is `.task { }` on the view (or an owner-scoped structured task)
  so the load is cancelled with the view's identity.
- Navigation, sheets and alerts are state bound to presentation modifiers (`NavigationStack(path:)`, `sheet(item:)`,
  `alert(_:isPresented:presenting:actions:message:)`), which reset the binding on dismiss. Grade a boolean or optional
  trigger that the model resets after a delay or that re-fires on restoration. Only effects without a presentation
  binding, such as haptics, scroll, focus and dismiss, are one-shot. Where they use an `AsyncStream`, grade a single
  consumer, buffering while unsubscribed, and a fresh stream per subscription.

**SwiftUI design system, correctness audit ([HIG], [SWIFTUI-DATAFLOW]):** open the design-system
package (or equivalent) and grade its *correctness*. Presence of a design-system module is not a
pass. It's the highest-value place to get theming, update-performance, and a11y right (every
screen consumes it). Check:
- **Token propagation:** tokens supplied via **`EnvironmentKey` + `@Environment`** (with a sensible
  `defaultValue`) so they participate in SwiftUI's update and trait system. **Flag a global mutable
  `Theme.shared` singleton captured at class-load**. A brand/theme switch neither propagates nor
  re-renders, and dark-mode/trait-collection reactivity is lost. Grep for hardcoded
  `Color(red:...)` / hex literals / literal point sizes outside the theme layer and quote offenders.
- **App-root theme injection:** the theme/environment is injected once at the `App`/scene root.
  Components read tokens from the environment, or else they silently fall through to defaults.
- **Component API quality:** `@ViewBuilder` content slots over boolean/enum appearance flags,
  variants expressed as `ButtonStyle` / `LabelStyle` / `ViewModifier` conformances rather than
  copy-pasted component forks, and no hardcoded colours or metrics inside components. Use asset-catalog
  colours **with dark-appearance variants** (note any-appearance-only entries).
- **`#Preview` safety:** components render in previews without live networking or a real DI graph.
  Grade preview coverage of the component catalog, not mere existence.
- **Per-component accessibility (see Accessibility below):** labels/traits baked into interactive components.
  A11y is won or lost in the design system.

**UI design ([UI-STANDARDS], [HIG], [WCAG22]):**
- Grade UI against the tiered design rules, the `design-standards.md` file the toolkit installs (`~/.claude/rules/` on Claude Code, `guidance/` on Codex and Antigravity). The `design-standards` skill carries the sources, rationale and APIs. Cite the rule ID and source key in each finding. T1 breaches grade Blocker or Major by user impact, T2 breaches grade Nit unless the project opts the rule in. iOS specifics are IOS-1 to IOS-4 (semantic colours, Liquid Glass out of the content layer, safe area, haptics used sparingly), with A11Y-4 for the 44 pt hit region and 28 pt HIG minimum, TYP-1 for Dynamic Type and A11Y-7 for the largest accessibility text size.

**SwiftUI update performance & identity ([SWIFTUI-DATAFLOW]):**
- Prefer `@Observable` (field-level access tracking) over `ObservableObject` whole-object
  invalidation for new code, and `Equatable` conformance on view/value inputs where diffing matters.
- **Stable `ForEach`/`List` identity:** never `id: \.self` on unstable or duplicable data, never a
  `UUID()` minted per `body` evaluation (destroys identity every update). Quote the `id` source.
- **Method, not vibes:** re-render/recomputation claims without evidence from
  `Self._printChanges()` output or the Instruments SwiftUI template are `Unverified`.
- Value-type model discipline: models as structs crossing the UI boundary, and reference types reserved
  for identity-bearing state owners.

**Concurrency ([SWIFT-CONCURRENCY], [SWIFT6-MIGRATION]):**
- Structured concurrency by default: child tasks / `async let` / task groups over `Task.detached`
  (each `detached` use must justify losing priority, task-locals and cancellation).
- `.task { }` for view-scoped work (auto-cancel), and long-lived observation owned by the state owner
  with an explicit cancellation story. Find who cancels it and quote the line.
- **`@MainActor` boundary:** UI-state mutation isolated to the main actor by annotation, not by
  scattered `DispatchQueue.main.async` hops, and **actor** isolation (not locks/queues) for shared
  mutable state off the UI.
- **Main-safety is the data layer's job, not the view model's:** main-safety belongs to whichever
  type does the blocking work. Repository/data-source `async` functions run off the main actor by
  design (`@concurrent` or actor-isolated async functions. A plain `nonisolated async` function runs on the caller's actor
  when `NonisolatedNonsendingByDefault` is on, so it is not main-safe by itself, [SE-0461]), so callers need no dispatch hops. A `@MainActor`
  view model simply `await`s already-main-safe functions. **`DispatchQueue.global()` or
  `Task.detached` inside a view model is a smell** that main-safety leaked up from the data layer.
  Grade it as a style issue, not a bug (per the pragmatism guardrails above), unless it demonstrably blocks the main
  thread.
- **Swift 6 / strict concurrency as a currency signal:** note the language mode and
  `SWIFT_STRICT_CONCURRENCY` level, `SWIFT_DEFAULT_ACTOR_ISOLATION` and `SWIFT_APPROACHABLE_CONCURRENCY` ([SE-0466]), `Sendable` adoption on crossing types, and whether warnings are
  suppressed with `@unchecked Sendable` (each one is a claim to verify). This feeds currency findings.
- Smells to grep and quote: `DispatchSemaphore`/`DispatchGroup.wait` on the main thread (deadlock
  class), runloop spinning, GCD-and-async/await mixed without a single bridging seam
  (`withCheckedContinuation`, checking that every continuation resumes exactly once), Combine
  `AnyCancellable`s stored in never-released holders (retained-subscription leaks).

**Testing:** protocol seams for time and network (injected clock/`Clock`, stubbed transport such as
a `URLProtocol` fake) and deterministic async tests driven by clocks/confirmed expectations.
Sleeps and generous `XCTWaiter` timeouts are a flakiness finding. Feed test-coverage findings with these
expectations.


## Security: MASVS v2.1.0 control map (+ Top 10 2024 cross-map)

**Framework ([MASVS], [MASTG]):** OWASP MASVS v2.1.0 is the verification standard (8 groups, 24
controls), and MASTG supplies atomic tests (`MASTG-TEST-xxxx`). Cite test IDs
in Refs where known. **Declare the target MAS profile in the review**: L1 = baseline for all apps,
**L2 = defense-in-depth for sensitive-data apps (finance/health, typically the right target
here)** and R = resilience add-on where the threat model warrants it. Grade each control
Pass/Fail/Partial/Unverified with `file:line` evidence.

| Control | What it requires | Static-check recipe (open & quote) |
|---|---|---|
| STORAGE-1 | Sensitive data stored securely | Where tokens/PII actually live: Keychain vs `UserDefaults`/plist/files/unencrypted SQLite-Core Data (plain = Fail). For each Keychain item quote its `kSecAttrAccessible*` class. `kSecAttrAccessibleAlways` (deprecated) or `AfterFirstUnlock*` on high-value tokens is a graded finding. Target `WhenUnlockedThisDeviceOnly` for session tokens (verify current guidance, protocol.md §13). Secrets in committed `.xcconfig`/`Info.plist`/`Secrets.swift` constants, `FileProtectionType` on written files (`.complete*` vs none) and `isExcludedFromBackup` on sensitive caches. Refs: MASVS-STORAGE-1 · [KEYCHAIN] · [MASVS] |
| STORAGE-2 | No sensitive-data leakage | Backup/export surface (`isExcludedFromBackup`, files landing in iCloud-synced containers). **In-memory residency of secrets**: PIN/password/key material held in an immutable `String` stays in the heap until deallocation and is recoverable from a dump. The target is zeroable `Data`/`[UInt8]` wiped via `resetBytes(in:)` in a `defer` immediately after use. Grade the **whole path** (input field → repository → crypto call), not one variable. Where a `SecureField`/`UITextField` `String` boundary makes end-to-end wiping impossible, grade the **residency window** and say so. Never give it a clean pass and never propose a fix that can't be built. Log leakage is graded in PRIVACY-3 and screen capture/snapshots in PLATFORM-3, so cross-reference rather than re-checking |
| CRYPTO-1 | Strong, correctly-used crypto | Rolled-own crypto: `CCCrypt`/CommonCrypto with ECB or static IVs, MD5/SHA-1 for security purposes, `arc4random`/`Int.random` for key material vs `SecRandomCopyBytes`. The target is CryptoKit primitives (`AES.GCM`, `ChaChaPoly`, `SHA256`). Quote every low-level crypto call site and what selects its mode/IV. Refs: MASVS-CRYPTO-1 · [CRYPTOKIT] · [MASVS] |
| CRYPTO-2 | Sound key management | Hardcoded keys/IVs (high-entropy string constants, committed xcconfig/plist values), keys generated and held in the Keychain with `SecAccessControl`, and Secure Enclave (`kSecAttrTokenIDSecureEnclave` / CryptoKit `SecureEnclave.P256`) for asymmetric keys where hardware backing matters. Verify private keys never leave `SecKey`/enclave types into exportable `Data`. Refs: MASVS-CRYPTO-2 · [KEYCHAIN] · [CRYPTOKIT] |
| AUTH-1 | Secure auth/authz protocols | Token issuance/refresh/rotation wiring (pairs with the token-refresh trace). Session invalidation on logout = Keychain item deletion **and** server-side revoke, not just navigation. Passkeys where present: `ASAuthorizationPlatformPublicKeyCredential` + the `webcredentials` AASA association. Verify the served AASA file, not just the client code. Refs: MASVS-AUTH-1 · [MASVS] |
| AUTH-2 | Secure local authentication | **A bare boolean back from `LAContext.evaluatePolicy` gating UI is the finding**. Biometric auth must be **bound to a Keychain item** via `SecAccessControl` with `.biometryCurrentSet` (the CryptoObject-binding analogue), so the protected secret is only released on successful biometry and re-enrolled biometrics invalidate it. Check `evaluatedPolicyDomainState` change detection where the app tracks enrolment itself, and note `.deviceOwnerAuthentication` (passcode fallback) vs `.deviceOwnerAuthenticationWithBiometrics` against product intent. Refs: MASVS-AUTH-2 · [LOCALAUTH] · [KEYCHAIN] |
| AUTH-3 | Extra auth for sensitive ops | Step-up auth before payments/credential changes. Trace one sensitive flow end-to-end and quote where the step-up is enforced (client *and* server) |
| NETWORK-1 | All traffic secured | `NSAppTransportSecurity` in every target's `Info.plist`: `NSAllowsArbitraryLoads` (+`InWebContent`/`ForMedia`/`LocalNetworking` carve-outs) and each `NSExceptionDomains` entry (`NSExceptionAllowsInsecureHTTPLoads`, minimum-TLS keys). Reconcile every exception vs the hosts the app actually calls, and grep for `http://` base URLs in code and xcconfig. Refs: MASVS-NETWORK-1 · [ATS] |
| NETWORK-2 | Identity pinning (done safely) + request integrity for owned endpoints | **Grade in context. Pinning is optional defense-in-depth, not mandatory, so don't reward mere presence or punish mere absence.** _Present_ (`URLSessionDelegate` trust evaluation / TrustKit / Alamofire `ServerTrustManager` / `NSPinnedDomains` in Info.plist): verify it covers the **real hosts the app actually calls** (pinning hosts never called = Fail/theatre), has **≥1 backup pin**, and an **expiry or remotely-updatable path** so rotation can't brick installs without a release. A challenge handler that calls `completionHandler(.useCredential, …)` without evaluating `SecTrust` = **Critical** (the empty-TrustManager analogue). _Absent_: **not an automatic Fail**. OWASP/platform guidance now often discourages pinning (CT vs downtime risk, and it breaks under corporate TLS inspection). Verify current stance at review time (protocol.md §13). Also, are **money-movement / credential-change requests signed or attested beyond a bearer token** (App Attest assertions, see RESILIENCE-1)? Put the safe-rotation implementation (SPKI, hybrid, signed remote pins + kill-switch, per [PINNING]) in the finding's PR comment and `verify_fixed_when`. Refs: MASVS-NETWORK-2 · [PINNING] · [MASVS] |
| PLATFORM-1 | Secure IPC | Entry-point audit: custom URL schemes (`CFBundleURLTypes`) vs universal links + AASA. Schemes are claimable by any installed app, so sensitive flows over a bare scheme are graded. Incoming-URL handling (`onOpenURL` / `application(_:open:)`) validated, with no open-redirect or unvalidated parameter forwarding into WebViews/navigation. `LSApplicationQueriesSchemes` breadth. App extensions + App Groups, covering what crosses the shared container and at what protection class. Entitlements review. Refs: MASVS-PLATFORM-1 · [MASTG] |
| PLATFORM-2 | Secure WebViews | `WKWebView` configuration: `allowFileAccessFromFileURLs` / `allowUniversalAccessFromFileURLs` preference flags, `loadFileURL(_:allowingReadAccessTo:)` scope, JS enabled for untrusted content. Enumerate every `WKScriptMessageHandler` bridge and grade its trust of `postMessage` input (origin/host checks, capability exposed). `isInspectable` left true in Release. Refs: MASVS-PLATFORM-2 · [MASTG] |
| PLATFORM-3 | Secure UI usage | **Input privacy on sensitive fields:** `isSecureTextEntry` / `SecureField`, `textContentType` (`.password`/`.oneTimeCode`/`.newPassword`), autocorrection and spell-checking disabled (`autocorrectionType = .no`, `.autocorrectionDisabled()`) so the keyboard cache learns nothing. Name the fields you checked and their actual state. **Pasteboard:** `UIPasteboard.general` writes of sensitive values. Target `.localOnly` + expiry via `setItems(_:options:)`. **Screen capture: iOS has no `FLAG_SECURE` equivalent, so say so.** Grade what the app does instead: `UIScreen.isCaptured` / `capturedDidChangeNotification` observation, `userDidTakeScreenshotNotification` handling, and snapshot privacy (blur/cover on `sceneWillResignActive` so balances/PII don't persist in the app-switcher snapshot). Refs: MASVS-PLATFORM-3 · [MASTG] |
| CODE-1 | Up-to-date platform version | Xcode / base-SDK vs the **App Store minimum-SDK submission requirement + effective date. Look it up at review time (protocol.md §13) and don't assert from memory** (annual, typically late April). Grade a toolchain below it as a **hard App Store submission gate** (dated finding), not merely "behind". Also note the `IPHONEOS_DEPLOYMENT_TARGET` spread. Feeds currency findings. Refs: MASVS-CODE-1 · [SUBMIT-REQS] |
| CODE-2 | Enforced app updates / incident response | Force-update mechanism and a remote **feature kill-switch** (remote-config-gated). For a regulated/fintech app treat absence as a graded finding, and check the mechanism is wired, not just declared. **There is no release rollback on the App Store**. A bad build can only be fixed forward through review, which raises the value of kill-switches and phased release. Call this out as a distinct risk. A **certificate-pinning kill-switch** is a specific case (see NETWORK-2). It must be **signed/authenticated** (an unauthenticated toggle is a one-switch bypass) and fail back to default PKI trust, never to disabled TLS validation |
| CODE-3 | No known-vulnerable components | Dependency versions vs known CVEs, and SCA tooling in CI (Renovate/Dependabot cover SPM, and osv-scanner reads `Package.resolved`). This pairs with the dependency/currency review |
| CODE-4 | Input validation | SQL built by string concatenation (raw SQLite / FMDB + interpolation), deep-link/URL parameter handling (pairs with PLATFORM-1), unsafe deserialisation (`NSKeyedUnarchiver` without `requiresSecureCoding` / `unarchivedObject(ofClasses:)`) and JS evaluation of remote strings. **Memory-unsafe surface:** Swift is memory-safe by default. What remains is `withUnsafe*`/`UnsafeMutablePointer` use and C/ObjC bridge code (`strcpy`/`memcpy` in vendored C). Enumerate and grade that residual surface rather than asserting blanket safety |
| RESILIENCE-1 | Platform-integrity validation | Attestation and device-integrity wiring. Read it and don't grep-match. **App Attest / DeviceCheck (`DCAppAttestService` key generation + attestation, assertions on sensitive requests) is the platform mechanism.** Also check verdicts are **enforced server-side**, not client-only (trivially bypassable). Jailbreak heuristics, where present: Cydia/`/private` sandbox-escape write test, `fork()` probe, suspicious dylibs via `_dyld_image_count`/`_dyld_get_image_name`. Grade as best-effort signals (bypassable), never as a control that "prevents" anything. Refs: MASVS-RESILIENCE-1 · [APP-ATTEST] · [MASVS] |
| RESILIENCE-2 | Anti-tampering | App Store code-signing covers baseline integrity. Grade what the app adds where the threat model warrants: bundle-integrity/self-checks, provisioning-profile presence checks (re-signing signal), and whether responses degrade gracefully vs brick the app for false positives |
| RESILIENCE-3 | Anti-static-analysis | Symbol stripping actually effective on Release (`DEPLOYMENT_POSTPROCESSING`/`STRIP_*`, pairs with the build-settings review), and string/asset protection for sensitive constants. **Be honest about limits:** Swift/ObjC metadata keeps much recoverable and there is no R8/ProGuard analogue. Commercial obfuscators exist, but absence is contextual, not an automatic finding |
| RESILIENCE-4 | Anti-dynamic-analysis | Anti-debug: `ptrace(PT_DENY_ATTACH)`, `sysctl` `P_TRACED` checks, debugger/hook detection (Frida artefacts, injected dylib scans). Confirm `get-task-allow` is false in Release entitlements, and grade detection responses like RESILIENCE-2 (signals, server-visible, non-bricking) |
| PRIVACY-1 | Minimal data/resource access | `NS*UsageDescription` audit. Every declared key maps to a real feature need (boilerplate/misleading purpose strings are transparency findings, and a missing key = runtime crash). Entitlements and `UIBackgroundModes` breadth vs actual use |
| PRIVACY-2 | Prevent user identification | Identifier collection & linkage: IDFA (requires ATT authorisation via `ATTrackingManager.requestTrackingAuthorization` + `NSUserTrackingUsageDescription`, and any tracking call before authorisation = Fail), IDFV, fingerprinting signals. Tracking domains declared in the privacy manifest vs actually contacted (hosts the app actually calls). Refs: MASVS-PRIVACY-2 · [ATT] · [PRIVACY-MANIFEST] |
| PRIVACY-3 | Transparency | `PrivacyInfo.xcprivacy` present and truthful for the app **and** third-party SDKs (required-reason APIs declared with valid reason codes. Enforcement dates move, so verify protocol.md §13). Nutrition-label consistency vs the SDKs actually found in the dependency inventory, and `ITSAppUsesNonExemptEncryption` declared correctly. **Log hygiene:** `os_log`/`Logger` interpolations marked `privacy: .public` on sensitive values, and raw `print()`/`NSLog` of PII reaching Release builds. Refs: MASVS-PRIVACY-3 · [PRIVACY-MANIFEST] |
| PRIVACY-4 | User data control | Deletion/opt-out paths for collected data and in-app **account deletion** where accounts can be created (an App Store review requirement). Verify the flow deletes server-side data, not just the local session |

**OWASP Mobile Top 10 (2024) cross-map** (check owasp.org for a newer edition before citing it. The Top 10 is the
awareness list, MASVS is the verification standard). Emit as
a compact table pointing each M-risk at the MASVS rows above rather than re-checking:
M1 Credentials→CRYPTO-2/AUTH-1 · M2 Supply Chain→CODE-3 · M3 Auth/Authz→AUTH-1/2/3 ·
M4 Input/Output Validation→CODE-4 · M5 Insecure Communication→NETWORK-1/2 ·
M6 Privacy→PRIVACY-1..4 · M7 Binary Protections→RESILIENCE-1..4 ·
M8 Misconfiguration→PLATFORM-1/STORAGE-2 · M9 Data Storage→STORAGE-1/2 · M10 Crypto→CRYPTO-1/2.

## Accessibility

- **Accessibility ([A11Y], [HIG]), also per-component in the design-system audit above.** A
  static pass can't replace VoiceOver, but grade these against the code (a regulated/finance app
  faces WCAG-grade expectations). **Touch targets** of 44×44 pt on buttons, with 28 pt the HIG minimum for any control (flag icon-only
  buttons below it). **Labels:** `accessibilityLabel`/`Value`/`Hint` on interactive elements,
  images/icons labelled or explicitly hidden (quote the ratio + offenders). **Traits:**
  `.isHeader`/`.isButton` etc. so structure and role are announced. **Dynamic Type:**
  `@ScaledMetric` for metrics that should scale, no fixed `.font(.system(size:))` on body text, and
  layouts that survive AX sizes (truncation checked). **VoiceOver traversal order** on composite
  rows (`accessibilityElement(children: .combine)`, sort priority). **Contrast** per WCAG.
  Verification tooling: Accessibility Inspector + `XCUIApplication().performAccessibilityAudit()`
  in UI tests. Anything needing a device pass goes under "Unverified (needs a trace)" with the
  VoiceOver / Accessibility-Inspector run that would confirm it.

## Source registry (canonical URLs for Refs lines)

| Key | Source |
|---|---|
| [SWIFTUI-DATAFLOW] | https://developer.apple.com/documentation/swiftui/model-data, Apple's SwiftUI data-flow/model-data documentation (state ownership, observation, bindings) |
| [BACKYARD-BIRDS] | https://github.com/apple/sample-backyard-birds, Apple sample app (SwiftUI + SwiftData, multi-target) used here as the architecture consensus source |
| [FOOD-TRUCK] | https://github.com/apple/sample-food-truck, Apple sample app (SwiftUI app + widgets, shared model layer) |
| [SWIFT-CONCURRENCY] | https://docs.swift.org/latest/documentation/the-swift-programming-language/concurrency/, structured concurrency, actors, tasks (official language book) |
| [SWIFT6-MIGRATION] | https://www.swift.org/migration/documentation/migrationguide/, Swift 6 / strict-concurrency migration guide (staging, Sendable) |
| [SE-0461] | https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md, `NonisolatedNonsendingByDefault` and `@concurrent`, implemented in Swift 6.2 |
| [SE-0466] | https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md, default actor isolation setting, implemented in Swift 6.2 |
| [SPM] | https://www.swift.org/documentation/package-manager/, Swift Package Manager documentation (products, dependency rules, Package.resolved) |
| [XCODE-BUILD] | https://developer.apple.com/documentation/xcode/build-settings-reference, canonical build-settings reference (optimisation, stripping, sandboxing) |
| [SWIFTLINT] | https://github.com/realm/SwiftLint, de-facto standard Swift linter |
| [HIG] | https://developer.apple.com/design/human-interface-guidelines, Apple Human Interface Guidelines (incl. 44 pt default and 28 pt minimum targets, platform conventions) |
| [UI-STANDARDS] | The toolkit's `design-standards.md` rule file (shared/guidance/design-standards.md in ai-toolkit), tiered rules with IDs. Sources per key in the design-standards skill, `references/sources.md` |
| [WCAG22] | https://www.w3.org/TR/WCAG22/ (W3C Recommendation, 2024-12-12), cite the success criterion per finding |
| [A11Y] | https://developer.apple.com/documentation/accessibility, Apple accessibility documentation (labels/traits, Dynamic Type, audits) |
| [KEYCHAIN] | https://developer.apple.com/documentation/security/keychain-services, Keychain Services (accessibility classes, SecAccessControl) |
| [CRYPTOKIT] | https://developer.apple.com/documentation/cryptokit, CryptoKit (modern primitives, Secure Enclave key types) |
| [LOCALAUTH] | https://developer.apple.com/documentation/localauthentication, LocalAuthentication (LAContext, evaluatePolicy, domain state) |
| [ATS] | https://developer.apple.com/documentation/security/preventing-insecure-network-connections, App Transport Security and its exception keys |
| [APP-ATTEST] | https://developer.apple.com/documentation/devicecheck, DeviceCheck framework incl. App Attest (attestation is verified server-side) |
| [PRIVACY-MANIFEST] | https://developer.apple.com/documentation/bundleresources/privacy-manifest-files, PrivacyInfo.xcprivacy, required-reason APIs, tracking domains |
| [ATT] | https://developer.apple.com/documentation/apptrackingtransparency, App Tracking Transparency (IDFA authorisation) |
| [SUBMIT-REQS] | https://developer.apple.com/news/upcoming-requirements/, App Store upcoming requirements (minimum Xcode/SDK submission gate + effective dates) |
| [LAUNCH-TIME] | https://developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time, launch-time guidance (dyld/pre-main, measurement) |
| [APP-SIZE] | https://developer.apple.com/documentation/xcode/reducing-your-app-s-size, app-size guidance (thinning, size report, download vs install) |
| [MASVS] | https://mas.owasp.org/MASVS/ (v2.1.0) |
| [MASTG] | https://mas.owasp.org/MASTG/ (cite the version shown on the site at review time). Cite iOS techniques/tests generically unless a specific iOS test ID is verified |
| [PINNING] | https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html, OWASP Pinning Cheat Sheet (public-key/SPKI pins, backup pins, expiration safety-valve, when NOT to pin) |
| [TOP10-2024] | https://owasp.org/projects/mobile-top-10 |

<!-- Source links. Keep in sync with the table above (primary URL per key) so [KEY] references
     render as links wherever this pack's content is pasted -->
[SWIFTUI-DATAFLOW]: https://developer.apple.com/documentation/swiftui/model-data
[BACKYARD-BIRDS]: https://github.com/apple/sample-backyard-birds
[FOOD-TRUCK]: https://github.com/apple/sample-food-truck
[SWIFT-CONCURRENCY]: https://docs.swift.org/latest/documentation/the-swift-programming-language/concurrency/
[SWIFT6-MIGRATION]: https://www.swift.org/migration/documentation/migrationguide/
[SE-0461]: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md
[SE-0466]: https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md
[SPM]: https://www.swift.org/documentation/package-manager/
[XCODE-BUILD]: https://developer.apple.com/documentation/xcode/build-settings-reference
[SWIFTLINT]: https://github.com/realm/SwiftLint
[HIG]: https://developer.apple.com/design/human-interface-guidelines
[UI-STANDARDS]: https://github.com/Mark-Hine/ai-toolkit/blob/main/shared/guidance/design-standards.md
[WCAG22]: https://www.w3.org/TR/WCAG22/
[A11Y]: https://developer.apple.com/documentation/accessibility
[KEYCHAIN]: https://developer.apple.com/documentation/security/keychain-services
[CRYPTOKIT]: https://developer.apple.com/documentation/cryptokit
[LOCALAUTH]: https://developer.apple.com/documentation/localauthentication
[ATS]: https://developer.apple.com/documentation/security/preventing-insecure-network-connections
[APP-ATTEST]: https://developer.apple.com/documentation/devicecheck
[PRIVACY-MANIFEST]: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
[ATT]: https://developer.apple.com/documentation/apptrackingtransparency
[SUBMIT-REQS]: https://developer.apple.com/news/upcoming-requirements/
[LAUNCH-TIME]: https://developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time
[APP-SIZE]: https://developer.apple.com/documentation/xcode/reducing-your-app-s-size
[MASVS]: https://mas.owasp.org/MASVS/
[MASTG]: https://mas.owasp.org/MASTG/
[PINNING]: https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
[TOP10-2024]: https://owasp.org/projects/mobile-top-10
