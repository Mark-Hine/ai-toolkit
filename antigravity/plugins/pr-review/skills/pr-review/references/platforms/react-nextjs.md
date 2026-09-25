# React and Next.js platform pack

Grading criteria for reviewing a React or Next.js change, including pnpm/Turborepo monorepos that hold several apps and shared packages. Load this pack when a `package.json` in the delta's workspace depends on `react` or `next` and the app is not React Native. It supplies the standards vocabulary that findings cite and the recipes that turn a suspicion into evidence. The platform-neutral review rules live in [`../protocol.md`](../protocol.md) §13 to §16 (volatile facts, `Unverified` grading, pragmatism guardrails, main-safety ownership), and their extensions in §17 to §20 (root cause, verification criteria, SHA ancestry, debug-variant exclusion). All of them apply here.

Next.js behaves differently per router and per build output. Before grading anything framework-specific, record three facts in the review's scope block. These are the pinned `next` and `react` versions, the router in use (`pages/` or `app/`), and the build output (`output: "export"`, `standalone` or the default server). A rule that only holds for one of them says so below.

## Standards-basis block

Paste this into the review's Standards basis section, then append the verification sentence (template.md):

```markdown
Findings are graded against the published React, Next.js and web-platform guidance, cited per finding:
**[REACT-RULES]** Rules of React, https://react.dev/reference/rules · **[REACT-HOOKS-RULES]** https://react.dev/reference/rules/rules-of-hooks · **[REACT-NO-EFFECT]** You Might Not Need an Effect, https://react.dev/learn/you-might-not-need-an-effect · **[REACT-SYNC-EFFECTS]** https://react.dev/learn/synchronizing-with-effects · **[NEXT-STATIC]** Static exports, https://nextjs.org/docs/pages/guides/static-exports · **[NEXT-ENV]** https://nextjs.org/docs/pages/guides/environment-variables · **[NEXT-CSP]** https://nextjs.org/docs/app/guides/content-security-policy · **[REDUX-STYLE]** Redux Style Guide, https://redux.js.org/style-guide/ (Priority A/B/C) · **[TESTING-QUERIES]** https://testing-library.com/docs/queries/about/#priority · **[TS-STRICT]** https://www.typescriptlang.org/tsconfig/#strict · **WCAG 2.2 AA** · **OWASP ASVS 5.0.0** · **RFC 9700** OAuth 2.0 Security BCP.
```

## Monorepo boundaries

- **Shared code has app-wide blast radius.** A change under `packages/*` or a shared feature module reaches every app that depends on it. Grade it like a shared component (SKILL.md Phase 2, lens 3). List the consuming apps from their `package.json` `workspace:*` entries and state which ones the PR's tests actually exercise.
- **Dependency direction.** A package that imports from an app, or from a layer the repo's documented graph puts above it, inverts the graph and is a finding. Quote the import.
- **Pipeline changes ([TURBOREPO]).** Edits to `turbo.json`, root `package.json` scripts or build wrappers change what CI runs for every app. Check that `test`, `lint` and `check-types` still reach the changed workspace. A task filter that silently matches nothing is a Blocker, because a CI step that cannot fail certifies everything else (protocol.md §3).
- **Lockfile and overrides.** Read `pnpm-lock.yaml` and `pnpm.overrides` changes alongside `package.json`. A new override pins a transitive version for every workspace, so it needs a stated reason, usually a CVE backport ([PNPM-OVERRIDES]).

## React correctness

Graded against [REACT-RULES] and [REACT-HOOKS-RULES]. These are correctness rules, not style.

- **Rules of Hooks.** Hooks are called at the top level of a component or custom hook, never inside conditions, loops, early-return branches or callbacks. A conditional hook call is a Major because it corrupts hook state on the render where the condition flips.
- **Effects are an escape hatch ([REACT-NO-EFFECT]).** The following patterns are findings.
  - State derived from props or other state, computed in an effect and written back with `setState`. Compute it during render instead.
  - An effect that only responds to a user event. Move the logic into the event handler.
  - A chain of effects that set state to trigger each other.
