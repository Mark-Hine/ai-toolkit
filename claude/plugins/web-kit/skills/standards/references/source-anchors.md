---
verified: 2026-10-08
sources: inline
---

# Web source anchors

Each URL `official-docs.md` cites, pinned to its page and to a sentence from it. Use the registry to find a page and these anchors to quote it. Do not fetch a page to grade a rule. Volatile facts, such as framework versions and changed defaults, are still looked up when they are used. `tools/source_anchors.py` in the ai-toolkit repo confirms every quote against the live page and records the date, and that repo's `docs/source-anchors.md` describes the format.

Quotes are verbatim and short, and each names its page. Copyright stays with the source's owner.

### WEB-REACT-LEARN
- URL: https://react.dev/learn
- Quote: "This page will give you an introduction to 80% of the React concepts that you will use on a daily basis."
- Confirmed: 2026-10-08 (html)

### REACT-RULES-OF-HOOKS
- URL: https://react.dev/reference/rules/rules-of-hooks
- Quote: "Instead, always use Hooks at the top level of your React function, before any early returns."
- Confirmed: 2026-10-08 (html)

### REACT-PURE
- URL: https://react.dev/reference/rules/components-and-hooks-must-be-pure
- Quote: "You always get the same result every time you run it with the same inputs"
- Confirmed: 2026-10-08 (html)

### REACT-NO-EFFECT
- URL: https://react.dev/learn/you-might-not-need-an-effect
- Quote: "You don’t need Effects to transform data for rendering."
- Confirmed: 2026-10-08 (html)

### REACT-LISTS
- URL: https://react.dev/learn/rendering-lists
- Quote: "Similarly, do not generate keys on the fly"
- Confirmed: 2026-10-08 (html)

### WEB-NEXT-DOCS
- URL: https://nextjs.org/docs
- Quote: "Next.js is a React framework for building full-stack web applications."
- Confirmed: 2026-10-08 (html)

### NEXT-SERVER-CLIENT
- URL: https://nextjs.org/docs/app/getting-started/server-and-client-components
- Quote: "When you need interactivity or browser APIs, you can use Client Components to layer in functionality."
- Confirmed: 2026-10-08 (html)

### NEXT-ENV
- URL: https://nextjs.org/docs/app/guides/environment-variables
- Quote: "It will be inlined into any JavaScript sent to the browser."
- Confirmed: 2026-10-08 (html)

### NEXT-LOADING
- URL: https://nextjs.org/docs/app/api-reference/file-conventions/loading
- Quote: "you can show an instant loading state from the server while the content of a route segment streams in."
- Confirmed: 2026-10-08 (html)

### NEXT-ERROR
- URL: https://nextjs.org/docs/app/api-reference/file-conventions/error
- Quote: "An error file allows you to handle unexpected runtime errors and display fallback UI."
- Confirmed: 2026-10-08 (html)

### TS-STRICT
- URL: https://www.typescriptlang.org/tsconfig/strict.html
- Quote: "The strict flag enables a wide range of type checking behavior that results in stronger guarantees of program correctness."
- Confirmed: 2026-10-08 (html)

### TS-NARROWING
- URL: https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- Quote: "This means you can use narrowing and rely on never turning up to do exhaustive checking in a switch statement."
- Confirmed: 2026-10-08 (html)

### TS-FUNCTIONS
- URL: https://www.typescriptlang.org/docs/handbook/2/functions.html
- Quote: "This is similar to the any type, but is safer because it’s not legal to do anything with an unknown value:"
- Confirmed: 2026-10-08 (html)

### RTL-QUERIES
- URL: https://testing-library.com/docs/queries/about/
- Quote: "your test should resemble how users interact with your code (component, page, etc.) as much as possible."
- Confirmed: 2026-10-08 (html)

### USER-EVENT
- URL: https://testing-library.com/docs/user-event/intro/
- Quote: "Testing Library's built-in fireEvent is a lightweight wrapper around the browser's low-level dispatchEvent API, which allows developers to trigger any event on any element."
- Confirmed: 2026-10-08 (html)

### VITEST-GUIDE
- URL: https://vitest.dev/guide/
- Quote: "is a next generation testing framework powered by Vite."
- Confirmed: 2026-10-08 (html)

### PW-BEST-PRACTICES
- URL: https://playwright.dev/docs/best-practices
- Quote: "By using web first assertions Playwright will wait until the expected condition is met."
- Confirmed: 2026-10-08 (html)

### PW-SCREENSHOTS
- URL: https://playwright.dev/docs/screenshots
- Quote: "Full page screenshot is a screenshot of a full scrollable page, as if you had a very tall screen and the page could fit it entirely."
- Confirmed: 2026-10-08 (html)

### MDN-ARIA
- URL: https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA
- Quote: "There is a saying "No ARIA is better than bad ARIA.""
- Confirmed: 2026-10-08 (html)
