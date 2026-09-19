# Platform pack — iOS

Grading criteria for reviewing an iOS/Swift change. Load this pack when the repo is iOS; it
supplies the standards vocabulary that findings cite and the recipes that turn a suspicion into
evidence. The platform-neutral review rules — volatile facts, `Unverified` grading, pragmatism
guardrails, main-safety ownership — live in [`../protocol.md`](../protocol.md) §13–§16, and their
extensions — root cause not symptom, verification criteria, SHA ancestry, debug-variant
exclusion — in §17–§20; all apply here too.

**Severity cap (important):** Apple publishes no architecture doctrine, so the architecture section
below is *synthesised consensus*, marked **(C)**. Grade those items against the codebase's own
patterns ("inconsistent with itself"), not against doctrine, and cap severity accordingly — see
protocol.md §4. The cap does not apply to MASVS/security items or to verified defects.

## Standards-basis block

Paste this into the review's Standards basis section, then append the verification sentence
(template.md):

```markdown
Findings are graded against published guidance, cited per finding: **[SWIFTUI-DATAFLOW]** Apple's SwiftUI model-data documentation (state ownership, single source of truth) — https://developer.apple.com/documentation/swiftui/model-data · **[SWIFT-CONCURRENCY]** the Swift book's concurrency chapter — https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/ · **[HIG]** Human Interface Guidelines (44 pt targets, alerts, dark mode, typography) — https://developer.apple.com/design/human-interface-guidelines · **[A11Y]** Apple accessibility documentation — https://developer.apple.com/documentation/accessibility · **[SWIFTLINT]** https://github.com/realm/SwiftLint · **OWASP MASVS** v2.1.0 · WCAG 2.1 AA. Apple publishes no official architecture doctrine, so architecture items are graded as *consensus* — where the only authority is consensus, we grade the code against **its own patterns in the same PR** rather than doctrine, and severity is capped accordingly.
```

## Architecture — synthesised (no official Apple equivalent)

**Authority note (read before grading):** Apple publishes no equivalent of Android's official
architecture-recommendations page. This benchmark is **synthesised** from Apple's SwiftUI data-flow
documentation ([SWIFTUI-DATAFLOW]), Apple's own sample apps (Backyard Birds, Fruta, Food Truck —
[BACKYARD-BIRDS], [FOOD-TRUCK]) and stated community consensus. Its items therefore carry **less
authority than the security section below** — grade accordingly: prefer "inconsistent with itself"
findings over "inconsistent with a doctrine", and cap severity where the only authority is
consensus. Items are marked **(C)** = consensus (Apple-documented pattern and/or broad community
agreement) — there is no SR/R grading to inherit, so do not invent one in findings.

- **Single source of truth per piece of state (C, Apple-documented):** every piece of state has
  exactly one owner; everything else reads it via observation or a `Binding`. A view copying a
  model property into its own `@State` and syncing manually is a graded finding. Read one screen
  end-to-end and name the owner of each state value.
- **State ownership placement (C, Apple-documented):** `@State` / `@StateObject` / `@Observable`
  instantiation lives at the owning view; children receive plain values or `Binding`s, not fresh
  copies. An `@ObservedObject` initialised inline per body evaluation (object recreated on every
  update) is a defect — quote it.
- **Unidirectional data flow (C):** state flows down the view tree, events flow up (closures /
  bound actions); no child mutating a parent's state through shared mutable references.
- **Side effects in cancellation-aware contexts (C):** async work launched from `.task { }` /
  `.task(id:)` (tied to view identity/lifetime) rather than fire-and-forget `Task { }` in
  `onAppear` or view-model `init` — the latter outlive the screen and race re-entry. See the concurrency notes below.
- **Dependency injection at the composition root (C):** dependencies assembled once at the
  app/scene entry point and passed down (initialiser injection or `@Environment` values), not
  `Singleton.shared` reach-ins from deep views and view models. Grep for `.shared` in feature code
  and quote the offenders worth flagging.
- **Navigation as data (C):** routes modelled as values (route enums, `NavigationPath`,
  `navigationDestination(for:)`) rather than imperative pushes or per-view presentation booleans
  scattered ad hoc; deep links then reduce to constructing the same route values. A home-grown
  router is fine — grade whether *it* is typed and centralised, not whether it uses the official API.
