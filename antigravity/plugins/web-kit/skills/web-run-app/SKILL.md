---
name: web-run-app
description: "Start a web app's dev server, wait for it to answer, and screenshot routes with Playwright at phone and desktop widths."
---

Read the project AGENTS.md (or GEMINI.md) and applicable guidance first. Fall back to CLAUDE.md if AGENTS.md is absent. Follow global rules for optional tools, specialist subagents and Git actions.

# Run the app: the user request

Defaults: the dev script, port and package manager from the project's `AGENTS.md` (or `GEMINI.md`). When it names no package manager,
take it from the lockfile: `pnpm-lock.yaml` means pnpm, `yarn.lock` yarn, `bun.lock` or `bun.lockb` bun, otherwise npm.

1. If `node_modules` is missing, ask before running the install command, because it downloads packages and may run install scripts.
2. Check whether the app already answers: `curl -s -o /dev/null -w '%{http_code}' http://localhost:<port>/`. If it does
   not, start the dev script in the background and repeat the check every few seconds for up to a minute. If it never
   answers with a 2xx or 3xx code, quote the last lines of the dev server output and stop.
3. Capture each route the caller named, or `/` when none, at phone and desktop widths:
   `npx playwright screenshot --channel chrome --viewport-size "390, 844" --full-page <url> <scratchpad>/<route>-phone.png`,
   and the same with `"1440, 900"` saved as `<route>-desktop.png`. Add `--color-scheme dark` for dark captures. Use the
   project's own Playwright when it has one. `--channel chrome` drives the installed Chrome, so no browser download is
   needed. Ask before letting Playwright download browsers. For the full matrix, follow `references/capture.md` in the `design-standards` skill.
4. Report: the URL, package manager and script, screenshot paths, and any error from the dev server output or a failed
   capture. Leave the dev server running and say so, with the background task that owns it.

Commands outside `allowed-tools`, such as installs or a production build, use the approval policy and prompt. A request to run the app authorizes starting its dev server and taking screenshots.
