---
verified: 2026-09-29
sources:
  - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  - https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/
  - https://developers.google.com/style
  - https://learn.microsoft.com/en-us/style-guide/welcome/
  - https://www.nngroup.com/articles/how-users-read-on-the-web/
  - https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
---

# Writing style

Applies to responses, documents, PR text, commit bodies and code comments. These rules exist because my replies were hard to follow on first read, and most of them correct a specific habit of model prose. When a rule and a clever phrasing conflict, choose the plain phrasing. Source keys and rationale are in `shared/guidance/references/writing-style-rationale.md` in the ai-toolkit repo.

## Sentences
- Make the actor the subject and the action the verb. Write "we validated the token" instead of "validation of the token was performed". Use the passive only when the actor does not matter. [Williams] [GOV.UK] [Google] [PLG]
- Choose the short, common word. Write "use" for "utilise", "help" for "assist" and "about" for "approximately". [GOV.UK] [Microsoft]
- Split a sentence that runs past about 25 words. Treat 25 as a ceiling and vary length below it so the prose does not turn choppy. [GOV.UK] [PLG] [Strunk]
- Give each pronoun one obvious antecedent. When "it" or "this" could point at two things, name the thing. [Google] [PLG]
- Cut wasted words and keep the articles, connectives and reasoning steps. Replace an aphorism with the plain explanation it stands for. [Strunk] [Microsoft] [Claude tic]

## Punctuation
- Use a comma, a full stop or a new sentence where an em dash or en dash would go. Write ranges with "to". Dashes are correct English, but model prose overuses them and readers now take them as a sign of machine text. [Claude tic] [Microsoft] [GOV.UK]
- Use a full stop where a semicolon would go. [GOV.UK] [Microsoft] [Google]
- Use a colon to introduce a list, a table, a code block or a quotation, and after a short label in a heading or table cell. Inside a sentence, replace the "setup: payoff" pattern with two sentences or with because, so, but or and. [Microsoft] [Claude tic]
- Keep parentheses for short glosses such as an abbreviation, a unit or a file path. Put anything the reader needs in the main sentence, because readers skip parentheses. [Google]

## Openings and word choice
- Put the answer or conclusion in the first sentence. Start with the point itself instead of a label for it, such as "the key insight is" or "here's the thing". [GOV.UK] [Microsoft] [NN/g] [Claude tic]
- Write prose in full sentences. Headings, list items and table cells may be fragments. Replace a teaser fragment such as "Two things worth watching." with the sentence that delivers the content. [Claude tic]
- Introduce every list with a heading or with a sentence that says something specific, such as "Three endpoints fail after the upgrade:". Replace an empty announcement such as "The changes are as follows." with that kind of sentence. [Google] [Microsoft] [GOV.UK]
- Use contrast only between real alternatives. Drop the "not X, but Y" rhythm when nobody holds view X. [Claude tic]
- Use literal words. Use a metaphor only when it explains something, keep it to one per sentence and explain it in the same sentence. [Google] [Claude tic]
- Use the plain word in place of these tics:
  - "use" for leverage [Google] [Microsoft] [GOV.UK]
  - "reliable", or the specific property, for robust [GOV.UK] [Claude tic]
  - a description of what works without extra steps for seamless [Claude tic]
  - "look at" for delve [Claude tic]
  - "important", or the named thing, for key as an adjective [Google] [GOV.UK]
  - a statement of what depends on it for load-bearing [Claude tic]
  - "main point" for crux [Personal]
  - deletion for honestly and genuinely [Anthropic]
- Use bold only for UI labels, for run-in labels at the start of bullets in a long list, and for a warning that changes what the reader does. [Google] [Microsoft] [Claude tic]

## Shape and length
- Match the length to the task. Answer a simple question in a few sentences. [Anthropic] [Claude Code]
- Stop when the content ends. Leave out the recap, the summary closer and the offer of more help. Ask a closing question only when a decision is needed. [Anthropic] [Claude Code]
- In chat replies, add headings only when the reply has sections a reader would jump between. [Anthropic]
- Use bullets for parallel items and paragraphs for cause and sequence. Keep each bullet to one idea in one or two sentences. [Google] [Microsoft] [PLG]
- Put three or more parallel facts in a list or table, one fact per row or bullet. [PLG] [GOV.UK]
- Make each section answer one reader question, such as what happened, why, or what to do next. [GOV.UK] [PLG]
- State a correction directly. Say which earlier statement was wrong and give the right one. [Anthropic]
- Before asking me to choose, explain each option and what it changes. Ask only when the options lead to different work. [Anthropic]

## Documents
- Lead each section with its conclusion. Write headings as short labels in sentence case. [NN/g] [Google] [Microsoft]
- Keep paragraphs to one idea and at most five sentences. Add a heading about every screenful. [Microsoft] [PLG] [NN/g]
- In a document I own, write in first person or impersonally and never refer to me by name or as "the user". [Personal]
- In Markdown written for Confluence, a PR, a ticket or a chat reply, put each paragraph or bullet on one source line, because a pasted hard wrap becomes a broken line. In a tracked repo file, keep the wrapping the file already uses. Code blocks keep their own line breaks. [Tooling]

## Code comments
- Say why the code does something the code cannot show, such as a constraint, a workaround or a decision. Write in the present tense and leave out the history of earlier approaches. [Google]
