---
name: run-app
description: Build, install, launch and screenshot an iOS debug scheme on a simulator via xcodebuild and xcrun simctl.
disable-model-invocation: true
argument-hint: "[simulator name] [scheme]"
allowed-tools: Bash(xcodebuild *), Bash(xcrun *), Bash(open -a Simulator*), Bash(pod install*)
---

# Run the app: $ARGUMENTS

Defaults: the simulator named in `~/.claude/CLAUDE.md` (fallback: the newest iPhone in `xcrun simctl list devices available`);
the project's workspace, default debug scheme and bundle id from its `CLAUDE.md`. Never guess a scheme name; quote `xcodebuild -list`.

1. `xcodebuild -version`; `xcodebuild -list -workspace <ws>` and confirm the scheme exists. CocoaPods repos: run `pod install`
   first when `Pods/` is missing or `Podfile.lock` changed; SwiftPM-only repos need nothing.
2. `xcrun simctl list devices available`; if the simulator is not `Booted`: `xcrun simctl boot "<name>"`, then
   `xcrun simctl bootstatus "<name>" -b`. `open -a Simulator` when the caller wants to watch.
3. Build: `xcodebuild build -workspace <ws> -scheme "<scheme>" -destination 'platform=iOS Simulator,name=<name>'
   -derivedDataPath <scratchpad>/DerivedData -quiet`. On failure re-run without `-quiet` and quote the first `error:` lines.
4. Locate the product: `xcodebuild -showBuildSettings … | grep -E 'BUILT_PRODUCTS_DIR|FULL_PRODUCT_NAME'`.
   Install and launch: `xcrun simctl install booted <path>.app`; `xcrun simctl launch booted <bundle id>` (prints the pid).
   Deep link: `xcrun simctl openurl booted <url>`. Permissions: `xcrun simctl privacy booted grant <service> <bundle id>`.
5. On the first screen: `xcrun simctl io booted screenshot <scratchpad>/<simulator>-<scheme>-<screen>.png`.
   For accessibility or dark-mode checks: `xcrun simctl ui booted content_size accessibility-extra-large`,
   `xcrun simctl ui booted appearance dark`, then screenshot again.
6. Report: simulator name, UDID and OS; scheme and configuration; `.app` path; launch pid; screenshot path(s); and if the
   app crashed, the last 30 lines of `xcrun simctl spawn booted log show --last 2m --predicate 'processImagePath CONTAINS "<App>"'`.

Mutating simulator commands (`erase`, `delete`, `privacy`) prompt for permission; that is intended.
