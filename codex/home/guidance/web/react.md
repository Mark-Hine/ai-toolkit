---
verified: 2026-10-07
sources:
  - https://react.dev/reference/rules/rules-of-hooks
  - https://react.dev/reference/rules/components-and-hooks-must-be-pure
  - https://react.dev/learn/you-might-not-need-an-effect
  - https://react.dev/learn/rendering-lists
  - https://nextjs.org/docs/app/getting-started/server-and-client-components
  - https://nextjs.org/docs/app/guides/environment-variables
  - https://nextjs.org/docs/app/api-reference/file-conventions/loading
  - https://nextjs.org/docs/app/api-reference/file-conventions/error
  - https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA
paths:
  - "**/*.tsx"
  - "**/*.jsx"
---

# React and Next.js (web repos)

- Components and hooks are pure. Rendering computes markup from props and state only. Side effects belong in event
  handlers, or in an Effect only when they synchronise with something outside React.
- Call hooks at the top level of a component or custom hook, never inside a condition, a loop or after an early return.
- Derive values during render instead of copying props into state or syncing state in an Effect. Add `useMemo` only
  when a measured render is slow.
- List keys come from the data, such as an id. Do not use the array index when the list can reorder, and never
  generate a key during render.
- In the Next.js App Router, pages and layouts are Server Components by default. Put `'use client'` on the smallest
  interactive component, not on a page or layout.
- Secrets stay on the server. A `NEXT_PUBLIC_` variable is inlined into the JavaScript sent to the browser, so it
  never holds a key or token.
- Every data-driven route designs loading, loaded, empty and error. In the App Router, give the segment a `loading`
  and an `error` file, and give the error UI a way to retry.
- Use native elements before ARIA: `button` for actions, `a` for navigation and `label` for form fields. Add ARIA only
  where no native element fits.
- Fetch and mutate data with the library the project's `AGENTS.md` names. Do not add a second one.
- Follow `guidance/design-standards.md` for layout, tokens, accessibility and screen states. Delegate UI diff
  reviews to `ui-reviewer`.
