---
verified: 2026-10-06
sources:
  - https://playwright.dev/docs/screenshots
  - https://playwright.dev/docs/emulation
  - https://developer.chrome.com/docs/chromium/headless
---

# Capture

How to render screens, options and brand marks as labelled images that `ui-reviewer`, a second opinion and the user can compare. Native platforms use the platform `run-app` skill and its verifier agent, which already label captures by device and setting. This file covers the web, the brand mark test sheet and the comparison board.

## Where files go

Each piece of design work gets one folder, `.design/iterations/<date>-<slug>/`, holding its captures, option prototypes, test sheets, board and notes. Offer to add `.design/` to `.gitignore`, and keep it out of lint and the build. Keep work in progress, such as draft SVGs, preview renders and helper scripts, in a `drafts/` subfolder, so the top level holds only the captures, the option files, the test sheets, the board and the notes. The decision itself lands in `DESIGN.md`, so the folder can be thrown away.

Name images `<state>-<page>-<label>-<scheme>.png`, where the state is `before`, `after` or an option letter. For example `before-home-phone-dark.png` or `B-pricing-desktop-light.png`.

## Web matrix

Capture every affected page at these sizes, in light and dark:

| Label | Viewport in CSS px | Checks |
| --- | --- | --- |
| `phone` | 390 by 844 | Compact layout, wrapping, targets |
| `tablet` | 834 by 1194 | The middle breakpoint |
| `desktop` | 1440 by 900 | Line length and wide layout (TYP-3) |
| `zoom200` | 720 by 450 at device scale factor 2 | 200% browser zoom on the desktop page (A11Y-7, WEB-2) |

The capture script turns on reduced motion so entrance animations are not caught halfway. Check reduced motion separately when the work changes motion (A11Y-9).

## Serving the page

Use the project's own dev server and record its URL in the report. A static folder can be served with `python3 -m http.server 4321` run in the background, and stopped when the captures are done. Open single files, such as a test sheet or a board, through a `file://` URL instead of a server.

## With Playwright

Prefer the project's own Playwright. `npx playwright` works without it, and `--channel chrome` drives an installed Chrome so no browser download is needed. Ask before letting Playwright download browsers.

One capture:

```bash
npx playwright screenshot --channel chrome --viewport-size "390, 844" --color-scheme dark --full-page \
  http://localhost:4321/ before-home-phone-dark.png
```

The full matrix comes from `capture.mjs` in the iterate skill's `scripts/` folder. Copy it beside the board, install `playwright` there and run `CAPTURE_CHANNEL=chrome node capture.mjs <url> <state> <page>`.

## Without Playwright

Headless Chrome takes a single screenshot. Find the Chrome path in `machine.md`:

```bash
"<chrome>" --headless=new --hide-scrollbars --window-size=390,844 \
  --screenshot=before-home-phone-light.png http://localhost:4321/
```

Its command line cannot switch the colour scheme reliably, so capture light only and report the dark captures as Unverified. With no browser at all, write the test sheet and the board as HTML, report every capture as Unverified, and ask the user to open the files.

## Brand mark test sheet

`board.py` in the iterate skill's `scripts/` folder writes each mark's test sheet when asked with `--sheets`, and a compact strip for every mark. The sheet shows the mark from 16 to 180 px, on light, dark, brand, footer and photo grounds, in one colour, blurred, under the platform masks and in a browser tab. The strip shows 16, 32 and 64 px, reversed, one colour and blurred, which is enough to screen an option.

Read each result against the criteria in `brand-marks.md`. A mark that vanishes on the brand background, turns into a solid shape in one colour, or crosses the dashed safe circle fails before taste is even discussed.

## Board

The board puts options side by side so the user compares them at the same size and scheme. Write it as `board.html` in the iteration folder and open it through a `file://` URL.

- For options, show one column per option in random order, labelled A, B and C, with no ranking or scores.
- For a change to a shared token, component or brand asset, show before and after for every affected screen.
- Keep notes, screening results and any second opinion inside a closed section that the user opens after the pick.
- When the session cannot render images, still write `board.html`. For a token or component change, put the before and after versions of the real components side by side in the page, using the project's stylesheet, so the user's browser renders them. Report the captures as Unverified.

`board.py` writes this board for brand marks, with the tab, header, phone header and footer rows at real size. For screen options, write the same layout by hand: one column per option, one row per capture, usually phone and desktop in light and dark.
