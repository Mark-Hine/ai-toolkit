---
verified: 2026-09-29
sources:
  - https://developer.android.com/training/testing/local-tests
  - https://developer.android.com/training/testing/local-tests/robolectric
  - https://developer.android.com/develop/ui/compose/testing
paths:
  - "**/src/test/**"
  - "**/src/androidTest/**"
  - "**/journeys/**"
---

# Tests (Android repos)

- What a change must carry: ViewModel / use case / repository change → unit test in the same module. New or changed screen →
  Compose UI-behaviour test if the repo already has Robolectric + Compose test infra, otherwise previews plus a journey.
  Bug fix → failing test first, then the fix, then green; quote both runs.
- Stack for new tests follows the module. Plain JVM unit tests use JUnit 5 where the module runs the JUnit Platform. Robolectric tests, Compose UI tests (`createComposeRule`) and instrumented tests run on JUnit 4, through the Vintage engine when a module mixes both. Kotest assertions, MockK and `kotlinx-coroutines-test` (`runTest`, injected `TestDispatcher`) work on either.
  Fakes over mocks for repositories and data sources; MockK only at true boundaries (SDKs, Android framework).
  No new Mockito/Hamcrest; no `Thread.sleep`; no `runBlocking`; tests share no static mutable state, because Gradle may run test classes in parallel forks.
- Never `@Ignore`, delete, or loosen an assertion to go green. A failing pre-existing test is reported as pre-existing, with the
  project AGENTS.md's known-broken list as the reference; it is not fixed inside another ticket.
- Run the narrowest test first (`./gradlew :<module>:test<Variant>UnitTest --tests '<FQCN>'`), then the module's unit tests.
  Quote the summary line as evidence.
- Screenshot tests only where the repo already has the tool (Roborazzi, Compose Preview Screenshot Testing, Paparazzi). Adding
  a test framework is its own ticket, done through the `testing-setup` skill, never inside a feature.
- End-to-end: journeys. Repos keep `journeys/<feature>.xml` in the Android CLI format (`android-cli` skill,
  `references/journeys.md`). After the emulator build, run the journey for the touched screen by driving `android layout` /
  `android screen` and paste the JSON per-action result. A FAILED action is a finding to report, not something to nudge into
  passing. A ticket that adds a screen adds a journey. Template and example: `android-standards` → `references/testing.md`.