- **Persistence & networking behind protocol seams (C):** views/view models depend on protocol
  types (or injected closures), with URLSession/SwiftData/Core Data conformances supplied at the
  root — the seam that makes previews and tests possible. Read one repository/service and its
  consumers.
- **`@MainActor` discipline at the UI boundary (C):** types that publish UI state are `@MainActor`
  (or isolate their mutations to it); no `DispatchQueue.main.async` sprinkled through view models
  to patch isolation after the fact. See the concurrency notes below.

> **PRAGMATISM GUARDRAILS — DO NOT FLAG:** this benchmark is synthesised consensus, not doctrine —
> do **not** raise findings for:
> - absence of TCA / VIPER / Clean-Architecture ceremony in an app that doesn't need it;
> - the absence of a view model per view — **MV vs MVVM is a live, unresolved community debate**;
>   flag *inconsistency within this codebase*, never the choice itself;
> - a missing domain/use-case layer in a small app;
> - SwiftUI views talking to a repository directly, **where the codebase does this consistently**.
> Flag the *absence of state-ownership and seam discipline*, not the absence of architectural
> ceremony.

## State, SwiftUI & concurrency

**UI-state exposure ([SWIFTUI-DATAFLOW]):**
- One observable state value per screen (an `@Observable` / `ObservableObject` exposing a single
  state struct or enum), not scattered independent `@Published` fragments the view must mentally
  join. **Sentinel initial values** (`isLoading = false` + empty array pretending to be "loaded")
  are a graded finding — model loading/empty/error as explicit cases.
- **No initial data loading in view-model `init` and no fire-and-forget `Task {}` in `onAppear`** —
  both are graded findings; the fix is `.task { }` on the view (or an owner-scoped structured task)
  so the load is cancelled with the view's identity.
- One-shot events (navigation, toasts) delivered via `AsyncStream` / `PassthroughSubject` consumed
  exactly once — not modelled as state that re-fires on every re-render or restoration; quote the
  consumption site and how it is reset.

**SwiftUI design system — correctness audit ([HIG], [SWIFTUI-DATAFLOW]):** open the design-system
package (or equivalent) and grade its *correctness* — presence of a design-system module is not a
pass. It's the highest-leverage place to get theming, update-performance, and a11y right (every
screen consumes it). Check:
- **Token propagation:** tokens supplied via **`EnvironmentKey` + `@Environment`** (with a sensible
  `defaultValue`) so they participate in SwiftUI's update and trait system. **Flag a global mutable
  `Theme.shared` singleton captured at class-load** — a brand/theme switch neither propagates nor
  re-renders, and dark-mode/trait-collection reactivity is lost. Grep for hardcoded
  `Color(red:...)` / hex literals / literal point sizes outside the theme layer and quote offenders.
- **App-root theme injection:** the theme/environment is injected once at the `App`/scene root;
  components read tokens from the environment — else they silently fall through to defaults.
- **Component API quality:** `@ViewBuilder` content slots over boolean/enum appearance flags;
  variants expressed as `ButtonStyle` / `LabelStyle` / `ViewModifier` conformances rather than
  copy-pasted component forks; no hardcoded colours or metrics inside components — asset-catalog
  colours **with dark-appearance variants** (note any-appearance-only entries).
- **`#Preview` safety:** components render in previews without live networking or a real DI graph;
  grade preview coverage of the component catalog, not mere existence.
- **Per-component accessibility (see Accessibility below):** labels/traits baked into interactive components —
  a11y is won or lost in the design system.

**SwiftUI update performance & identity ([SWIFTUI-DATAFLOW]):**
- Prefer `@Observable` (field-level access tracking) over `ObservableObject` whole-object
  invalidation for new code; `Equatable` conformance on view/value inputs where diffing matters.
- **Stable `ForEach`/`List` identity:** never `id: \.self` on unstable or duplicable data, never a
  `UUID()` minted per `body` evaluation (destroys identity every update) — quote the `id` source.
- **Method, not vibes:** re-render/recomputation claims without evidence from
  `Self._printChanges()` output or the Instruments SwiftUI template are `Unverified`.
- Value-type model discipline: models as structs crossing the UI boundary; reference types reserved
  for identity-bearing state owners.

**Concurrency ([SWIFT-CONCURRENCY], [SWIFT6-MIGRATION]):**
- Structured concurrency by default: child tasks / `async let` / task groups over `Task.detached`
  (each `detached` use must justify losing priority, task-locals and cancellation).
