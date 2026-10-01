---
name: run-app
description: Build, install, launch and screenshot a house Android debug variant on an emulator via the Android CLI.
argument-hint: "[avd] [flavour]"
allowed-tools: Bash(android info*), Bash(android emulator list*), Bash(android emulator start *), Bash(android run *), Bash(android screen *), Bash(android layout*), Bash(./gradlew :app:assemble*), Bash(adb devices*), Bash(adb logcat *), Bash(adb shell monkey *)
---

# Run the app: $ARGUMENTS

Defaults: the default phone AVD named in `~/.claude/CLAUDE.md`, and the project's default debug flavour and application id
from its `CLAUDE.md`. Load the `android-cli` skill if any command below is unfamiliar.

1. `android info`, then confirm the compile SDK platform is installed (`ls $ANDROID_HOME/platforms`, because the `android sdk list` pattern filter misses `android-37.0`-style names).
2. `android emulator list`. If the AVD is not running, `android emulator start <avd>` and wait until `adb devices` shows `device`.
3. Build: `./gradlew :app:assemble<Flavour>Debug` (capitalise the flavour, and omit the flavour segment if the project has none).
4. Install and launch: `android run --apks <apk path from the build output> --device <serial>` (never `--debug`, because it makes
   the app wait for a debugger and the screen shows "Waiting For Debugger"). If the launch does not come to the foreground,
   `adb shell monkey -p <applicationId> -c android.intent.category.LAUNCHER 1`. Flavoured apps suffix the id (e.g. `.sit`).
5. On the first screen, `android screen`, then save the PNG to the session scratchpad as `<avd>-<flavour>-<screen>.png`.
   `android layout` when the caller needs the view tree.
6. Report: device serial and AVD, variant, APK path, launch result, screenshot path(s), and the last 30 lines of
   `adb logcat -d -s AndroidRuntime` if anything crashed.

Device commands outside `allowed-tools`, such as uninstall or emulator removal, use the approval policy and prompt. A request to run the app authorizes its normal build, install and launch steps.
