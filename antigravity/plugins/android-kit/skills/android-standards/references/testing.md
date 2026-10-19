---
verified: 2026-09-29
sources: inline
---

# Testing: expectations, tooling, journeys

Rule: the android-kit testing rule. This file holds the reasoning and the pyramid. The journey contract is in `references/journeys.md`.

## Pyramid per change

| Change | Required | Nice to have |
|---|---|---|
| ViewModel / use case / repository | Unit test in the module (`runTest`, fakes, injected dispatcher) | Turbine-style flow assertions if the repo has them |
| New or changed Compose screen | Preview(s) for each `UiState` and a journey for the flow | Compose UI-behaviour test (Robolectric) if infra exists, and a screenshot test if the repo has a tool |
| Bug fix | Failing test reproducing the report, then green | Journey step covering the symptom |
| Dependency / toolchain uplift | Existing tests that compiled at baseline and a runtime launch check | Journey on the 16 KB AVD when native code is involved |

Sources: developer.android.com/training/testing (fundamentals, what to test), Now in Android `core/testing` (fakes over
mocks, `TestDispatcher` rule), `testing-setup` skill (Google, infra install order: DI → unit → UI → screenshot → e2e).

## Why fakes over mocks
Repositories and data sources are owned code with small interfaces. A fake exercises the real contract and survives refactors,
while a mock encodes call order and breaks on every internal change. Mocks stay for third-party SDKs and framework types.

## Journeys (Android CLI end-to-end)
Format, conventions, evaluation, drivers and the result shape: `references/journeys.md` in this skill, which follows Google's
journey format in the discovered `android-cli` skill's `references/journeys.md`. Journeys are checked into the repo under
`journeys/`, and a ticket that adds a screen adds one.

Running one: `/android-run-app <avd> <flavour> <journey>`, which hands the journey to the `android-verifier` agent.
It drives the app with `android layout` and `android input`, and returns the JSON result and screenshot paths for the task report.

## SDK-only fallback

When `android input --help` fails, because the `android` command is missing or predates `android input`, follow `references/journeys.md` with the Android SDK tools as the driver. Drive the device with `adb shell input` and inspect the UI hierarchy with `adb shell uiautomator dump /dev/tty`. That dump exits 137 while the Android CLI's helper holds UI automation, so run `adb shell am force-stop com.android.cli.interact.instrumentation` first in that case. The verifier's command guard blocks `adb exec-out screencap -p`, because saving its output needs a redirect, so ask the caller to capture screenshots with it into the scratch directory. Ask the caller the same way for any other artifact the guard does not allow. Set `driver` to `adb` in the result. Report missing devices or inputs as Unverified rather than claiming Android CLI verification.
