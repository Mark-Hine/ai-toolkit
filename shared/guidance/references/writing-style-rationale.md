---
verified: 2026-09-29
sources: inline
---

# Writing style rationale

This file explains the rules in `claude/home/rules/writing-style.md`. The rule file carries the rules and a source key per rule. This file carries the sources, the reason each rule exists, and where the authorities disagree. It lives outside `rules/` on purpose, because Claude Code loads every markdown file under `rules/` into each session.

## Purpose and scope

The rule file exists because model replies were hard to follow on first read. Most rules correct a specific habit of model prose rather than restate general style advice. The Codex and Antigravity layers carry a condensed `writing-style.md` by design. They keep the wrapping scope and the code-comment rule and leave out the punctuation and word bans, because those layers have no reminder hook and the user tolerates more variance there.

## Source keys

| Key | Source | URL |
| --- | --- | --- |
| Anthropic | Claude prompting best practices, and the Claude Opus 5 prompting guide | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices and https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 |
| Claude Code | Output styles reference, the Concise style | https://code.claude.com/docs/en/output-styles |
| GOV.UK | Style guide A to Z, and the clear-language and clear-structure guidelines | https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/ and https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/ |
| Google | Google developer documentation style guide, pages on dashes, semicolons, colons, lists, parentheses, pronouns, text formatting, voice and tone | https://developers.google.com/style |
| Microsoft | Microsoft Writing Style Guide, top ten tips, punctuation and scannable-content pages | https://learn.microsoft.com/en-us/style-guide/welcome/ |
| PLG | Federal Plain Language Guidelines, 2011 edition | https://www.plainlanguage.gov/guidelines/ |
| NN/g | Nielsen Norman Group, how users read on the web, and the inverted pyramid | https://www.nngroup.com/articles/how-users-read-on-the-web/ and https://www.nngroup.com/articles/inverted-pyramid/ |
| Williams | Joseph Williams, Style: Lessons in Clarity and Grace, characters as subjects and actions as verbs | https://nysba.org/thoughts-on-legal-writing-from-the-greatest-of-them-all-joseph-m-williams-part-i/ |
| Strunk | Strunk, The Elements of Style, rule 13 on omitting needless words and rule 14 on varied sentences | https://www.gutenberg.org/cache/epub/37134/pg37134.txt |
| Claude tic | A habit of model prose with no style-guide backing either way. Evidence is the Wikipedia essay on signs of AI writing and the Link and Think catalogue of Claude clichés | https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing and https://www.linkandth.ink/p/catalog-of-claude-cliches |
| Personal | The user's own preference, kept without an external source | none |
| Tooling | A fact about a tool the user pastes into, not a readability finding | none |

## Rule notes

**Actor as subject, action as verb.** Williams puts characters in subjects and actions in verbs. The plain-language guidelines say hidden verbs make writing weak and longer. GOV.UK requires active voice. Google allows the passive when the actor does not matter, which the rule keeps. Before, "validation of the token was performed". After, "we validated the token".

**Short common words.** GOV.UK and Microsoft both prefer the plain word. The rule gives three swaps so the reader knows the scale of change intended.

**Sentence ceiling of 25 words.** GOV.UK says to split sentences over 25 words. The plain-language guidelines say one idea per sentence and give no number. Claude Code's memory guidance asks for rules concrete enough to check, so the rule states the number. Strunk's rule 14 and Williams both warn that uniformly short sentences read as choppy, which is why the rule also asks for varied length.

**Pronoun antecedents.** Google says to avoid vague pronoun references and to follow "this" with a noun. The guidelines say to repeat the noun when a pronoun could point at two things.

**Concise, not compressed.** Strunk asks that every word tell, not that every sentence be short. Microsoft warns against sounding abrupt. The aphoristic ender is a catalogued Claude cliché, so the rule names it.

**Dashes.** Google and Microsoft accept em dashes and Microsoft warns that too many hurt readability. Google avoids en dashes and GOV.UK writes ranges with "to". The dashes themselves are correct English. The ban exists because model prose overuses them and the Wikipedia essay lists dash overuse as a sign of machine text. Before, a sentence with a thought set off by a dash. After, the thought as its own sentence.

**Semicolons.** GOV.UK bans them because readers misread them. Microsoft says to break the sentence up. Google says to avoid them where possible.

**Colons.** Microsoft advises against a colon that introduces a clarification inside a sentence and says to rephrase or split. Google allows that colon. The Link and Think catalogue names the "setup, colon, tidy payload" pattern as a Claude cliché. The rule bans the in-sentence reveal only and keeps colons before lists, tables, code, quotations and after short labels. The old "three or more items" limit had no support and is gone.

**Parentheses.** Google says readers skip parentheses, so keep important content out of them and keep asides short. GOV.UK allows round brackets. A total ban also forbids useful glosses such as a file path, so the rule allows short glosses.