- **Dependencies and cleanup ([REACT-SYNC-EFFECTS]).** Every value an effect reads is in its dependency array, or the omission is justified in a comment. An effect that subscribes, sets a timer or starts a request returns a cleanup.
- **Fetch races.** An effect that fetches and then sets state needs an ignore flag or an `AbortController`, so a slow earlier response cannot overwrite a later one. Name the two inputs that race in the finding.
- **Stale closures.** Callbacks registered once (listeners, intervals, `redux-persist` callbacks) that read state captured at registration time.
- **Keys ([REACT-KEYS]).** List keys are stable identifiers from the data. Array indexes as keys are a finding only when the list reorders, filters or inserts.
- **Memoisation.** `useMemo`, `useCallback` and `React.memo` need a measured reason or a referential-equality dependency downstream. Their absence is not a finding (see guardrails).

## State

Graded against [REDUX-STYLE]. Quote its priority level (A Essential, B Strongly Recommended, C Recommended) rather than inventing a severity.

- **Priority A rules** are Major when broken in the delta. They include "Do Not Mutate State" outside Immer-backed RTK reducers, "Do Not Put Non-Serializable Values in State or Actions", and "Only One Redux Store Per App".
- **Redux Toolkit.** New slices use `createSlice` and new async flows use `createAsyncThunk` or RTK Query. Hand-written action types and switch reducers in new code are a Nit in a repo that already uses RTK.
- **Persisted state.** Read the `redux-persist` config (`whitelist`, `blacklist`, storage engine). Anything persisted lands in `localStorage` or `sessionStorage` in plain text. Tokens, PII and authorisation flags there are graded under Security below. `redux-persist` itself has had no release in years, so a new dependency on it is worth a Question (maintenance status Unverified at the time of writing).
- **Server state versus UI state.** Remote data cached in Redux needs an owner for staleness and invalidation. Flag duplicated sources of truth, such as the same entity kept in a slice and in component state.

## Next.js

Confirm the version-matched doc at review time (protocol.md §13). The Pages Router and App Router docs are separate trees on nextjs.org.

- **Static export limits ([NEXT-STATIC]).** Under `output: "export"` the build is plain files, so nothing that needs a Next.js server runs. The unsupported list includes API routes, `rewrites`, `redirects` and `headers` in `next.config.js`, Middleware (renamed Proxy in Next 16), ISR, `getServerSideProps`, Server Actions and the default image loader. Config for any of these in a static-export app is dead code that looks like protection. Security headers must then come from the host, CDN or reverse proxy, and the review asks where.
- **Environment variables ([NEXT-ENV]).** `NEXT_PUBLIC_*` values are inlined into the client bundle at build time. A secret, internal hostname or signing key behind that prefix is shipped to every browser. Non-prefixed variables read in client components resolve to `undefined`.
- **Build gates.** `typescript.ignoreBuildErrors` and `eslint.ignoreDuringBuilds` skip those checks in `next build`. The Next.js docs call the TypeScript flag "very dangerous" unless type checks run elsewhere ([NEXT-TS-CONFIG], [NEXT-ESLINT-CONFIG]). Next 16 removed `next lint` and the `eslint` config key, so on 16 linting only happens if CI runs it. When either flag is set, or on Next 16, confirm CI runs `tsc`/`check-types` and `lint` for the changed workspace, and that the step can fail.
- **Pages Router.** Data fetching belongs in `getStaticProps`/`getServerSideProps` or client effects that follow the React rules above. `_app.tsx` and `_document.tsx` changes apply to every page. `router.query` is empty on the first render of a statically optimised page. Code that acts on it before `router.isReady` (a fetch, a redirect, an auth decision) is a finding.
- **App Router.** Check the `"use client"` boundary. Server-only code (secrets, database clients) must not be imported into a client component. Server Actions are public endpoints and need the same authorisation checks as an API route.
- **CSP ([NEXT-CSP]).** Nonce-based CSP needs a server and Middleware/Proxy, so it cannot work with a static export. `frame-ancestors` is ignored in a `<meta>` tag ([MDN-FRAME-ANCESTORS]), so a static export cannot set it from markup either.

## Security against ASVS 5.0.0

Cite the ASVS 5.0.0 chapter and requirement ID ([ASVS5]). Chapter numbering changed completely from 4.0.3, so never cite a 4.x ID against 5.0.

