---
name: audit
description: "Audits the ai-toolkit standards against their cited sources and writes a dated findings register with proposed diffs. Run it from the ai-toolkit checkout every 90 days or when the freshness job warns. Never runs on its own."
argument-hint: "[all|android|ios|design|pr-review|writing|agents] [--stale-only]"
disable-model-invocation: true
metadata:
  verified: 2026-09-29
  sources: references/sources.md
---

# Toolkit audit: $ARGUMENTS

Re-check the toolkit's rules and references against their sources, classify every rule, and write a register. Apply nothing. The register and its proposed diffs are the deliverable.

## Preconditions
1. The working directory is the ai-toolkit checkout (`.claude-plugin/marketplace.json` has `"name": "ai-toolkit"`) and `git status --porcelain` is empty.
2. Take today's date from `date -u +%F`, never from memory. If the current branch is `main`, create `chore/audit-<date>`.

## Procedure
1. **Inventory.** Run `python3 tools/freshness.py --json`. Keep the rows whose file matches the domain argument (`all` keeps everything, `android` keeps Android rules and references, and so on). With `--stale-only`, keep only rows 90 days old or older. Order by age, oldest first.
2. **Fetch every source.** For each file, fetch each URL in its `sources:` list, or every URL in its body when `sources: inline`. Follow the fetch tips in `references/sources.md` (Apple JSON endpoint, Material 3 site map plus a web search for the page text, raw GitHub URLs). Record per URL the status, the date fetched and the exact sentence you rely on. A page that returns only a shell is "content Unverified".
3. **Classify every rule.** Treat each bullet or sentence that states a requirement as one rule with the ID `file:line`. Use the classes in `references/rubric.md`. SUPPORTED, PARTIAL, COMMUNITY, HOUSE, WRONG or STALE, with an Unverified flag when no source could be read. Note conflicts between files in the "Conflicts with" column. Design rules also get their tier from the rule file.
4. **Write the register.** Copy `references/register-template.md` to `docs/audits/<date>-audit.md` and fill it. One row per rule, a summary count per class and per file, and a "Proposed changes" section with a unified diff per canonical file. List the mirror files each diff touches, using the groups in `tools/mirrors.toml`. Do not apply any diff.
5. **Refresh stamps, only on confirmation.** List the files where every source was fetched and no rule is WRONG or STALE. Ask the user to confirm. Only then set `verified:` to today in those canonical files and their mirrors, and run `python3 scripts/ci/check_parity.py --write`, `python3 tools/mirror_parity.py` and `python3 tools/freshness.py`. A file with a WRONG or STALE rule keeps its old date until the fix lands.
6. **Report.** Give the counts, the register path, the files eligible for a stamp refresh, and the follow-up PRs you suggest, one logical change each.

## Rules of the audit
- Look up, never recall. A version, a deadline or a deprecation you cannot fetch is Unverified, not asserted.
- A HOUSE rule is a deliberate standard. Check it for internal consistency and for a source that now contradicts it. Never report it as unsourced.
- Quote the sentence you rely on. A classification without a quote is a guess.
- Prefer the smallest diff that makes the rule true. Rewording for style belongs in a separate PR.
