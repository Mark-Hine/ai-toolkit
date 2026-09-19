---
name: android-run-app
description: "Build, install, launch and screenshot a house Android debug variant on an emulator via the Android CLI."
---

Read the project AGENTS.md (or GEMINI.md) and applicable guidance first. Fall back to CLAUDE.md if AGENTS.md is absent. Follow global rules for optional tools, specialist subagents and Git actions.

# Run the app: the user request

Defaults: default phone AVD named in `~/.gemini/config/machine.md`; project's default debug flavour and application id
from its `AGENTS.md`. Load the `android-cli` skill if any command below is unfamiliar.

1. `android info`; confirm the compile SDK platform is installed (`ls $ANDROID_HOME/platforms`; the `android sdk list` pattern filter misses `android-37.0`-style names).
2. `android emulator list`; if the AVD is not running, `android emulator start <avd>` and wait until `adb devices` shows `device`.
3. Build: `./gradlew :app:assemble<Flavour>Debug` (capitalise the flavour; omit flavour segment if the project has none).
4. Install and launch: `android run --apks <apk path from the build output> --device <serial>` (never `--debug`: it makes
   the app wait for a debugger and the screen shows "Waiting For Debugger"); if launch does not come to the foreground,
   `adb shell monkey -p <applicationId> -c android.intent.category.LAUNCHER 1`. Flavoured apps suffix the id (e.g. `.sit`).
5. On the first screen, `android screen`; save the PNG to the session scratchpad as `<avd>-<flavour>-<screen>.png`.
   `android layout` when the caller needs the view tree.
6. Report: device serial and AVD, variant, APK path, launch result, screenshot path(s), and the last 30 lines of
   `adb logcat -d -s AndroidRuntime` if anything crashed.

Use configured approval policy for device commands. A request to run the app authorizes its normal build, install and launch steps.