- `.task { }` for view-scoped work (auto-cancel); long-lived observation owned by the state owner
  with an explicit cancellation story — find who cancels it and quote the line.
- **`@MainActor` boundary:** UI-state mutation isolated to the main actor by annotation, not by
  scattered `DispatchQueue.main.async` hops; **actor** isolation (not locks/queues) for shared
  mutable state off the UI.
- **Main-safety is the data layer's job, not the view model's:** main-safety belongs to whichever
  type does the blocking work — repository/data-source `async` functions run off the main actor by
  design (nonisolated async / actor-isolated), so callers need no dispatch hops. A `@MainActor`
  view model simply `await`s already-main-safe functions; **`DispatchQueue.global()` or
  `Task.detached` inside a view model is a smell** that main-safety leaked up from the data layer —
  grade it as a style issue, not a bug (per the pragmatism guardrails above), unless it demonstrably blocks the main
  thread.
- **Swift 6 / strict concurrency as a currency signal:** note the language mode and
  `SWIFT_STRICT_CONCURRENCY` level, `Sendable` adoption on crossing types, and whether warnings are
  suppressed with `@unchecked Sendable` (each one is a claim to verify) — feeds currency findings.
- Smells to grep and quote: `DispatchSemaphore`/`DispatchGroup.wait` on the main thread (deadlock
  class), runloop spinning, GCD-and-async/await mixed without a single bridging seam
  (`withCheckedContinuation` — check every continuation resumes exactly once), Combine
  `AnyCancellable`s stored in never-released holders (retained-subscription leaks).

**Testing:** protocol seams for time and network (injected clock/`Clock`, stubbed transport such as
a `URLProtocol` fake); deterministic async tests driven by clocks/confirmed expectations — sleeps
and generous `XCTWaiter` timeouts are a flakiness finding. Feed test-coverage findings with these
expectations.


## Security — MASVS v2.1.0 control map (+ Top 10 2024 cross-map)

**Framework ([MASVS], [MASTG]):** OWASP MASVS v2.1.0 is the verification standard (8 groups, 24
controls); MASTG v2.0.0 (stable 2026-06) supplies atomic tests (`MASTG-TEST-xxxx`) — cite test IDs
in Refs where known. **Declare the target MAS profile in the review**: L1 = baseline for all apps;
**L2 = defense-in-depth for sensitive-data apps (finance/health — typically the right target
here)**; R = resilience add-on where the threat model warrants it. Grade each control
Pass/Fail/Partial/Unverified with `file:line` evidence.

