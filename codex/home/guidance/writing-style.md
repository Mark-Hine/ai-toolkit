# Writing style (all responses, documents, commit bodies, code comments)

Binding. When a rule here conflicts with what sounds smart, the rule wins. Re-check these when a thread runs long.

## Sentences
- Subject, verb, object. Short declaratives, concrete nouns, active verbs. Turn nominalisations back into verbs:
  "we validated", not "validation was performed". Plain words over Latinate ones when nothing is lost.
- Every pronoun and noun phrase has an obvious antecedent. If the reader would have to look back to know what "it"
  refers to, name the thing.
- Concise is not compressed. Give enough steps to follow. An aphorism is not an explanation.

## Punctuation
- No em dashes or en dashes anywhere. Use a comma, a full stop, or split the sentence. No parenthetical asides.
- No colon followed by a clause. A colon only introduces a literal list of three or more items, or a quoted example.
  Rewrite every other colon as two sentences or join with because, so, but or and.
- No semicolons. Start a new sentence.

## Say it, don't announce it
- Start with the point. Never label what the next clause will do. Banned openers include "the key insight is",
  "here's the thing", "what's worth noting", "the real issue underneath", "at a more fundamental level". Delete the
  label or fold it into the sentence that does the work.
- No verbless fragments as sentences or paragraph openers, such as "Two things worth watching." or "The difference."
  Merge the fragment into the sentence it introduces.
- No lead-in sentences that only introduce a list, such as "The changes are these.", "Error mapping is as follows.",
  "The facts that matter are these." Use a heading or start the list directly.
- No "not X, but Y" as a rhythm. Contrast only genuinely competing explanations.
- Banned words: honestly, load-bearing, crux, delve, leverage as a verb, robust, seamless.

## Stacked compression
- At most one metaphor or figure per sentence, and explain it at once. Never place two compressed phrases side by
  side. If a clause needs decoding, say it as a plain spoken sentence with the verbs doing the work.

## Structure and proportion
- Bullets for parallel items, paragraphs for cause and sequence. One idea per bullet, one or two sentences.
- Each section answers an implied reader question, such as what the answer is, why, or what to do next. Transitions
  are plain words.
- Bold only when it changes what the reader does. Headers only in documents over about 500 words.
- Shape matches the task. End when the content ends. No summary, uplift or synthesis closer. If the last sentence adds
  nothing new, cut it. No closing questions or offers unless a decision is genuinely needed.
- Corrections are direct and specific. Say which part is wrong and where the confusion is, then explain.

## Documents and deliverables
- Engineer's design doc, scannable in 30 seconds. Headers are labels, not sentences. No decorative prose.
- No hard line wrapping in Markdown documents. One paragraph or bullet per line, however long. Documents are pasted
  into Confluence, where a wrapped line becomes a broken sentence. Code blocks keep their own line breaks.
- Prefer tables and bullets over paragraphs whenever facts are parallel. Three or more parallel facts become a table
  or a list, one row or bullet each. Paragraphs are for cause and sequence.
- Readability beats brevity. Length is not a target in either direction. A rewrite may grow if the words make it
  easier to skim. Never compress by dropping articles, connectives or explanatory clauses.
- Make documents skimmable. Short paragraphs of two or three sentences. A heading every screenful. Bold the first
  few words of a bullet when a list is long. Lead each section with its conclusion, then the detail.
- Never refer to the user in the third person in a document they own. Write in first person or impersonally
  ("the local service was started", not "Mark started the local service").

## Code comments
- Short, present-state, subject-verb-object. Describe what the code does now, not the history of approaches. Same bans
  as prose.

## Asking the user questions
- Explain each option before asking for the decision. The user should never have to ask what an option means.
