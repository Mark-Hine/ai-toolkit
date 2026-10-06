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

Each piece of design work gets one folder, `.design/iterations/<date>-<slug>/`, holding its captures, option prototypes, test sheets, board and notes. Offer to add `.design/` to `.gitignore`, and keep it out of lint and the build. The decision itself lands in `DESIGN.md`, so the folder can be thrown away.

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

The full matrix, from a script written beside the board and run as `node capture.mjs <url> <state> <page>` with `playwright` installed in that folder:

```js
// capture.mjs renders one page across the capture matrix.
import { chromium } from "playwright";

const [url, state, page] = process.argv.slice(2);
const sizes = {
  phone: { width: 390, height: 844, scale: 1 },
  tablet: { width: 834, height: 1194, scale: 1 },
  desktop: { width: 1440, height: 900, scale: 1 },
  zoom200: { width: 720, height: 450, scale: 2 },
};
// CAPTURE_CHANNEL=chrome uses the installed Chrome instead of a downloaded browser.
const browser = await chromium.launch({ channel: process.env.CAPTURE_CHANNEL || undefined });
for (const [label, size] of Object.entries(sizes)) {
  for (const scheme of ["light", "dark"]) {
    const context = await browser.newContext({
      viewport: { width: size.width, height: size.height },
      deviceScaleFactor: size.scale,
      colorScheme: scheme,
      reducedMotion: "reduce",
    });
    const tab = await context.newPage();
    await tab.goto(url, { waitUntil: "load" });
    const file = `${state}-${page}-${label}-${scheme}.png`;
    await tab.screenshot({ path: file, fullPage: true });
    console.log(file);
    await context.close();
  }
}
await browser.close();
```

## Without Playwright

Headless Chrome takes a single screenshot. Find the Chrome path in `machine.md`:

```bash
"<chrome>" --headless=new --hide-scrollbars --window-size=390,844 \
  --screenshot=before-home-phone-light.png http://localhost:4321/
```

Its command line cannot switch the colour scheme reliably, so capture light only and report the dark captures as Unverified. With no browser at all, write the test sheet and the board as HTML, report every capture as Unverified, and ask the user to open the files.

## Brand mark test sheet

Write one sheet per mark beside its SVG, replace `MARK_NAME`, `mark.svg` and `--brand`, and capture it at 1100 by 760 in light. The sheet shows the mark small, on every background, in one colour, blurred, under the platform masks and in a browser tab.

```html
<!doctype html>
<meta charset="utf-8">
<title>Mark test sheet</title>
<style>
  :root { --brand: #1f4e5f; }
  body { margin: 24px; font: 13px system-ui, sans-serif; color: #222; background: #fff; }
  h1 { font-size: 18px; margin: 0 0 16px; }
  h2 { font-size: 13px; margin: 20px 0 8px; color: #555; }
  .row { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
  .tile { display: grid; place-items: center; width: 112px; height: 112px; border: 1px solid #ddd; }
  .tile img { width: 64px; height: 64px; }
  .dark { background: #111; }
  .brand { background: var(--brand); }
  .photo { background: linear-gradient(135deg, #b08968, #3e5c4a 60%, #1d2b2f); }
  .black img { filter: brightness(0); }
  .white img { filter: brightness(0) invert(1); }
  .blur img { filter: blur(2px); }
  .mask { display: grid; place-items: center; width: 108px; height: 108px; background: #e9e9e9; overflow: hidden; position: relative; }
  .mask img { width: 66px; height: 66px; }
  .circle { border-radius: 50%; }
  .squircle { border-radius: 24px; }
  .safe::after { content: ""; position: absolute; inset: 21px; border: 1px dashed #d33; border-radius: 50%; }
  .tab { display: flex; align-items: center; gap: 8px; width: 240px; padding: 8px 12px; border-radius: 8px 8px 0 0; background: #dee1e6; }
  .tab img { width: 16px; height: 16px; }
</style>
<h1>MARK_NAME</h1>
<h2>Sizes 16, 24, 32, 48, 64, 128 and 180 px</h2>
<div class="row">
  <img src="mark.svg" width="16"><img src="mark.svg" width="24"><img src="mark.svg" width="32">
  <img src="mark.svg" width="48"><img src="mark.svg" width="64"><img src="mark.svg" width="128"><img src="mark.svg" width="180">
</div>
<h2>Light, dark, brand and photo backgrounds, one colour black, one colour white, blurred</h2>
<div class="row">
  <div class="tile"><img src="mark.svg"></div>
  <div class="tile dark"><img src="mark.svg"></div>
  <div class="tile brand"><img src="mark.svg"></div>
  <div class="tile photo"><img src="mark.svg"></div>
  <div class="tile black"><img src="mark.svg"></div>
  <div class="tile dark white"><img src="mark.svg"></div>
  <div class="tile blur"><img src="mark.svg"></div>
</div>
<h2>Android circle and squircle with the 66 dp safe zone, iOS rounded square, maskable circle</h2>
<div class="row">
  <div class="mask circle safe"><img src="mark.svg"></div>
  <div class="mask squircle safe"><img src="mark.svg"></div>
  <div class="mask squircle"><img src="mark.svg" style="width: 108px; height: 108px"></div>
  <div class="mask circle"><img src="mark.svg" style="width: 86px; height: 86px"></div>
</div>
<h2>In a browser tab</h2>
<div class="row"><div class="tab"><img src="mark.svg"> MARK_NAME</div></div>
```

Read the sheet against the criteria in `brand-marks.md`. A mark that vanishes on the brand background, turns into a solid shape in one colour, or crosses the dashed safe circle fails before taste is even discussed.

## Board

The board puts options side by side so the user compares them at the same size and scheme. Write it as `board.html` in the iteration folder and open it through a `file://` URL.

- For options, show one column per option in random order, labelled A, B and C, with no ranking or scores.
- For a change to a shared token, component or brand asset, show before and after for every affected screen.
- Keep notes, screening results and any second opinion inside a closed section that the user opens after the pick.
- When the session cannot render images, still write `board.html`. For a token or component change, put the before and after versions of the real components side by side in the page, using the project's stylesheet, so the user's browser renders them. Report the captures as Unverified.

```html
<!doctype html>
<meta charset="utf-8">
<title>BOARD_TITLE</title>
<style>
  body { margin: 24px; font: 15px system-ui, sans-serif; color: #222; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }
  figure { margin: 0; }
  img { width: 100%; border: 1px solid #ddd; }
  figcaption { margin-top: 8px; font-weight: 600; }
  details { margin-top: 32px; }
</style>
<h1>BOARD_TITLE</h1>
<p>BRIEF_IN_ONE_SENTENCE</p>
<h2>Desktop, light</h2>
<div class="grid">
  <figure><img src="A-home-desktop-light.png" alt="Option A, desktop, light"><figcaption>A</figcaption></figure>
  <figure><img src="B-home-desktop-light.png" alt="Option B, desktop, light"><figcaption>B</figcaption></figure>
  <figure><img src="C-home-desktop-light.png" alt="Option C, desktop, light"><figcaption>C</figcaption></figure>
</div>
<details><summary>Notes, opened after the pick</summary><p>NOTES</p></details>
```

Repeat the heading and grid for each label and scheme the brief cares about, usually phone and desktop in light and dark.
