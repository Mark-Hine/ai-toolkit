# Per-repo `AGENTS.md` (or `GEMINI.md`) template for web repos

Copy to `<repo>/AGENTS.md`, replace every `<…>`, delete lines that do not apply. Keep it under about 60 lines with the
hard rules in the first 40, repo facts only and no tutorials (the shared `web-kit` skills and the web-kit rules
carry conventions). Personal or temporary notes go in `GEMINI.md` (gitignored).

```markdown
# <repo-name>

<one-line product description>, `<git host>` repo `<org>/<repo>`, deployed to `<host>`.

## Never (hooks enforce the push, lock-file and secret-file rules)
- Commit `.env*` files other than `.env.example`, or put a secret in a `NEXT_PUBLIC_` variable.
- Add a dependency without approval, or edit `<package-lock.json | pnpm-lock.yaml | yarn.lock>` by hand.
- Change `tsconfig.json` strictness, the lint config or the framework major version outside an explicit uplift ticket.
- <repo-specific never, e.g. "Add a second data-fetching library. Use <TanStack Query | SWR | server actions>.">
- Fix the "known broken" items below inside another ticket. Report them as pre-existing.

## Commands
- Package manager: `<npm | pnpm | yarn | bun>`, Node `<version from .nvmrc or engines>`.
- Dev: `<pnpm dev>` on `http://localhost:<3000>`. Build: `<pnpm build>`.
- Type check: `<pnpm typecheck | npx tsc --noEmit>`. Lint: `<pnpm lint>`.
- Unit and component tests: `<pnpm test -- <file>>` with `<Vitest | Jest>` and Testing Library.
- End-to-end: `<pnpm test:e2e | npx playwright test <file>>`, or "none yet".
- Monorepo: `<turbo | nx | pnpm workspaces>`, app at `<apps/web>`. Run scripts with `<pnpm --filter web …>`.

## Architecture map
- Framework: `<Next.js <version> App Router | Pages Router | Vite + React Router>`. Entry `<app/layout.tsx | src/main.tsx>`.
- Design system: `<package or folder>`, tokens in `<file>`, components `<Button>`, `<Card>`…. `DESIGN.md` at `<path>`.
- Data: `<server components with fetch | server actions | TanStack Query | SWR>`. API client `<file>`. Validation `<zod | valibot | none>`.
- State: `<React state and context | Zustand | Redux Toolkit>`. URL state `<nuqs | searchParams>`.
- Reference route for state, loading and error: `<path>`. Anti-example: `<path>` (<why>).

## Known broken on <default branch>
- <failing test, lint debt or flaky e2e, with ticket>
```
