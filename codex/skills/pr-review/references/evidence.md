---
verified: 2026-11-23
sources: house
---

# Evidence: showing a visible defect

An optional step between personal verification and `findings.json` (SKILL.md Phase 3a). It gives a
Blocker, Question or Major whose defect shows on screen a screenshot or similar proof that the
author can check in seconds. Reviews land faster when the author sees the defect. A screenshot has
settled a disputed "done" ticket in one exchange where `file:line` references had not.

Evidence shows a defect that Phase 3 already proved. It never replaces that proof, and a finding
without evidence is still a finding. The rules here are protocol.md §25. The platform pack loaded in
Phase 2 holds the commands for each method.

## When to collect evidence

- **Only B, Q and M findings whose defect is visible**: a wrong or blank field, a wrong enabled
  state, misleading copy, the wrong screen, or a wrong timing or navigation step. Nits never get
  evidence.
- **Each B, Q and M draft says whether a screenshot helps.** When the defect has nothing visible,
  such as a leaked token in a log or a race in a repository, the draft says so in one line and
  moves on: "No screenshot: the defect is in the request body, not on screen." Keep that line in
  the run's notes, not in the finding.
- **Local mode only for device work.** CI mode runs no emulator, simulator or browser (see
  "CI mode" below).
- **Ask before the first device run** in local mode. Name the findings, the rung you plan for
  each and the device you will use. Booting an emulator and installing an APK change the user's
  machine.

## The ladder

Try the cheapest rung that can show the defect, and stop at the first rung that shows it.

| Rung | `kind` | What it is | Typical cost |
|---|---|---|---|
| 1 | `unit_test` | A failing unit test on the pinned SHA that asserts the wrong state, such as "Continue is enabled for this address". The excerpt is the assertion failure | minutes |
| 2 | `render` | The real screen built from the real view model or state on the JVM or host, drawn to an image | 10 to 20 minutes |
| 3 | `device_harness` | The real screen and the real view model on an emulator or simulator, with only the data layer stubbed, driven by UI test APIs | 20 to 40 minutes |
| 4 | `device_live` | The real app on an emulator or simulator, driven through a real journey | often impractical, see below |
| 5 | `recording` | A short screen recording, only for timing or navigation defects that a still image cannot show | as rung 3 or 4, plus the recording |

Backend and library repos use `unit_test` or `transcript` and never take screenshots. A
`transcript` is a request and response pair, redacted, that shows the wrong status, field or
header.

Rung 4 is rarely worth trying. A live journey usually needs a test account, a one-time code sent
by SMS or email, and backend data that triggers the defect. Use it only when the user already has
those ready, and say in the caption which environment it ran against.

### Show the defect beside its control

A defect and control pair in one image works best. Put the defect state beside the nearest state
that behaves correctly, such as an address from the lookup with Continue enabled beside the same
street typed in by hand with Continue disabled. The reader then sees the difference without
reading the code. Build the pair inside the harness where the platform allows it, because the host
may have no image tools. The platform pack names the API. When composing is not practical, attach 2
images with a caption each.

## Budget and the stop rule

Spend at most about 25 tool calls or 30 minutes per finding, whichever comes first, across every
rung tried. When the budget runs out:

1. Stop. Ship the finding without evidence. Phase 3 already verified it.
2. If part of the finding's claim rests on how the screen renders and code reading cannot settle
   that part, such as "the field renders blank" rather than "the flag is never set", grade that
   part **Unverified** with the exact run that would confirm it (protocol.md §14). Name the rung,
   the harness and the device, so the next reviewer can pick it up.
3. Record what you tried in the run's notes.

## Honesty rules

- **Every image states its method in its caption**, such as "Real screen and view model on an API
  36 emulator, repository mocked." The `method` field carries it, and the renderer and the poster
  print it under the image.
- **Never present a harness or a render as a live reproduction.** Use the words "live" or
  "reproduced in the app" only for rung 4. A harness proves what the real screen does with the
  state the harness gave it, and the caption says which part was stubbed.
- **Pin the SHA.** Build every piece of evidence from `scope.source_head`, or from the new head in
  a re-review, and record it in `sha`.
- **Crop harness-only chrome**, such as a test runner overlay, debug banner or blank system bar the
  real app would not show. Never crop or edit anything the app draws.
- **Test data only.** No customer data, real names, addresses, phone numbers, card or account
  numbers, tokens or session IDs in any image, excerpt or transcript. Invent data that triggers the
  defect. Redact headers such as `Authorization` and `Cookie` in a transcript.
- **Respect `FLAG_SECURE`** and its iOS equivalents. Never remove a secure-window flag from the app
  to capture a screen. A harness may host the screen's composable or view without the activity or
  window that sets the flag, and then the caption says "secure window flag not applied in the
  harness".

## Hygiene

- **Harness code lives only in a scratch worktree** of the pinned SHA, separate from the Phase 2a
  checkout: `git worktree add --detach <scratchpad>/pr-<id>-evidence SOURCE_HEAD`. Never commit,
  push or stash harness code in the reviewed repo, and never edit the user's working tree.
- **Clean up when the evidence is captured**, and before Phase 6:
  - uninstall every test APK or app build you installed, such as
    `adb uninstall <test package>` and `adb uninstall <app package>`;
  - stop any recording, and shut down a simulator or emulator that this session booted;
  - `git worktree remove --force <scratchpad>/pr-<id>-evidence`.
- **Keep the harness out of the review.** The document and the JSON never contain harness code. If
  the user wants it kept, copy it beside the evidence as `pr-review-evidence/harness/`.

## Storage and naming

- Store each file at `pr-review-evidence/<pr>-<id>-<slug>.<ext>` beside the review files, with the
  finding ID in lower case, such as `pr-review-evidence/78455-m1-lookup-vs-manual.png`. In
  promotion mode use `<source>-to-<target>` in place of `<pr>`.
- Local mode: the folder sits at the repo root beside the review files and stays untracked, like
  them (protocol.md §12). CI mode: the artifact staging directory.
- Images are PNG, JPEG, GIF or WebP, at most 5 MB each. A recording is an MP4 of at most 30 seconds,
  or a GIF when the host should play it inline. The poster refuses larger files.
- Record each file in the finding's `evidence` array (output.md). `path` is relative to the
  directory that holds `findings.json`, so it never carries an absolute local path.

## Where evidence appears

- **Document**: the image and its caption render under the finding's Evidence paragraph
  (template.md).
- **Azure DevOps**: the poster uploads each file as a PR attachment and embeds it in the finding's
  thread (posting.md).
- **GitHub**: no API attaches a file to a PR comment, so the poster names the file and points at
  the review document, or embeds the item's `url` when one is set (posting.md).
- **Confluence**: `render_confluence.py publish` uploads each referenced file as a page attachment
  (posting.md).

## CI mode

CI mode (protocol.md §24) runs no emulator, simulator, browser or live journey. It may record
`unit_test` or `transcript` evidence when the pipeline already builds and runs tests for the
review. Every skipped evidence step goes into `scope.inferences`, such as
`evidence skipped for M2: device_harness needs an emulator (CI mode)`.