| Area | ASVS 5.0.0 | What to check in the delta |
|---|---|---|
| Token storage | V7 Session Management, V9 Self-contained Tokens, V14 Data Protection | Where access, refresh and ID tokens live. `localStorage`, `sessionStorage` and persisted Redux are readable by any script on the origin ([OWASP-HTML5]). Grade against the threat model, because an XSS then exfiltrates the refresh token. Prefer memory plus an `HttpOnly` cookie or a backend-for-frontend, per [OAUTH-BROWSER-BCP]. |
| OAuth and OIDC client | V10 OAuth and OIDC | Authorization code with PKCE (S256), with `state` generated per request, stored, compared and discarded. `nonce` is checked when an ID token is used. No implicit flow. The `redirect_uri` is an exact, registered value ([RFC9700]). When native apps use this flow, the redirect back to the app follows [RFC8252]. |
| Redirects | V2 Validation and Business Logic, V3 Web Frontend Security | Any `returnUrl`, `redirect_uri` or `next` parameter is matched against an allow-list before `window.location` or `router.push`. Open redirects in an auth flow are a Blocker. |
| XSS and output | V1 Encoding and Sanitization, V3 Web Frontend Security | `dangerouslySetInnerHTML`, `innerHTML`, `eval`, `new Function`, and `href`/`src` built from untrusted input (a `javascript:` URL). Sanitiser in use and its config ([OWASP-XSS]). |
| Clickjacking and framing | V3 Web Frontend Security | `Content-Security-Policy: frame-ancestors` with an explicit list. Browsers ignore an `X-Frame-Options` header that carries `ALLOW-FROM`, while `DENY` and `SAMEORIGIN` still work ([MDN-XFO], [OWASP-CLICKJACK]). Check the header is actually served (see static export above), not just configured. |
| Cross-window messaging | V3 Web Frontend Security | `postMessage` sends name an exact `targetOrigin`, never `"*"`. Listeners check `event.origin` against an allow-list before acting ([MDN-POSTMESSAGE]). |
| Security headers and config | V3 Web Frontend Security (headers), V13 Configuration | CSP, HSTS, `Referrer-Policy` and `Permissions-Policy` are served by whatever hosts the build. Source maps, debug flags and verbose error pages stay out of production builds. |
| Logging | V16 Security Logging and Error Handling | No tokens, codes, PKCE verifiers or PII in `console.*`, analytics events or error reporters. |
| Dependencies | V15 Secure Coding and Architecture | New packages and version bumps, with provenance. Run `pnpm audit --prod` for the changed workspace, or cite the repo's SCA step. |

## Accessibility

Graded against [WCAG22] Level AA, with [ARIA-APG] for widget patterns. A static pass cannot replace a screen reader run, so anything that needs one goes under "Unverified (needs a trace)" with the test that would confirm it.

- **Forms.** Every input has a programmatic label (`<label htmlFor>` or `aria-labelledby`). Validation errors are tied to the field with `aria-describedby` and announced (`role="alert"` or a live region). Required fields are marked beyond colour alone.
- **Focus.** After a route change or a multi-step flow advances, focus moves to the new heading or main region. Dialogs trap focus and restore it on close.
- **Semantics.** Interactive elements are `<button>` or `<a href>`, not clickable `<div>`s. Custom widgets follow the matching APG pattern, including keyboard support.
- **Contrast and target size.** WCAG 2.2 adds 2.5.8 Target Size (Minimum) at AA. Check new design-system tokens rather than individual screens.
- **Accessible authentication.** WCAG 2.2 3.3.8 Accessible Authentication (Minimum) is AA. Blocking paste or password managers on password and OTP fields fails it.

## Tests and build

