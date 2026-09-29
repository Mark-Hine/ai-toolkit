---
verified: 2026-09-29
sources: inline
---

# Authoritative sources per domain

The sources the audit fetches for each domain, and how to fetch pages that resist a plain request. The per-file `sources:` lists name the exact pages. This file names the authorities.

| Domain | Authorities | Community sources allowed as COMMUNITY or HOUSE origins |
| --- | --- | --- |
| Android | https://developer.android.com (architecture, Compose, testing, releases, behaviour changes), https://kotlinlang.org/docs, https://docs.gradle.org, the Compose API guidelines at https://github.com/androidx/androidx/blob/androidx-main/compose/docs/compose-api-guidelines.md, https://m3.material.io | Now in Android, JetSnack, Chris Banes, Manuel Vivo, ProAndroidDev posts |
| iOS | https://developer.apple.com/documentation, https://developer.apple.com/design/human-interface-guidelines, https://developer.apple.com/news/upcoming-requirements, https://docs.swift.org, https://www.swift.org, https://github.com/swiftlang/swift-evolution | Apple sample apps, Paul Hudson, Donny Wals, fatbobman |
| Design | https://developer.apple.com/design/human-interface-guidelines, https://m3.material.io, https://www.w3.org/TR/WCAG22, https://developer.android.com/develop/ui, https://developer.mozilla.org, https://web.dev | Anthropic frontend-design post, Scott Hurff, Butterick, Bringhurst |
| pr-review | https://mas.owasp.org, https://owasp.org, https://cheatsheetseries.owasp.org, https://docs.spring.io, https://react.dev, https://nextjs.org, https://www.rfc-editor.org | Redux style guide, Testing Library, Vercel and community posts |
| Agents | https://code.claude.com/docs, https://learn.chatgpt.com/docs (Codex), https://antigravity.google/docs and the docs bundled under `~/.gemini/antigravity-cli/builtin/skills/agy-customizations/docs/` | none |
| Writing | https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards, https://developers.google.com/style, https://learn.microsoft.com/en-us/style-guide, the Federal Plain Language Guidelines, https://www.nngroup.com, Anthropic prompting guidance | Wikipedia signs of AI writing, the Link and Think Claude clichés catalogue |

## Fetch tips

- **Apple.** Documentation and HIG pages render client-side. Fetch `https://developer.apple.com/tutorials/data/<path>.json` for the text. A 404 from the JSON endpoint means the page does not exist. Deprecation and availability live in the JSON too.
- **Material 3.** Pages return only a title to a plain fetch. Check `https://m3.material.io/sitemap.xml` for existence and use a web search for the page text. Mark the content Unverified when only the snippet is available.
- **GitHub.** Use raw URLs for file contents. Swift Evolution proposals carry their implementation status in the header.
- **Android.** Pages fetch normally. Behaviour changes live under `/about/versions/<n>/behavior-changes-<n>`. Releases pages list the current stable.
- **WCAG.** One URL per success criterion, `https://www.w3.org/TR/WCAG22/#<anchor>`. The Understanding documents explain intent.
- **Medium and ProAndroidDev.** Often return 403 to bots. Try a web search for the title, and mark Unverified when the text cannot be read.
- **Version numbers.** Read them from the source on the day. Never carry a version from an older register.
