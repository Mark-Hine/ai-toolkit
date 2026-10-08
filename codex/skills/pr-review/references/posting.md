---
verified: 2026-10-08
sources: house
---

# Posting a review from a local session

Local mode posts nothing unless the user asks. When they ask, post through one of the routes below.
CI posting is in [`ci.md`](ci.md). Every route posts the same content, because each one starts from
`scripts/post_review.py`, either running it or posting what it emits.

## What lands on the PR

- **One anchored thread per Blocker, Question and Major**, at the finding's causal `file:line`. The
  header names the severity and what it asks, such as "Major (please ticket, does not block the
  merge)". The body carries the PR comment, a **Why** line from `root_cause`, an **Also at** line
  from `symptom_sites` and the **Verified fixed when** criterion.
- **One summary comment** with:
  - the verdict and the scope statement (protocol.md §2);
  - a severity legend;
  - an index that links every finding's thread;
  - the nits;
  - the "Good in this delta" list.

  Nits get no thread of their own, so a branch policy that requires every comment to be resolved
  doesn't make the author click through them.
- **A footer marker** such as `_pr-review M1 · see the review summary on this PR for every finding_`
  ends every body. Re-runs find their threads by it, so a re-review updates threads instead of
  duplicating them. The poster also recognises the older `[pr-review:M1]` marker.
- **No vote** unless the user asks. The vote lands under the user's name.

## Before posting

1. Confirm the PR head hasn't moved. `git ls-remote origin <source branch>` must print
   `scope.source_head`. If it moved, re-review first (Phase R).
2. Run the poster with `--dry-run --no-vote` and show the user the bodies. With a token present,
   the dry run reads the live threads, so it also shows what a re-run would update.
3. Post only after the user confirms.

The poster picks the host from `--host`, then `scope.host` in findings.json, then the CI
environment, then the `origin` remote URL.

## Azure DevOps

| Route | When | How |
|---|---|---|
| A. PAT | The user has or can create a PAT | Create a PAT with **Code (Read & write)**. Store it in a file only the user can read, for example `~/.ado-pat` with mode 600. Run `post_review.py <findings.json> --host azure --org-url <org> --project <project> --repo <repo> --pr <n> --token-file ~/.ado-pat` |
| B. Entra token | `az` is installed and signed in | Set `AZURE_DEVOPS_EXT_PAT` from `az account get-access-token --resource 499b84ac-1321-427f-aa17-267ca6975798 --query accessToken -o tsv` in the same command. The poster sends a JWT-shaped token as a bearer token |
| C. Azure DevOps MCP server | An MCP server with pull-request thread tools is connected | Run the poster with `--emit-threads threads.json`, then create each `create_thread` entry in order and the `summary` entry last |

For route C, create each anchored thread with only `filePath` and the right-file start and end line
and offset. Leave out `firstComparingIteration`, `secondComparingIteration` and `changeTrackingId`.
The service rejects iteration 0 and attaches the thread to the latest iteration by itself. Cast no
vote through MCP. `--emit-threads` doesn't read the PR, so on a PR that already carries pr-review
threads use route A or B, which update those threads in place.

## GitHub

| Route | When | How |
|---|---|---|
| D. `gh` CLI token | `gh auth status` shows a signed-in account | Run `post_review.py <findings.json> --host github --repo <owner/name> --pr <n>`. The poster takes the token from `gh auth token`, so nothing needs exporting |
| E. GitHub MCP server | An MCP server with pull-request review tools is connected | Post from `--emit-threads` as in route C. Anchor each comment at the head commit on the right side |

GitHub anchors a review comment only on a line inside the diff. The poster moves a finding it can't
anchor into the summary under "Outside the diff", and route E should do the same. GitHub refuses an
approval or a change request on the author's own pull request, and the poster then leaves a comment
review instead.

## Tokens

Never put a token in a prompt, a command the session echoes, the findings JSON or the review
document. Pass it in an environment variable set in the same command, or in a file named with
`--token-file`. The poster reads the file and never prints the token.