**Start with the point.** GOV.UK puts the most important information first. Microsoft says to get to the point fast. NN/g recommends the inverted pyramid. The Claude Code Concise style drops the lead-in. Meta-signposting and significance signalling are catalogued Claude habits.

**Fragments.** No authority bans fragments, and Microsoft's own example uses one. Headings, list items and table cells are fragments by nature. The target is the teaser fragment, which the catalogue calls the suspense hook.

**List lead-ins.** Google requires a complete introductory sentence unless a heading comes right before the list, and its own example is "The fields are defined as follows:". Microsoft and GOV.UK also want a lead-in or heading. The old rule banned all lead-ins, which contradicted all three. The rewrite allows a heading or a lead-in and bans only the empty announcement. A lead-in must say something specific, such as a count or a finding.

**Contrast only between real alternatives.** The Wikipedia essay lists negative parallelisms as a sign of AI writing and the catalogue calls the pattern the contrastive binary. No style guide covers it directly.

**Metaphors.** Google discourages figurative language and idioms. Anthropic's own prompt allows a metaphor that illustrates a point. The rule keeps that middle ground.

**Word list.** Each word carries its evidence. "Leverage" is advised against by Google, Microsoft and GOV.UK. "Robust" is on the GOV.UK words-to-avoid list and Wikipedia's words to watch. "Delve" is a Wikipedia word to watch. "Seamless" appears only in Wikipedia's promotional-language examples, so its evidence is weak and it stays as a Claude tic. "Honestly" and "genuinely" are words Anthropic's own claude.ai prompt tells Claude to avoid. "Load-bearing" is tracked as a Claude habit in claude-code issue 53454. "Key" as an adjective is advised against by Google and GOV.UK. "Crux" has no source and is marked personal. Anthropic advises telling the model what to do instead of what not to do, so each entry names the replacement.

**Bold.** Google limits bold to UI elements and run-in headings. Wikipedia lists heavy bold as a sign of AI writing. Anthropic's sample prompt says to avoid bold in chat. The old file had two contradicting bold rules, which are now one.

**Length and endings.** Claude's constitution says to avoid padding and repetition of prior content. The Opus 5 guide warns against redundant summaries. The Concise style drops the closing recap. Wikipedia lists "let me know" closers as a sign of AI writing.

**Headings in chat.** No source gives a word threshold, so the old "over 500 words" rule is gone. Anthropic asks for the minimum formatting that keeps a chat reply clear, so headings appear only when a reply has sections a reader would jump between.

**Bullets and paragraphs.** Google uses lists for sequences and collections and tables for structured data. The guidelines say to use lists often but not to overuse them. Anthropic's sample prompt prefers prose for technical explanation, which is why cause and sequence stay in paragraphs.

**Sections and corrections.** GOV.UK organises content around user needs and the guidelines ask for a topic sentence first. The Opus 5 guide says to state corrections plainly and briefly, and to check in only when different readings of a request lead to different work.

**Documents.** NN/g found that most users scan, and GOV.UK reports the F-shaped reading pattern, so sections lead with the conclusion and headings are labels. Microsoft suggests three to seven lines per paragraph and the guidelines allow up to eight sentences, so the old "two or three sentences" became "at most five". Google and Microsoft both support run-in bold labels in long lists.

**Wrapping.** No plain-language authority covers source wrapping, and Google's Markdown guide prefers 80 columns. The Confluence problem happens only when raw Markdown source is pasted, because rendered Markdown turns a single newline into a space. The rule is therefore scoped to deliverables that get pasted. Tracked files keep whatever wrapping they already use. As of the 2026-09-29 audit, only four tracked files were hard-wrapped near 120 columns.

**Code comments.** Google's engineering practices say comments should explain why, not what. The Codex and Antigravity mirrors already said "what the code does now and why".

## Where the authorities disagree

| Topic | Positions | Rule taken |
| --- | --- | --- |
| Em dashes | Google and Microsoft accept them in moderation. GOV.UK avoids them. | Banned, because of model overuse |
| Semicolons | Strunk allows them. GOV.UK bans them. Google and Microsoft avoid them. | Banned |
| In-sentence colon | Google allows it. Microsoft advises rephrasing. | Banned inside a sentence, allowed before lists and after labels |
| List lead-ins | All three guides require one. The old rule banned them. | Required, but it must say something specific |
| Bullets vs prose | Google and Microsoft favour lists for scanning. Anthropic prefers prose for technical explanation. | Bullets for parallel items, prose for cause and sequence |
| Markdown wrapping | Google's Markdown guide wraps at 80. Confluence pasting breaks on hard wraps. | Scoped to pasted deliverables |

## Maintenance

- A new rule needs a source key or the [Personal] tag, and positive wording that says what to do.
- Keep the rule file under 60 lines. Rationale and examples belong here.
- Re-check the sources when the `verified` date is older than 90 days, and refresh the stamp only after re-reading them.
- After a rule change, update the reminder line in `claude/home/settings.snippet.json` and the condensed Codex and Antigravity copies where the change applies to them.