| Control | What it requires | Static-check recipe (open & quote) |
|---|---|---|
| STORAGE-1 | Sensitive data stored securely | Where tokens/PII actually live: Keychain vs `UserDefaults`/plist/files/unencrypted SQLite-Core Data (plain = Fail). For each Keychain item quote its `kSecAttrAccessible*` class — `kSecAttrAccessibleAlways` (deprecated) or `AfterFirstUnlock*` on high-value tokens is a graded finding; target `WhenUnlockedThisDeviceOnly` for session tokens (verify current guidance, protocol.md §13). Secrets in committed `.xcconfig`/`Info.plist`/`Secrets.swift` constants; `FileProtectionType` on written files (`.complete*` vs none); `isExcludedFromBackup` on sensitive caches. Refs: MASVS-STORAGE-1 · [KEYCHAIN] · [MASVS] |
| STORAGE-2 | No sensitive-data leakage | Backup/export surface (`isExcludedFromBackup`, files landing in iCloud-synced containers); **in-memory residency of secrets** — PIN/password/key material held in an immutable `String` stays in the heap until deallocation and is recoverable from a dump; the target is zeroable `Data`/`[UInt8]` wiped via `resetBytes(in:)` in a `defer` immediately after use. Grade the **whole path** (input field → repository → crypto call), not one variable. Where a `SecureField`/`UITextField` `String` boundary makes end-to-end wiping impossible, grade the **residency window** and say so — never a clean pass, never a fix that can't be built. Log leakage is graded in PRIVACY-3 and screen capture/snapshots in PLATFORM-3 — cross-reference rather than re-checking |
| CRYPTO-1 | Strong, correctly-used crypto | Rolled-own crypto: `CCCrypt`/CommonCrypto with ECB or static IVs, MD5/SHA-1 for security purposes, `arc4random`/`Int.random` for key material vs `SecRandomCopyBytes`; the target is CryptoKit primitives (`AES.GCM`, `ChaChaPoly`, `SHA256`) — quote every low-level crypto call site and what selects its mode/IV. Refs: MASVS-CRYPTO-1 · [CRYPTOKIT] · [MASVS] |
| CRYPTO-2 | Sound key management | Hardcoded keys/IVs (high-entropy string constants, committed xcconfig/plist values); keys generated and held in the Keychain with `SecAccessControl`; Secure Enclave (`kSecAttrTokenIDSecureEnclave` / CryptoKit `SecureEnclave.P256`) for asymmetric keys where hardware backing matters — verify private keys never leave `SecKey`/enclave types into exportable `Data`. Refs: MASVS-CRYPTO-2 · [KEYCHAIN] · [CRYPTOKIT] |
| AUTH-1 | Secure auth/authz protocols | Token issuance/refresh/rotation wiring (pairs with the token-refresh trace); session invalidation on logout = Keychain item deletion **and** server-side revoke, not just navigation. Passkeys where present: `ASAuthorizationPlatformPublicKeyCredential` + the `webcredentials` AASA association — verify the served AASA file, not just the client code. Refs: MASVS-AUTH-1 · [MASVS] |
| AUTH-2 | Secure local authentication | **A bare boolean back from `LAContext.evaluatePolicy` gating UI is the finding** — biometric auth must be **bound to a Keychain item** via `SecAccessControl` with `.biometryCurrentSet` (the CryptoObject-binding analogue): the protected secret is only released on successful biometry and re-enrolled biometrics invalidate it. Check `evaluatedPolicyDomainState` change detection where the app tracks enrolment itself; note `.deviceOwnerAuthentication` (passcode fallback) vs `.deviceOwnerAuthenticationWithBiometrics` against product intent. Refs: MASVS-AUTH-2 · [LOCALAUTH] · [KEYCHAIN] |
| AUTH-3 | Extra auth for sensitive ops | Step-up auth before payments/credential changes — trace one sensitive flow end-to-end and quote where the step-up is enforced (client *and* server) |
| NETWORK-1 | All traffic secured | `NSAppTransportSecurity` in every target's `Info.plist`: `NSAllowsArbitraryLoads` (+`InWebContent`/`ForMedia`/`LocalNetworking` carve-outs) and each `NSExceptionDomains` entry (`NSExceptionAllowsInsecureHTTPLoads`, minimum-TLS keys); reconcile every exception vs the hosts the app actually calls; grep for `http://` base URLs in code and xcconfig. Refs: MASVS-NETWORK-1 · [ATS] |
| NETWORK-2 | Identity pinning (done safely) + request integrity for owned endpoints | **Grade in context — pinning is optional defense-in-depth, not mandatory; don't reward mere presence or punish mere absence.** _Present_ (`URLSessionDelegate` trust evaluation / TrustKit / Alamofire `ServerTrustManager` / `NSPinnedDomains` in Info.plist): verify it covers the **real hosts the app actually calls** (pinning hosts never called = Fail/theatre), has **≥1 backup pin**, and an **expiry or remotely-updatable path** so rotation can't brick installs without a release; a challenge handler that calls `completionHandler(.useCredential, …)` without evaluating `SecTrust` = **Critical** (the empty-TrustManager analogue). _Absent_: **not an automatic Fail** — OWASP/platform guidance now often discourages pinning (CT vs downtime risk; breaks under corporate TLS inspection); verify current stance at review time (protocol.md §13). Also: are **money-movement / credential-change requests signed or attested beyond a bearer token** (App Attest assertions — see RESILIENCE-1)? Put the safe-rotation implementation (SPKI, hybrid, signed remote pins + kill-switch, per [PINNING]) in the finding's PR comment and `verify_fixed_when`. Refs: MASVS-NETWORK-2 · [PINNING] · [MASVS] |
| PLATFORM-1 | Secure IPC | Entry-point audit: custom URL schemes (`CFBundleURLTypes`) vs universal links + AASA — schemes are claimable by any installed app, so sensitive flows over a bare scheme are graded; incoming-URL handling (`onOpenURL` / `application(_:open:)`) validated, no open-redirect or unvalidated parameter forwarding into WebViews/navigation; `LSApplicationQueriesSchemes` breadth; app extensions + App Groups — what crosses the shared container and at what protection class; entitlements review. Refs: MASVS-PLATFORM-1 · [MASTG] |
| PLATFORM-2 | Secure WebViews | `WKWebView` configuration: `allowFileAccessFromFileURLs` / `allowUniversalAccessFromFileURLs` preference flags, `loadFileURL(_:allowingReadAccessTo:)` scope, JS enabled for untrusted content; enumerate every `WKScriptMessageHandler` bridge and grade its trust of `postMessage` input (origin/host checks, capability exposed); `isInspectable` left true in Release. Refs: MASVS-PLATFORM-2 · [MASTG] |
| PLATFORM-3 | Secure UI usage | **Input privacy on sensitive fields:** `isSecureTextEntry` / `SecureField`, `textContentType` (`.password`/`.oneTimeCode`/`.newPassword`), autocorrection and spell-checking disabled (`autocorrectionType = .no`, `.autocorrectionDisabled()`) so the keyboard cache learns nothing — name the fields you checked and their actual state. **Pasteboard:** `UIPasteboard.general` writes of sensitive values — target `.localOnly` + expiry via `setItems(_:options:)`. **Screen capture — iOS has no `FLAG_SECURE` equivalent, say so:** grade what the app does instead — `UIScreen.isCaptured` / `capturedDidChangeNotification` observation, `userDidTakeScreenshotNotification` handling, and snapshot privacy (blur/cover on `sceneWillResignActive` so balances/PII don't persist in the app-switcher snapshot). Refs: MASVS-PLATFORM-3 · [MASTG] |
| CODE-1 | Up-to-date platform version | Xcode / base-SDK vs the **App Store minimum-SDK submission requirement + effective date — look it up at review time (protocol.md §13), don't assert from memory** (annual, typically late April; e.g. from 2026-04-28 uploads require Xcode 26 / the iOS 26 SDK); grade a toolchain below it as a **hard App Store submission gate** (dated finding), not merely "behind". Also note the `IPHONEOS_DEPLOYMENT_TARGET` spread. Feeds currency findings. Refs: MASVS-CODE-1 · [SUBMIT-REQS] |
| CODE-2 | Enforced app updates / incident response | Force-update mechanism and a remote **feature kill-switch** (remote-config-gated) — for a regulated/fintech app treat absence as a graded finding, and check the mechanism is wired, not just declared. **There is no release rollback on the App Store** — a bad build can only be fixed forward through review, which raises the value of kill-switches and phased release; call this out as a distinct risk. A **certificate-pinning kill-switch** is a specific case (see NETWORK-2): it must be **signed/authenticated** (an unauthenticated toggle is a one-switch bypass) and fail back to default PKI trust, never to disabled TLS validation |
| CODE-3 | No known-vulnerable components | Dependency versions vs known CVEs; SCA tooling in CI (Renovate/Dependabot cover SPM; osv-scanner reads `Package.resolved`); pairs with the dependency/currency review |
| CODE-4 | Input validation | SQL built by string concatenation (raw SQLite / FMDB + interpolation); deep-link/URL parameter handling (pairs with PLATFORM-1); unsafe deserialisation — `NSKeyedUnarchiver` without `requiresSecureCoding` / `unarchivedObject(ofClasses:)`; JS evaluation of remote strings. **Memory-unsafe surface:** Swift is memory-safe by default — what remains is `withUnsafe*`/`UnsafeMutablePointer` use and C/ObjC bridge code (`strcpy`/`memcpy` in vendored C): enumerate and grade that residual surface rather than asserting blanket safety |
| RESILIENCE-1 | Platform-integrity validation | Attestation and device-integrity wiring — read it, don't grep-match. **App Attest / DeviceCheck (`DCAppAttestService` key generation + attestation, assertions on sensitive requests) is the platform mechanism.** Also check verdicts are **enforced server-side**, not client-only (trivially bypassable). Jailbreak heuristics, where present: Cydia/`/private` sandbox-escape write test, `fork()` probe, suspicious dylibs via `_dyld_image_count`/`_dyld_get_image_name` — grade as best-effort signals (bypassable), never as a control that "prevents" anything. Refs: MASVS-RESILIENCE-1 · [APP-ATTEST] · [MASVS] |
| RESILIENCE-2 | Anti-tampering | App Store code-signing covers baseline integrity — grade what the app adds where the threat model warrants: bundle-integrity/self-checks, provisioning-profile presence checks (re-signing signal), and whether responses degrade gracefully vs brick the app for false positives |
| RESILIENCE-3 | Anti-static-analysis | Symbol stripping actually effective on Release (`DEPLOYMENT_POSTPROCESSING`/`STRIP_*` — pairs with the build-settings review); string/asset protection for genuinely sensitive constants. **Be honest about limits:** Swift/ObjC metadata keeps much recoverable and there is no R8/ProGuard analogue — commercial obfuscators exist but absence is contextual, not an automatic finding |
| RESILIENCE-4 | Anti-dynamic-analysis | Anti-debug: `ptrace(PT_DENY_ATTACH)`, `sysctl` `P_TRACED` checks, debugger/hook detection (Frida artefacts, injected dylib scans); confirm `get-task-allow` is false in Release entitlements; detection responses graded like RESILIENCE-2 (signals, server-visible, non-bricking) |
| PRIVACY-1 | Minimal data/resource access | `NS*UsageDescription` audit — every declared key maps to a real feature need (boilerplate/misleading purpose strings are transparency findings; missing key = runtime crash); entitlements and `UIBackgroundModes` breadth vs actual use |
| PRIVACY-2 | Prevent user identification | Identifier collection & linkage: IDFA (requires ATT authorisation — `ATTrackingManager.requestTrackingAuthorization` + `NSUserTrackingUsageDescription`; any tracking call before authorisation = Fail), IDFV, fingerprinting signals; tracking domains declared in the privacy manifest vs actually contacted (hosts the app actually calls). Refs: MASVS-PRIVACY-2 · [ATT] · [PRIVACY-MANIFEST] |
| PRIVACY-3 | Transparency | `PrivacyInfo.xcprivacy` present and truthful for the app **and** third-party SDKs (required-reason APIs declared with valid reason codes — enforcement dates move, verify protocol.md §13); nutrition-label consistency vs the SDKs actually found in the dependency inventory; `ITSAppUsesNonExemptEncryption` declared correctly. **Log hygiene:** `os_log`/`Logger` interpolations marked `privacy: .public` on sensitive values, and raw `print()`/`NSLog` of PII reaching Release builds. Refs: MASVS-PRIVACY-3 · [PRIVACY-MANIFEST] |
| PRIVACY-4 | User data control | Deletion/opt-out paths for collected data; in-app **account deletion** where accounts can be created (an App Store review requirement) — verify the flow deletes server-side data, not just the local session |

**OWASP Mobile Top 10 (2024) cross-map** (2024 is still the latest edition — as of mid-2026 there
is no newer Mobile Top 10; it is the awareness list, MASVS is the verification standard). Emit as
a compact table pointing each M-risk at the MASVS rows above rather than re-checking:
M1 Credentials→CRYPTO-2/AUTH-1 · M2 Supply Chain→CODE-3 · M3 Auth/Authz→AUTH-1/2/3 ·
M4 Input/Output Validation→CODE-4 · M5 Insecure Communication→NETWORK-1/2 ·
M6 Privacy→PRIVACY-1..4 · M7 Binary Protections→RESILIENCE-1..4 ·
M8 Misconfiguration→PLATFORM-1/STORAGE-2 · M9 Data Storage→STORAGE-1/2 · M10 Crypto→CRYPTO-1/2.

## Accessibility

- **Accessibility ([A11Y], [HIG]) — also per-component in the design-system audit above.** A
  static pass can't replace VoiceOver, but grade these against the code (a regulated/finance app
  faces WCAG-grade expectations): **touch targets** ≥ 44×44 pt (HIG minimum — flag icon-only
  buttons below it); **labels** — `accessibilityLabel`/`Value`/`Hint` on interactive elements,
  images/icons labelled or explicitly hidden (quote the ratio + offenders); **traits** —
  `.isHeader`/`.isButton` etc. so structure and role are announced; **Dynamic Type** —
  `@ScaledMetric` for metrics that should scale, no fixed `.font(.system(size:))` on body text, and
  layouts that survive AX sizes (truncation checked); **VoiceOver traversal order** on composite
  rows (`accessibilityElement(children: .combine)`, sort priority); **contrast** per WCAG;
  verification tooling: Accessibility Inspector + `XCUIApplication().performAccessibilityAudit()`
  in UI tests. Anything needing a device pass goes under "Unverified (needs a trace)" with the
  VoiceOver / Accessibility-Inspector run that would confirm it.

