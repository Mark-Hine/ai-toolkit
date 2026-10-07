---
verified: 2026-10-07
sources:
  - https://www.typescriptlang.org/tsconfig/strict.html
  - https://www.typescriptlang.org/docs/handbook/2/narrowing.html
  - https://www.typescriptlang.org/docs/handbook/2/functions.html
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.mts"
---

# TypeScript (web repos)

- Keep `strict` on in `tsconfig.json`. A change never loosens a compiler option to make an error go away.
- No `any` in new code. Type data from outside the program as `unknown` and narrow it where it enters, such as a
  fetch response, `localStorage`, URL parameters or `postMessage`. Use the project's schema validator when its
  `AGENTS.md` names one.
- Model each screen or request state as a discriminated union on one field, such as `status`, with `loading`, `loaded`,
  `error`, and `empty` where the screen can be empty. End each `switch` over it with a `never` check, so a new case
  fails to compile until every consumer handles it.
- Do not silence the compiler with a non-null assertion (`!`) or an `as` cast. Narrow the value, or say in a comment
  why it cannot be null.
- Give exported functions and component props explicit types. Inferred types are fine inside a module.
- Run the project's type check (`tsc --noEmit` or its `typecheck` script) before calling a change done, and quote the result.
