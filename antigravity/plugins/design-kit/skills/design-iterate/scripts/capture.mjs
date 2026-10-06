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