- **Query priority ([TESTING-QUERIES]).** Tests prefer `getByRole`, then label and text queries, and use `getByTestId` last. A suite built on test IDs and class names tests implementation details ([TESTING-PRINCIPLES]).
- **Tests that cannot fail.** Assertions inside callbacks that never run, `waitFor` blocks with no assertion, `expect(...)` without a matcher, or mocked modules that make the assertion tautological. Grade by the risk of the path the test pretends to cover. It is a Blocker only when that path is a protocol.md §3 surface such as auth, money or privacy, and Major otherwise (generic.md "Tests").
- **Network mocks.** An axios or fetch mock should assert the request (URL, method, body, headers) as well as return a canned response. Auth flows need tests for the failure and `state`-mismatch paths, not only the happy path.
- **Snapshots.** Large component snapshots accepted with `-u` in the same PR carry no evidence. Grade the behavioural assertions instead.
- **Coverage.** Read the `jest.config` thresholds. A PR that lowers them, or adds its files to `coveragePathIgnorePatterns`, needs a stated reason.
- **Version currency.** Check the pinned Next.js and React majors against the Next.js security release program ([NEXT-SECURITY-PROGRAM]) and [REACT-VERSIONS] at review time, and record the date (protocol.md §13). Raise it as a finding only when the delta changes the pinned version or deepens reliance on an unsupported line, for example a new app on an unpatched major (protocol.md §1). Otherwise record it in the scope block as context.

> **PRAGMATISM GUARDRAILS, DO NOT FLAG.** These are legitimate choices that the official docs do not rank. Unless the repo has adopted a standard that the change contradicts, do **not** raise findings for:
> - Redux (with or without RTK) against Zustand, Jotai, React Query or Context
> - the Pages Router against the App Router, or a static export against a server build
> - Emotion, styled-components, CSS Modules or Tailwind
> - the absence of `useMemo`/`useCallback`/`React.memo` without a measured render cost
> - class components that already exist and are not touched by the delta
> - formatting and import order that the repo's Prettier and ESLint config accept
>
> Flag *a broken React rule, a Redux Priority A rule, an unserved security control or an untested auth path*.

## Recipes

```bash
# Churn first: how much of the delta is formatting? (protocol.md §7)
git diff -w --stat MERGE_BASE SOURCE_HEAD

# Which apps consume a changed shared package?
git grep -l '"<package-name>": "workspace:' SOURCE_HEAD -- '**/package.json'

# Framework facts to record in the scope block
git show SOURCE_HEAD:apps/<app>/package.json | grep -E '"(next|react|react-dom)"'
git show SOURCE_HEAD:apps/<app>/next.config.js | grep -nE 'output|ignoreBuildErrors|ignoreDuringBuilds|headers|rewrites|redirects'

# Security greps over the delta
git diff MERGE_BASE SOURCE_HEAD | grep -nE '^\+.*(dangerouslySetInnerHTML|innerHTML|postMessage|localStorage|sessionStorage|NEXT_PUBLIC_|window\.location|console\.(log|debug))'

# Run the checks that settle a claim, in a scratch worktree
pnpm install --frozen-lockfile
pnpm --filter <app> test
pnpm check-types && pnpm lint
pnpm why <package>
```

## Source registry (canonical URLs for Refs lines)

