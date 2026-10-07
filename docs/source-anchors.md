# Source anchors

Rules in this toolkit cite official sources by key, such as `HIG-LAYOUT` or `[MASVS]`. A source anchor
pins that key to its page and to the one or two sentences the rule rests on, so an agent can grade and
defend a rule without opening the page. Fetching happens at maintenance time instead, through
`tools/source_anchors.py`, which proves each quote is still on the live page.

## Why anchors and not fetching

- Apple HIG and Material 3 render client-side, so an agent's web fetch often returns a title or a model
  summary instead of the text.
- A fetch at invocation costs time on every run and can read the page differently each time.
- Codex, Antigravity and CI have no browser, so a browser read cannot be the default.

Volatile facts are different. A store deadline, a required target API or a latest version changes
between snapshots, so the review rules (pr-review `protocol.md` §13) still look those up when they
are used.

## Format

Each plugin that cites sources keeps `references/source-anchors.md`, mirrored to the Codex and
Antigravity layers. One heading per key:

```
### HIG-LAYOUT
- URL: https://developer.apple.com/design/human-interface-guidelines/layout
- Quote: "Respecting the safe area is essential to make sure system UI and hardware features like the Dynamic Island don't obstruct content and controls."
- Confirmed: 2026-10-07 (apple-json)
```

- **URL** is the page, with an optional fragment.
- **Quote** is verbatim text from the page, at most 300 characters and two sentences. Repeat the line
  for a second passage. Use `none (house)` for this repo's own decisions, `none (book)` for a printed
  source, and `none (offline)` for a page that blocks automated readers, such as Medium, whose bot
  protection turns away both plain requests and headless Chrome. An offline source stays cited but
  unconfirmed, so prefer an official page that says the same thing when one exists.
- **Confirmed** is written by the tool. It records the date the quote was last found and how the page
  was read (`apple-json`, `html` or `browser`). A new anchor starts as `not yet`.
- **Fetch** is optional and overrides how the page is read.

Quotes are short attributed citations of the sentence a rule relies on. Copyright stays with each
source's owner, and no page text is committed.

## Maintenance

```
python3 tools/source_anchors.py --lint            # offline: format, quote length, coverage
python3 tools/source_anchors.py                   # network: CONFIRMED, DRIFTED or UNREACHABLE
python3 tools/source_anchors.py --write           # also record today on confirmed anchors
python3 tools/source_anchors.py --only HIG-       # one family of keys
```

- **DRIFTED** means the page changed. Read the cached text in `.cache/sources/`, choose the new
  sentence, and update the rule if its meaning moved.
- **UNREACHABLE** means the tool could not read the page, for example because Chrome is missing for a
  client-rendered host. Open the page in a browser, with the user's OK when an agent does it, and
  confirm the quote by hand.
- A monthly scheduled run opens a "Source anchors need attention" issue when any anchor is drifted or
  unreachable, and closes it when all are confirmed.
