---
verified: 2026-10-19
sources: inline
---

# Journeys

A journey is a user flow written as plain-language steps in XML, which a verifier agent runs against the live app on an Android emulator, an iOS simulator or a browser. The same format serves all 3 platforms. Journeys are the acceptance check that a person could follow by hand. Project test code, such as Compose UI tests, XCUITest and Playwright specs, stays the regression suite, and a journey never replaces a test the project already has.

The format is Google's Android CLI journey format. For Android, when the `android-cli` skill is installed, its `references/journeys.md` is the authority for the evaluation rules. This file adds the house conventions, the result shape and the drivers for all 3 platforms.

## File and naming

- Keep journeys in the app repo under `journeys/`, one file per user flow, named `journeys/<feature>-<flow>.xml`.
- `<description>` states the preconditions: the build or flavour, the device or viewport, the test account and the data it needs, and any one-off dialog to dismiss before starting.
- A ticket that adds a screen adds a journey for it, unless a project end-to-end test, such as a Playwright spec or an XCUITest, already covers the flow. A ticket that changes a flow updates its journey in the same change.

```xml
<journey name="Offers - browse">
  <description>
    Precondition: debug build on the default phone device, logged in with a test account that has at least one offer.
    Verifies the Offers screen opens from Home, shows a featured offer, and returns to Home.
  </description>
  <actions>
    <action>Verify the app is on the Home screen</action>
    <action>Tap the Offers tile</action>
    <action>Verify the Offers screen is shown with a featured offer card</action>
    <action>Tap the back button in the top bar</action>
    <action>Verify the app is on the Home screen</action>
  </actions>
</journey>
```

## Writing actions

- Each action is literal and does one thing, either one interaction or one verification.
- An action that starts with "Verify" or "Check" inspects the current screen only. It never scrolls, taps or types.
- Actions are unconditional. Handle a one-off dialog, such as a permission prompt or a What's new sheet, in the `<description>` precondition, never as an "If shown" action, because the evaluator runs every step as written.
- Name elements by what a person sees or what assistive technology announces, such as a button label, a heading or a field label. Avoid coordinates, view ids and CSS selectors, so one journey reads the same on every platform.
- Journeys assert behaviour, not pixels. Screenshot tests own pixels.

## Evaluating a journey

1. Perform the precondition in `<description>` first. A precondition the verifier cannot meet, such as a missing test account, is a finding and the journey does not start.
2. Run the actions in order, one at a time. Split an action that names several steps into its parts and run each.
3. Do exactly what the action says, even when the intent seems different. If the action cannot be performed as written, it is FAILED.
4. If the app crashes, exits or freezes, the current action is FAILED.
5. After the first FAILED action, mark every later action SKIPPED.
6. A FAILED action is a finding for the caller. Never edit the journey to make it pass, unless the same ticket changed the product behaviour on purpose.

## Drivers and fallbacks

The driver is the tool that reads the screen and performs input. Each verifier tries its drivers in order and uses the first one available. A missing driver never stops the run, and it never turns a step into a pass.

- The verifier never asks. It lists a missing driver and its install command under Findings and continues with the next driver. The caller tells the user about it once per session, never once per journey, and a "no" holds for the rest of the session.
- When the project instructions name a choice for a platform, such as "iOS journeys: no interaction driver", follow it and do not ask.
- Never install a driver. Give the install command from the kit's references and continue with the next driver.
- With only a fallback driver, run every action it can still perform. Mark the actions it cannot perform SKIPPED with the comment "no driver". Once a skipped action would have changed the screen, mark every later action SKIPPED with the comment "no driver" as well, because the app is no longer in the state the journey expects.
- A SKIPPED action is never reported as PASSED or FAILED, and a journey with SKIPPED actions is reported as Unverified, not as passed.

| Platform | Preferred driver | Fallback | Last resort |
| --- | --- | --- | --- |
| Android | `android input` with selectors from `android layout` | Android SDK tools: `adb shell input`, `adb shell uiautomator dump /dev/tty` and `adb exec-out screencap -p` | None, because the SDK must exist to build the app. Without a running emulator the whole journey is Unverified |
| iOS | A simulator control tool in the session, then the AXe CLI | The project's XCUITest for the flow, when one exists | Launch, deep links with `xcrun simctl openurl` and screenshots. Verify actions on a screen a deep link reaches still run, and tap and type actions are SKIPPED |
| Web | The project's Playwright spec for the flow, then the Playwright CLI or a browser tool in the session | `npx playwright screenshot --channel chrome`, when the project has Playwright | A headless Chrome screenshot. Interaction actions are SKIPPED |

The verifier for each kit holds the exact commands for its drivers.

## Result

Report each journey as one JSON block, followed by a one-line verdict and the screenshot paths. `driver` names the driver that ran, or `none`.

```json
{
  "journey": "Offers - browse",
  "driver": "android input",
  "results": [
    {"action": "Verify the app is on the Home screen", "status": "PASSED", "commands": ["android layout"], "comment": "Home title and Offers tile present"},
    {"action": "Tap the Offers tile", "status": "FAILED", "commands": ["android input --device=emulator-5554 tap text=Offers,clickable=true --match=single --wait=3000"], "comment": "No matching elements"},
    {"action": "Verify the Offers screen is shown with a featured offer card", "status": "SKIPPED", "commands": [], "comment": "after a failed action"}
  ]
}
```

`status` is `PASSED`, `FAILED` or `SKIPPED`. `comment` gives the evidence observed, or the reason for a skip, which is either "after a failed action" or "no driver".
