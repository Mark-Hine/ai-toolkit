---
verified: 2026-10-06
sources:
  - https://www.paulrand.design/writing/articles/1991-logos-flags-and-escutcheons.html
  - https://logogeek.uk/logo-design/optical-corrections/
  - https://developer.android.com/develop/ui/views/launch/icon_design_adaptive
  - https://developer.apple.com/design/human-interface-guidelines/app-icons
  - https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/How_to/Define_app_icons
  - https://evilmartians.com/chronicles/how-to-favicon-in-2021-six-files-that-fit-most-needs
  - https://branddb.wipo.int/
---

# Brand marks

How to audit, refine or redesign a logo or app icon, and ship it to every platform (AND-7, IOS-5, WEB-5, WEB-6).

## Refine or redesign

Render the current mark on the test sheet in `capture.md` first, and diagnose it against the criteria below with the image paths as evidence. Then agree the route with the user before drawing anything.

- **Refine** when people recognise the mark and its idea works. Fix the construction, the optical balance, the small-size version and the asset set, and keep the recognition the mark has earned.
- **Redesign** when the idea fails the criteria or the user asks for a new identity. Produce three to five concepts.

The agent takes geometric and typographic marks to a final master. Pictorial and illustrated marks, mascots and detailed emblems stop at rendered concepts plus the designer brief below, because model-drawn pictorial SVGs are rarely good enough to ship.

## Criteria

Paul Rand asked that a logo be "reproducible in one color and in exceedingly small sizes", and listed distinctiveness, visibility, useability, memorability, universality, durability and timelessness. He also wrote that a logo "derives its meaning from the quality of the thing it symbolizes, not the other way around", so a mark need not explain the product.

| Criterion | Test on the sheet |
| --- | --- |
| Distinctive | It would not be mistaken for a competitor's mark, a stock icon or a letter in a rounded square |
| Small | It reads at 16 px in a browser tab and at its header size |
| One colour | It holds its shape in solid black, in solid white on dark and reversed. A mark that becomes a solid block depends on its container |
| Backgrounds | It stays visible on light, dark, brand colour and photograph |
| Simple | A 2 px blur leaves a silhouette people would still recognise |
| Lasting | It does not need a current trend to make sense |
| Platform safe | It sits inside the Android 66 dp safe zone, the iOS canvas and the maskable circle (AND-7, IOS-5, WEB-5) |

## Concepts

Draw each concept from a different idea:

- A letterform or monogram drawn for the brand, not typed in a default face.
- A geometric symbol built on a simple grid.
- A shape taken from the product's subject, its materials or its vernacular.
- A wordmark with one drawn detail.
- A combination of symbol and wordmark, with a symbol that works alone.

Anchor each concept to a different exemplar, as `options.md` describes, and give each one sentence that ties it to the brief.

## Construction

- Keep one SVG master per mark with a `viewBox`, no embedded raster images and as few paths as the shape needs.
- Convert letters to paths. A `<text>` element depends on the viewer's fonts. When a wordmark uses a typeface, record the face and its licence in `DESIGN.md`.
- Build on a grid, then correct by eye. Round and pointed shapes need a little overshoot to look the same height as flat ones. A mark reversed out of a dark ground looks heavier, so its white version needs slightly thinner strokes.
- Draw a simpler small-size version when counters or details close up at 16 px.
- Design each concept with its colour versions from the start: a positive version for light grounds and a reversed version for dark and brand-colour grounds. A mark drawn only in the brand colour disappears on the brand's own header.
- Take fills from the brand colours in `DESIGN.md`. An `icon.svg` for the web can switch fills with a `prefers-color-scheme` media query:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <style>
    path { fill: #1f4e5f; }
    @media (prefers-color-scheme: dark) { path { fill: #8cc7d9; } }
  </style>
  <path d="M8 8h48v48H8z"/>
</svg>
```

## Platform assets

Generate every file from the master after the user picks.

| Platform | Files | Rule |
| --- | --- | --- |
| Web | `favicon.ico` at 32 px, `icon.svg` with dark mode, `apple-touch-icon.png` at 180 px. With a web app manifest, also `icon-192.png`, `icon-512.png` and a maskable `icon-mask.png` at 512 px with the mark inside the central 409 px | WEB-5, WEB-6 |
| Android | An adaptive `ic_launcher` with foreground, background and monochrome layers at 108 dp, the mark between 48 and 66 dp | AND-7 |
| iOS | 1024 px foreground and background layers for Icon Composer, checked in the default, dark, clear and tinted appearances | IOS-5 |

Render PNGs by capturing an HTML page that shows the master at the target size, as in `capture.md`, or with the platform tools: Image Asset Studio in Android Studio and Icon Composer in Xcode. Writing an `.ico` needs a converter. When none is available, report the file as Unverified instead of guessing its format.

## Recording the mark

Add the mark to the Brand marks section of `DESIGN.md` in the same change:

- the master file path, and the small-size version if there is one
- clear space, as a part of the mark such as the height of its main counter
- the minimum size
- the approved colour versions
- misuses, such as stretching, recolouring, adding effects or placing it on a busy photograph

## Designer brief

For pictorial marks and new identities, hand a designer this brief with the concept renders:

- product, audience and the three traits from the brief
- the concept chosen and why, with the renders and the test sheet
- what to keep from the current mark
- where the mark appears and at which sizes
- competitors' marks to stay clear of
- the deliverables: the master SVG, the platform assets above and the usage rules

## Trademark check

An agent cannot clear a trademark. Before a new mark ships, the user searches the WIPO Global Brand Database, which accepts an image query, and the trademark register of each market, and takes legal advice where the mark matters.
