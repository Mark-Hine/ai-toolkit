---
paths:
  - "**/src/test/**"
  - "**/src/androidTest/**"
  - "**/journeys/**"
---

# Tests (Android repos)

- What a change must carry: ViewModel / use case / repository change → unit test in the same module. New or changed screen →
  Compose UI-behaviour test if the repo already has Robolectric + Compose test infra, otherwise previews plus a journey.
  Bug fix → failing test first, then the fix, then green; quote both runs.
- Stack for new tests: JUnit 5, Kotest assertions, MockK, `kotlinx-coroutines-test` (`runTest`, injected `TestDispatcher`).
  Fakes over mocks for repositories and data sources; MockK only at true boundaries (SDKs, Android framework).
  No new Mockito/Hamcrest; no `Thread.sleep`; no `runBlocking`; tests share no static mutable state (parallel forks are on).
- Never `@Ignore`, delete, or loosen an assertion to go green. A failing pre-existing test is reported as pre-existing, with the
  project CLAUDE.md's known-broken list as the reference; it is not fixed inside another ticket.
- Run the narrowest test first (`./gradlew :<module>:test<Variant>UnitTest --tests '<FQCN>'`), then the module's unit tests.
  Quote the summary line as evidence.
- Screenshot tests only where the repo already has the tool (Roborazzi, Compose Preview Screenshot Testing, Paparazzi). Adding
  a test framework is its own ticket, done through the `testing-setup` skill, never inside a feature.
- End-to-end: journeys. Repos keep `journeys/<feature>.xml` in the Android CLI format (`android-cli` skill,
  `references/journeys.md`). After the emulator build, run the journey for the touched screen by driving `android layout` /
  `android screen` and paste the JSON per-action result. A FAILED action is a finding to report, not something to nudge into
  passing. A ticket that adds a screen adds a journey. Template and example: `android-kit:standards` → `references/testing.md`.
