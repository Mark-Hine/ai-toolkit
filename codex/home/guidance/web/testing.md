---
verified: 2026-10-08
sources:
  - https://testing-library.com/docs/queries/about/
  - https://testing-library.com/docs/user-event/intro/
  - https://playwright.dev/docs/best-practices
  - https://playwright.dev/docs/screenshots
  - https://vitest.dev/guide/
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/*.spec.tsx"
  - "**/__tests__/**"
  - "**/e2e/**"
---

# Tests (web repos)

- The runners come from the project's `AGENTS.md`: Vitest or Jest with Testing Library for unit and component tests,
  and Playwright for end-to-end journeys. Add a runner only when the ticket asks for one.
- Query the way a user finds things: `getByRole` with a name first, then `getByLabelText` and `getByText`. Use
  `getByTestId` only when nothing a user can perceive identifies the element.
- Drive interactions with `user-event` rather than `fireEvent`, so focus, keyboard and pointer events happen in order.
- Fake the network at the boundary with the project's tool, such as MSW or Playwright's `page.route`. Do not mock the
  component's own modules and do not call real services.
- No fixed waits such as `setTimeout` or `waitForTimeout`. Await `findBy` queries or Playwright's web-first
  assertions, which retry until the condition holds. Use fake timers for time-based logic.
- Playwright locators use the roles, labels and text the user sees, not CSS or XPath tied to the markup.
- Bug fixes start with a failing test that reproduces the report, then the fix, then the same test green. Quote both runs.
- Run targeted: `npx vitest run <file>`, `npx jest <file>`, `npx playwright test <file>`, or the project's script
  with a file filter. Updating snapshots needs the user's approval and a reason in the report.
- Add a test for whatever you change in a hook, a data function or a component's behaviour, even if the file has none.
