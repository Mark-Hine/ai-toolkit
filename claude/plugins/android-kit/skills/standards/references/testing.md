# Testing: expectations, tooling, journeys

Rule: `claude-rules/android/testing.md`. This file holds the reasoning, the pyramid, and the journey template.

## Pyramid per change

| Change | Required | Nice to have |
|---|---|---|
| ViewModel / use case / repository | Unit test in the module (`runTest`, fakes, injected dispatcher) | Turbine-style flow assertions if the repo has them |
| New or changed Compose screen | Preview(s) for each `UiState`; journey for the flow | Compose UI-behaviour test (Robolectric) if infra exists; screenshot test if the repo has a tool |
| Bug fix | Failing test reproducing the report, then green | Journey step covering the symptom |
| Dependency / toolchain uplift | Existing tests that compiled at baseline; runtime launch check | Journey on the 16 KB AVD when native code is involved |

Sources: developer.android.com/training/testing (fundamentals, what to test), Now in Android `core/testing` (fakes over
mocks, `TestDispatcher` rule), `testing-setup` skill (Google, infra install order: DI → unit → UI → screenshot → e2e).

## Why fakes over mocks
Repositories and data sources are owned code with small interfaces; a fake exercises the real contract and survives refactors,
while a mock encodes call order and breaks on every internal change. Mocks stay for third-party SDKs and framework types.

## Journeys (Android CLI end-to-end)
Format and evaluation rules: `~/.claude/skills/android-cli/references/journeys.md`. The agent drives the app with
`android layout` / `android layout --diff` / `android screen capture` and adb, evaluates each `<action>` literally, and reports
JSON with `PASSED` / `FAILED` / `SKIPPED` per action. Journeys are checked into the repo under `journeys/`.

Conventions:
- One file per user flow, `journeys/<feature>-<flow>.xml`; `<description>` states preconditions (logged-in test account,
  flavour, AVD).
- Actions are literal and single-purpose: one tap or one verification each. "Verify" actions inspect only, never scroll.
- Actions are unconditional. One-off dialogs (What's-new, permission prompts) are handled in the `<description>` precondition
  ("dismiss X before starting"), never as an `If shown…` action, because the evaluator executes steps literally.
- Journeys assert behaviour, not pixels; screenshot tests own pixels.
- A FAILED action is a finding for the report. Do not edit the journey to make it pass unless the product behaviour changed
  deliberately in the same ticket.

Template:
```xml
<journey name="Offers - browse">
  <description>
    Precondition: dev flavour on the default phone AVD, logged in with a test account that has at least one offer.
    Verifies the Offers screen opens from Home, shows a featured offer, and returns to Home.
  </description>
  <actions>
    <action>Verify the app is on the Home screen</action>
    <action>Tap the Offers tile</action>
    <action>Verify the Offers screen is shown with a featured offer card</action>
    <action>Tap the back/navigation-up button in the top bar</action>
    <action>Verify the app is on the Home screen</action>
  </actions>
</journey>
```

Running one: `/android-kit:run-app <avd> <flavour>`, then evaluate the journey per the android-cli reference and paste the JSON
summary into the task report.
