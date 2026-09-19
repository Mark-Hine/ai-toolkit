# Per-repo `AGENTS.md` template for iOS repos

Copy to `<repo>/AGENTS.md`, replace every `<…>`, delete lines that do not apply. Keep it under ~60 lines with the hard
rules in the first 40; repo facts only, no tutorials (the shared `ios-*` skills and `~/.codex/guidance/ios/` carry conventions).
Personal or temporary notes go in `.local/agent-notes.md` (gitignored).

```markdown
# <repo-name>

<one-line product description>, bundle id `<com.example.app>`, Azure DevOps `<org>/<project>/<repo>`.

## Never (hooks enforce the push, lock-file and secret-file rules)
- Edit `GoogleService-Info.plist`, `*.entitlements`, `ExportOptions.plist`, `<Secrets file>` or signing settings in
  `<release.xcconfig / project.pbxproj>`. Commit an ATS exception (`NSAllowsArbitraryLoads`, `NSExceptionDomains`) without a ticket that says so.
- Add a dependency outside `<Package.swift | project.pbxproj package list | Podfile>`; edit `Package.resolved` or `Podfile.lock` by hand.
- Change `IPHONEOS_DEPLOYMENT_TARGET`, `SWIFT_VERSION` or `SWIFT_STRICT_CONCURRENCY` outside an explicit uplift ticket.
- Store tokens or PII in `UserDefaults`; Keychain items below `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`.
- <repo-specific never, e.g. "Subclass <LegacyBaseViewController> for new screens; use SwiftUI in <DesignSystem>.">
- Fix the "known broken" items below inside another ticket; report them as pre-existing.

## Commands
- Build: `xcodebuild build -workspace <Name>.xcworkspace -scheme "<Scheme>" -destination 'platform=iOS Simulator,name=<Simulator>' -quiet`
  (schemes: `<Scheme Dev>`, `<Scheme SIT>`, `<Scheme UAT>`, `<Scheme Release>`; default debug scheme `<Scheme Dev>`).
- Tests: `xcodebuild test -workspace <Name>.xcworkspace -scheme "<Test scheme>" -destination '<same>' -only-testing:<TestTarget>/<Suite> -resultBundlePath <path>.xcresult`
  then `xcrun xcresulttool get test-results summary --path <path>.xcresult`. Framework: `<Swift Testing | XCTest | Quick+Nimble>`.
- Dependencies: `<xcodebuild -resolvePackageDependencies -workspace … -scheme … | pod install>`; lock files
  `<Name>.xcworkspace/xcshareddata/swiftpm/Package.resolved`, `Podfile.lock`.
- Lint/format: `<swiftlint --config .swiftlint.yml | swiftformat . | "not installed; format by hand">`.
- CI (`<azure-pipeline/*.yml | fastlane lanes>`) runs `<lane/scheme>`; run tests locally.

## Architecture map
- `<App target>`: `<pattern, e.g. layer-first Controllers/ ViewModels/ Services/; UIKit + SwiftUI>`. Entry `<App.swift | AppDelegate/SceneDelegate>`.
  Bases `<BaseViewController>`, `<BaseViewModel>`; composition root / DI `<file or "none, singletons via .shared">`.
- `<Design-system package>`: `<Theme/tokens type>`, components `<Prefix>Button`, `<Prefix>Card`…; preview helpers `<file>`.
- `<Data package/target>`: `<Network client> → <repositories/interactors> → <models>`; persistence `<Keychain wrapper, SwiftData, Core Data>`.
- New code: SwiftUI inside `<Design-system package>`; `@MainActor` `<@Observable | ObservableObject (deployment target < 17)>` models;
  data in `<package>` (repository → view model); async/await, not completion handlers or Combine, unless extending an existing Combine pipeline.
- Reference screen for state + one-shot events: `<path>` (`<XModel>`, `<XRoute>`, `<XScreen>`). Anti-example: `<path>` (<why>).

## Known broken on <default branch>
- <e.g. "`<Test target>` has N pre-existing failures in <Suite>; run only the suites you touched.">
- <e.g. "SwiftLint is not installed on dev machines; CI runs it via the pod.">
- <e.g. "`<Scheme>` needs manual signing env vars (`APPLE_CERTIFICATE_SIGNING_IDENTITY`) to archive; build with CODE_SIGNING_ALLOWED=NO.">

## Repo facts
- Xcode `<26.x>` (CI: `<version>`), Swift `<toolchain>` in language mode `<5 | 6>`, strict concurrency `<minimal | targeted | complete>`,
  deployment target iOS `<n>`, device family `<iPhone | iPhone+iPad>`. Dependencies: `<SwiftPM | CocoaPods | both>` (`<n>` pods, `<n>` packages).
- Environments: `<Dev/SIT/UAT/Prod>` selected by `<scheme | xcconfig | Info.plist key>`; Firebase plist per environment under `<path>`.
- Branches `feature|fix|task/<TICKET>-<slug>` off `<develop>`. Formal PR reviews: `$pr-review`.

## Compaction
Preserve: modified-file list, each xcodebuild/simctl command with pass/fail, open `ios-reviewer` findings, current ticket.
```