## Source registry (canonical URLs for Refs lines)

| Key | Source |
|---|---|
| [SWIFTUI-DATAFLOW] | https://developer.apple.com/documentation/swiftui/model-data — Apple's SwiftUI data-flow/model-data documentation (state ownership, observation, bindings) |
| [BACKYARD-BIRDS] | https://github.com/apple/sample-backyard-birds — Apple sample app (SwiftUI + SwiftData, multi-target) used here as the architecture consensus source |
| [FOOD-TRUCK] | https://github.com/apple/sample-food-truck — Apple sample app (SwiftUI app + widgets, shared model layer) |
| [SWIFT-CONCURRENCY] | https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/ — structured concurrency, actors, tasks (official language book) |
| [SWIFT6-MIGRATION] | https://www.swift.org/migration/documentation/migrationguide/ — Swift 6 / strict-concurrency migration guide (staging, Sendable) |
| [SPM] | https://www.swift.org/documentation/package-manager/ — Swift Package Manager documentation (products, dependency rules, Package.resolved) |
| [XCODE-BUILD] | https://developer.apple.com/documentation/xcode/build-settings-reference — canonical build-settings reference (optimisation, stripping, sandboxing) |
| [SWIFTLINT] | https://github.com/realm/SwiftLint — de-facto standard Swift linter |
| [HIG] | https://developer.apple.com/design/human-interface-guidelines — Apple Human Interface Guidelines (incl. 44 pt targets, platform conventions) |
| [A11Y] | https://developer.apple.com/documentation/accessibility — Apple accessibility documentation (labels/traits, Dynamic Type, audits) |
| [KEYCHAIN] | https://developer.apple.com/documentation/security/keychain-services — Keychain Services (accessibility classes, SecAccessControl) |
| [CRYPTOKIT] | https://developer.apple.com/documentation/cryptokit — CryptoKit (modern primitives, Secure Enclave key types) |
| [LOCALAUTH] | https://developer.apple.com/documentation/localauthentication — LocalAuthentication (LAContext, evaluatePolicy, domain state) |
| [ATS] | https://developer.apple.com/documentation/security/preventing-insecure-network-connections — App Transport Security and its exception keys |
| [APP-ATTEST] | https://developer.apple.com/documentation/devicecheck — DeviceCheck framework incl. App Attest (attestation is verified server-side) |
| [PRIVACY-MANIFEST] | https://developer.apple.com/documentation/bundleresources/privacy-manifest-files — PrivacyInfo.xcprivacy, required-reason APIs, tracking domains |
| [ATT] | https://developer.apple.com/documentation/apptrackingtransparency — App Tracking Transparency (IDFA authorisation) |
| [SUBMIT-REQS] | https://developer.apple.com/news/upcoming-requirements/ — App Store upcoming requirements (minimum Xcode/SDK submission gate + effective dates) |
| [LAUNCH-TIME] | https://developer.apple.com/documentation/xcode/reducing-your-app-s-launch-time — launch-time guidance (dyld/pre-main, measurement) |
| [APP-SIZE] | https://developer.apple.com/documentation/xcode/reducing-your-app-s-size — app-size guidance (thinning, size report, download vs install) |
| [MASVS] | https://mas.owasp.org/MASVS/ (v2.1.0) |
| [MASTG] | https://mas.owasp.org/MASTG/ (v2.0.0, 2026-06-30) — cite iOS techniques/tests generically unless a specific iOS test ID is verified |
| [PINNING] | https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html — OWASP Pinning Cheat Sheet (public-key/SPKI pins, backup pins, expiration safety-valve, when NOT to pin) |
| [TOP10-2024] | https://owasp.org/www-project-mobile-top-10/ |

<!-- Source links — keep in sync with the table above (primary URL per key) so [KEY] references
     render as links wherever this pack's content is pasted -->
[SWIFTUI-DATAFLOW]: https://developer.apple.com/documentation/swiftui/model-data
[BACKYARD-BIRDS]: https://github.com/apple/sample-backyard-birds
[FOOD-TRUCK]: https://github.com/apple/sample-food-truck
[SWIFT-CONCURRENCY]: https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/
[SWIFT6-MIGRATION]: https://www.swift.org/migration/documentation/migrationguide/
[SPM]: https://www.swift.org/documentation/package-manager/
[XCODE-BUILD]: https://developer.apple.com/documentation/xcode/build-settings-reference
[SWIFTLINT]: https://github.com/realm/SwiftLint
[HIG]: https://developer.apple.com/design/human-interface-guidelines
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
[TOP10-2024]: https://owasp.org/www-project-mobile-top-10/
