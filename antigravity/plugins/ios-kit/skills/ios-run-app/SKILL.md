---
name: ios-run-app
description: "Build, install, launch and screenshot an iOS debug scheme on a simulator via xcodebuild and xcrun simctl."
---

Read the project AGENTS.md (or GEMINI.md) and applicable guidance first. Fall back to CLAUDE.md if AGENTS.md is absent. Follow global rules for optional tools, specialist subagents and Git actions.

# Run the app: the user request

Defaults: simulator named in `~/.gemini/config/machine.md` or project instructions, otherwise a compatible available iPhone from `xcrun simctl list devices available`;
project's workspace, default debug scheme and bundle id from its `AGENTS.md`. Never guess a scheme name; quote `xcodebuild -list`.

1. `xcodebuild -version`; `xcodebuild -list -workspace <ws>` and confirm scheme exists. CocoaPods repos: run `pod install`
   first when `Pods/` is missing or `Podfile.lock` changed; SwiftPM-only repos need nothing.
2. `xcrun simctl list devices available`; record selected simulator UDID and use it for every subsequent command; if simulator is not `Booted`: `xcrun simctl boot <udid>`, then
   `xcrun simctl bootstatus <udid> -b`. `open -a Simulator` when caller wants to watch.
3. Build: `xcodebuild build -workspace <ws> -scheme "<scheme>" -destination 'platform=iOS Simulator,id=<udid>'
   -derivedDataPath <scratchpad>/DerivedData -quiet`. On failure re-run without `-quiet` and quote first `error:` lines.
4. Locate product: `xcodebuild -showBuildSettings … | grep -E 'BUILT_PRODUCTS_DIR|FULL_PRODUCT_NAME'`.
   Install and launch: `xcrun simctl install <udid> <path>.app`; `xcrun simctl launch <udid> <bundle id>` (prints pid).
   Deep link: `xcrun simctl openurl <udid> <url>`.
5. On first screen: `xcrun simctl io <udid> screenshot <scratchpad>/<simulator>-<scheme>-<screen>.png`.
   For accessibility or dark-mode checks: `xcrun simctl ui <udid> content_size accessibility-extra-large`,
   `xcrun simctl ui <udid> appearance dark`, then screenshot again.
6. Report: simulator name, UDID and OS; scheme and configuration; `.app` path; launch pid; screenshot path(s); and if
   app crashed, last 30 lines of `xcrun simctl spawn <udid> log show --last 2m --predicate 'processImagePath CONTAINS "<App>"'`.

Do not erase or delete simulators, or change privacy permissions, without user authorization. Record existing appearance and content-size settings before a visual check and restore them afterwards. Plain simctl cannot tap or type; use existing XCUITests or an available UI automation tool, otherwise mark interaction checks Unverified.
