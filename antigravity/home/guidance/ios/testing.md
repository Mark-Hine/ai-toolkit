---
paths:
  - "**/*Tests/**"
  - "**/*Tests.swift"
  - "**/*Test.swift"
  - "**/*Spec.swift"
---

# Tests

- Framework per repo, named in its `AGENTS.md`: Swift Testing (`@Test`, `#expect`, `#require`, `@Suite`) for new tests
  where the repo has adopted it; otherwise XCTest. Add Quick/Nimble only inside a file that already uses it. UI tests
  (`XCUIApplication`) and performance tests stay in XCTest.
- Async: `async` test functions with `await`; Swift Testing `confirmation` or XCTest `fulfillment(of:)` for callbacks.
  No `sleep`, `Thread.sleep`, `Task.sleep` or generous waits to "let it settle"; inject a `Clock` and advance it.
- Tests run in parallel by default (Swift Testing) or per scheme setting: no shared mutable statics, `UserDefaults.standard`
  or Keychain without an isolated suite/service name; mark truly serial suites `.serialized` and say why.
- Seams: fake the protocol the code depends on (repository, clock, `URLProtocol` stub); do not hit the network or Keychain.
- Bug fixes start with a failing test that reproduces the report, then the fix, then the same test green. Quote both runs.
- Run targeted: `xcodebuild test -workspace <ws> -scheme "<test scheme>" -destination '<sim>' -only-testing:<Target>/<Suite>`
  using the command form from the project's `AGENTS.md`; summarise with `xcrun xcresulttool get test-results summary`.
  If the project lists pre-existing failing or non-compiling tests, report them as pre-existing; do not fix them inside another ticket.
- Add a test for whatever you change in a view model, service or repository, even if the surrounding type has none.
- Only add UI tests when the ticket asks or the project already has that target; where a UI test exists for the screen,
  add `performAccessibilityAudit()` to it.
