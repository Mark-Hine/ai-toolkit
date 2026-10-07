---
verified: 2026-10-07
sources: inline
---

# Rule source anchors

Each URL the `sources:` lists of the rule files in `claude/home/rules/` and `shared/guidance/` cites, pinned to its page and to a sentence from it. Use the registry to find a page and these anchors to quote it. Do not fetch a page to grade a rule. Volatile facts, such as store deadlines and latest versions, are still looked up when they are used. `tools/source_anchors.py` in the ai-toolkit repo confirms every quote against the live page and records the date, and that repo's `docs/source-anchors.md` describes the format.

Quotes are verbatim and short, and each names its page. Copyright stays with the source's owner.

### UI
- URL: https://developer.android.com/develop/ui
- Quote: "Design a beautiful user interface using Android best practices."
- Confirmed: 2026-10-07 (html)

### STATE-HOISTING
- URL: https://developer.android.com/develop/ui/compose/state-hoisting
- Quote: "For some Compose UI element state, hoisting to the ViewModel might require special considerations."
- Confirmed: 2026-10-07 (html)

### TESTING
- URL: https://developer.android.com/develop/ui/compose/testing
- Quote: "Semantics give meaning to your UI, allowing tests to interact with specific elements."
- Confirmed: 2026-10-07 (html)

### STYLE-GUIDE
- URL: https://developer.android.com/kotlin/style-guide
- Quote: "A Kotlin source file is described as being in Google Android Style if and only if it adheres to the rules herein."
- Confirmed: 2026-10-07 (html)

### LOCAL-TESTS
- URL: https://developer.android.com/training/testing/local-tests
- Quote: "As such, it uses your local Java Virtual Machine (JVM), rather than an Android device to run tests."
- Confirmed: 2026-10-07 (html)

### ROBOLECTRIC
- URL: https://developer.android.com/training/testing/local-tests/robolectric
- Quote: "Robolectric was conceived as a way to enable "unit testing" in Android apps."
- Confirmed: 2026-10-07 (html)

### ALERT-ISPRESENTED-PRESENTING-ACTIONS-MES
- URL: https://developer.apple.com/documentation/swiftui/view/alert(_:ispresented:presenting:actions:message:)
- Quote: "When the user presses or taps one of the alert’s actions, the system sets this value to false and dismisses."
- Confirmed: 2026-10-07 (apple-json)

### WEB
- URL: https://developer.mozilla.org/en-US/docs/Web
- Quote: "Below you'll find links to our Web technology documentation."
- Confirmed: 2026-10-07 (html)

### STYLE
- URL: https://developers.google.com/style
- Quote: "This style guide provides editorial guidelines for writing clear and consistent technical documentation for an audience of software developers and other technical practitioners."
- Confirmed: 2026-10-07 (html)

### WIKIPEDIA-SIGNS-OF-AI-WRITING
- URL: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- Quote: "While some older writing displays some of the AI signs given in this list, the vastness of Wikipedia allows for these coincidences."
- Confirmed: 2026-10-07 (html)

### A-TO-Z-STYLE-GUIDE
- URL: https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/
- Quote: "Read the technical A to Z style guide for more information."
- Confirmed: 2026-10-07 (html)

### API-GUIDELINES-BACKWARD-COMPATIBILITY
- URL: https://kotlinlang.org/docs/api-guidelines-backward-compatibility.html
- Quote: "The most common motivation for creating a library is to expose functionality to a wider community."
- Confirmed: 2026-10-07 (html)

### API-GUIDELINES-SIMPLICITY
- URL: https://kotlinlang.org/docs/api-guidelines-simplicity.html
- Quote: "The fewer concepts your users need to understand and the more explicitly these are communicated, the simpler their mental model is likely to be."
- Confirmed: 2026-10-07 (html)

### CODING-CONVENTIONS
- URL: https://kotlinlang.org/docs/coding-conventions.html
- Quote: "Commonly known and easy-to-follow coding conventions are vital for any programming language."
- Confirmed: 2026-10-07 (html)

### DATA-CLASSES
- URL: https://kotlinlang.org/docs/data-classes.html
- Quote: "Data classes in Kotlin are primarily used to hold data."
- Confirmed: 2026-10-07 (html)

### WELCOME
- URL: https://learn.microsoft.com/en-us/style-guide/welcome/
- Quote: "Welcome to the Microsoft Writing Style Guide, your guide to writing style and terminology for all communication—whether an app, a website, or a white paper."
- Confirmed: 2026-10-07 (html)

### CLAUDE-PROMPTING-BEST-PRACTICES
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Quote: "When tracking structured information (like test results or task status), use JSON or other structured formats to help Claude understand schema requirements."
- Confirmed: 2026-10-07 (html)

### HOW-USERS-READ-ON-THE-WEB
- URL: https://www.nngroup.com/articles/how-users-read-on-the-web/
- Quote: "Users detested "marketese"; the promotional writing style with boastful subjective claims ("hottest ever") that currently is prevalent on the Web."
- Confirmed: 2026-10-07 (html)

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

### MDN-ARIA
- URL: https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA
- Quote: "There is a saying "No ARIA is better than bad ARIA.""
- Confirmed: 2026-10-08 (html)

### RTL-QUERIES
- URL: https://testing-library.com/docs/queries/about/
- Quote: "your test should resemble how users interact with your code (component, page, etc.) as much as possible."
- Confirmed: 2026-10-08 (html)

### USER-EVENT
- URL: https://testing-library.com/docs/user-event/intro/
- Quote: "Testing Library's built-in fireEvent is a lightweight wrapper around the browser's low-level dispatchEvent API, which allows developers to trigger any event on any element."
- Confirmed: 2026-10-08 (html)

### PW-BEST-PRACTICES
- URL: https://playwright.dev/docs/best-practices
- Quote: "By using web first assertions Playwright will wait until the expected condition is met."
- Confirmed: 2026-10-08 (html)

### PW-SCREENSHOTS
- URL: https://playwright.dev/docs/screenshots
- Quote: "Full page screenshot is a screenshot of a full scrollable page, as if you had a very tall screen and the page could fit it entirely."
- Confirmed: 2026-10-08 (html)

### VITEST-GUIDE
- URL: https://vitest.dev/guide/
- Quote: "is a next generation testing framework powered by Vite."
- Confirmed: 2026-10-08 (html)