| Key | Source |
|---|---|
| [REACT-RULES] | https://react.dev/reference/rules |
| [REACT-HOOKS-RULES] | https://react.dev/reference/rules/rules-of-hooks |
| [REACT-NO-EFFECT] | https://react.dev/learn/you-might-not-need-an-effect |
| [REACT-SYNC-EFFECTS] | https://react.dev/learn/synchronizing-with-effects (fetch race cleanup under "Fetching data") |
| [REACT-KEYS] | https://react.dev/learn/rendering-lists#why-does-react-need-keys |
| [REACT-VERSIONS] | https://react.dev/versions |
| [NEXT-STATIC] | https://nextjs.org/docs/pages/guides/static-exports (App Router: /docs/app/guides/static-exports), "Unsupported Features" list |
| [NEXT-ENV] | https://nextjs.org/docs/pages/guides/environment-variables |
| [NEXT-TS-CONFIG] | https://nextjs.org/docs/pages/api-reference/config/next-config-js/typescript |
| [NEXT-ESLINT-CONFIG] | https://nextjs.org/docs/15/app/api-reference/config/next-config-js/eslint (option removed from `next.config.js` in Next 16) |
| [NEXT-CSP] | https://nextjs.org/docs/app/guides/content-security-policy |
| [NEXT-SECURITY-PROGRAM] | https://nextjs.org/blog/next-security-release-program (which release lines receive security patches) |
| [REDUX-STYLE] | https://redux.js.org/style-guide/ |
| [TESTING-PRINCIPLES] | https://testing-library.com/docs/guiding-principles/ |
| [TESTING-QUERIES] | https://testing-library.com/docs/queries/about/#priority |
| [TS-STRICT] | https://www.typescriptlang.org/tsconfig/#strict |
| [WCAG22] | https://www.w3.org/TR/WCAG22/ (W3C Recommendation, 2024-12-12) |
| [ARIA-APG] | https://www.w3.org/WAI/ARIA/apg/ |
| [ASVS5] | https://github.com/OWASP/ASVS/tree/v5.0.0/5.0 (OWASP ASVS 5.0.0, May 2025) |
| [OWASP-XSS] | https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html |
| [OWASP-HTML5] | https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html ("Do not store session identifiers in local storage") |
| [OWASP-CLICKJACK] | https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html |
| [MDN-XFO] | https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options (a header carrying `ALLOW-FROM` is ignored) |
| [MDN-FRAME-ANCESTORS] | https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/frame-ancestors (not supported in `<meta>`) |
| [MDN-POSTMESSAGE] | https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage |
| [OAUTH-BROWSER-BCP] | https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps (Internet-Draft, check the current revision at review time) |
| [RFC8252] | https://datatracker.ietf.org/doc/html/rfc8252 (OAuth 2.0 for Native Apps) |
| [RFC9700] | https://www.rfc-editor.org/rfc/rfc9700 (OAuth 2.0 Security BCP) |
| [PNPM-OVERRIDES] | https://pnpm.io/settings/dependency-resolution#overrides |
| [TURBOREPO] | https://turborepo.dev/docs |

<!-- Source links. Keep in sync with the table above (primary URL per key) so [KEY] references render as links wherever this pack's content is pasted. -->
[REACT-RULES]: https://react.dev/reference/rules
[REACT-HOOKS-RULES]: https://react.dev/reference/rules/rules-of-hooks
[REACT-NO-EFFECT]: https://react.dev/learn/you-might-not-need-an-effect
[REACT-SYNC-EFFECTS]: https://react.dev/learn/synchronizing-with-effects
[REACT-KEYS]: https://react.dev/learn/rendering-lists#why-does-react-need-keys
[REACT-VERSIONS]: https://react.dev/versions
[NEXT-STATIC]: https://nextjs.org/docs/pages/guides/static-exports
[NEXT-ENV]: https://nextjs.org/docs/pages/guides/environment-variables
[NEXT-TS-CONFIG]: https://nextjs.org/docs/pages/api-reference/config/next-config-js/typescript
[NEXT-ESLINT-CONFIG]: https://nextjs.org/docs/15/app/api-reference/config/next-config-js/eslint
[NEXT-CSP]: https://nextjs.org/docs/app/guides/content-security-policy
[NEXT-SECURITY-PROGRAM]: https://nextjs.org/blog/next-security-release-program
[REDUX-STYLE]: https://redux.js.org/style-guide/
[TESTING-PRINCIPLES]: https://testing-library.com/docs/guiding-principles/
[TESTING-QUERIES]: https://testing-library.com/docs/queries/about/#priority
[TS-STRICT]: https://www.typescriptlang.org/tsconfig/#strict
[WCAG22]: https://www.w3.org/TR/WCAG22/
[ARIA-APG]: https://www.w3.org/WAI/ARIA/apg/
[ASVS5]: https://github.com/OWASP/ASVS/tree/v5.0.0/5.0
[OWASP-XSS]: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
[OWASP-HTML5]: https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html
[OWASP-CLICKJACK]: https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
[MDN-XFO]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options
[MDN-FRAME-ANCESTORS]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/frame-ancestors
[MDN-POSTMESSAGE]: https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
[OAUTH-BROWSER-BCP]: https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps
[RFC8252]: https://datatracker.ietf.org/doc/html/rfc8252
[RFC9700]: https://www.rfc-editor.org/rfc/rfc9700
[PNPM-OVERRIDES]: https://pnpm.io/settings/dependency-resolution#overrides
[TURBOREPO]: https://turborepo.dev/docs
