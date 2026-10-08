---
verified: 2026-10-08
sources: house
---

# CI/CD integration

How to run this skill headless in a pipeline. The review itself is unchanged, with the same phases, the same
grading and the same adversarial pass, but CI mode never asks anything (protocol.md §24), writes both
artifacts to the staging directory, and lets the pipeline post the findings JSON to the PR.

## Contract

- **Trigger:** a PR-validation pipeline (branch policy build). The review runs against the PR's
  merge-base..head, exactly like a local run.
- **Mode switch:** `PR_REVIEW_MODE=ci` in the environment.
- **Inputs:** source/target from the CI system's PR variables. Phase 0 infers everything else,
  recording each inference in the JSON's `scope.inferences`.
- **Outputs:** `pr-review-<PR#>-<YYYY-MM-DD>.json` and `pr-review-<PR#>-<YYYY-MM-DD>.md` in the
  artifact staging directory, published as build artifacts. The poster globs `pr-review-*.json`
  and expects exactly one.
- **Posting:** the pipeline runs `scripts/post_review.py` from the installed skill, with
  `--host azure` or `--host github`. It creates an anchored thread at `file:line` for each Blocker,
  Question and Major, one summary comment that also lists the nits, and a reviewer vote. Re-runs
  find their threads by the `pr-review <ID>` footer, so they update threads instead of duplicating
  them. Findings whose status is `open`, `regressed` or `partial` gate the vote. A thread a human
  resolved is never reopened, and a resolved Question thread lifts that Question's gate.
  [`posting.md`](posting.md) shows what each comment contains. `scripts/post_azdo.py` still works
  as an alias for `--host azure`.
- **Gating:** the poster's `--fail-on-verdict` exits 1 when the computed vote is negative, so a
  branch policy can require the step. Prefer gating on the vote (a human resolving a Question
  thread in the PR UI lifts the gate without a re-run) over gating on the JSON's verdict field.
- **Secrets:** the token comes from the pipeline (`System.AccessToken` mapped to
  `SYSTEM_ACCESSTOKEN`, or a PAT variable). It is never written into the JSON, the document, or
  the logs. Expose the model API key to the review step only.
- **Pinning:** pin the agent CLI version and the ai-toolkit ref you tested. An unpinned install in
  a merge gate changes behaviour without a commit.

## Azure DevOps

The build identity needs **Contribute to pull requests** on the repo. The example below is a
template. Run it once on a scratch pipeline before wiring it as a branch policy.

<!-- layer-specific:start -->
```yaml
# azure-pipelines.yml, PR review stage (wire as the PR build via branch policy)
trigger: none                        # PR-triggered via branch policy, not CI trigger

pool:
  vmImage: ubuntu-latest

variables:
  AI_TOOLKIT_REF: 'main'             # pin to a tag in production

steps:
  - checkout: self
    fetchDepth: 0                    # full history, the review needs the merge-base

  - bash: |
      set -euo pipefail
      curl -fsSL https://antigravity.google/cli/install.sh | bash   # pin once a versioned installer exists
      git clone --depth 1 --branch "$AI_TOOLKIT_REF" https://github.com/Mark-Hine/ai-toolkit.git "$AGENT_TEMPDIRECTORY/ai-toolkit"
      mkdir -p ~/.gemini/config/plugins
      ln -sfn "$AGENT_TEMPDIRECTORY/ai-toolkit/antigravity/plugins/pr-review" ~/.gemini/config/plugins/pr-review
      echo "##vso[task.setvariable variable=PR_REVIEW_SKILL_DIR]$AGENT_TEMPDIRECTORY/ai-toolkit/antigravity/plugins/pr-review/skills/pr-review"
    displayName: Install Antigravity CLI and pr-review

  - bash: |
      set -euo pipefail
      ~/.local/bin/agy --sandbox --dangerously-skip-permissions --print-timeout 45m \
        --add-dir "$REVIEW_ARTIFACT_DIR" \
        -p 'Use the pr-review skill in CI mode. Review the PR named by the SYSTEM_PULLREQUEST_* variables. Write pr-review-<PR#>-<YYYY-MM-DD>.json and .md to REVIEW_ARTIFACT_DIR. Do not post findings.'
    displayName: Run Antigravity PR review
    env:
      GEMINI_API_KEY: $(GEMINI_API_KEY)   # secret, scoped to this step only
      PR_REVIEW_MODE: ci
      REVIEW_ARTIFACT_DIR: $(Build.ArtifactStagingDirectory)

  - publish: $(Build.ArtifactStagingDirectory)
    artifact: pr-review
    condition: succeededOrFailed()
    displayName: Publish review artifacts

  - bash: |
      set -euo pipefail
      shopt -s nullglob
      files=("$REVIEW_ARTIFACT_DIR"/pr-review-*.json)
      [ "${#files[@]}" -eq 1 ] || { echo "Expected one findings JSON, found ${#files[@]}"; exit 1; }
      python3 "$PR_REVIEW_SKILL_DIR/scripts/post_review.py" "${files[0]}" --host azure --fail-on-verdict
    displayName: Post findings to PR
    env:
      SYSTEM_ACCESSTOKEN: $(System.AccessToken)
      REVIEW_ARTIFACT_DIR: $(Build.ArtifactStagingDirectory)
```
<!-- layer-specific:end -->

Notes:

- `System.AccessToken` must be mapped into the step's env as `SYSTEM_ACCESSTOKEN` explicitly (as
  above). It is not exposed by default.
- The poster reads org/project/repo/PR from the predefined variables
  (`SYSTEM_COLLECTIONURI`, `SYSTEM_TEAMPROJECT`, `BUILD_REPOSITORY_NAME`,
  `SYSTEM_PULLREQUEST_PULLREQUESTID`). Flags override for local testing.
- To warn instead of fail, drop `--fail-on-verdict` and emit
  `##vso[task.complete result=SucceededWithIssues]` when the poster prints a negative vote.
- Re-runs on new pushes are the CI re-review: Phase R updates the findings JSON statuses, and the
  poster resolves threads whose `verify_fixed_when` now passes and reactivates regressions.
- The poster rejects a findings file with an unknown severity or status, or with a gating Blocker
  under a verdict other than `request_changes`, before it sends anything.

## GitHub Actions

The workflow token needs `pull-requests: write`. A pull request from a fork gets a read-only token
and no secrets, so the review and posting steps only run for branches in the same repository. An
approval from `GITHUB_TOKEN` also needs the repository setting **Allow GitHub Actions to create and
approve pull requests**. Without it, or on the author's own pull request, the poster leaves a
comment review instead. Run the workflow once on a scratch pull request before requiring it.

<!-- layer-specific:start -->
```yaml
# .github/workflows/pr-review.yml
name: pr-review
on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    env:
      AI_TOOLKIT_REF: 'main'             # pin to a tag in production
      REVIEW_ARTIFACT_DIR: ${{ runner.temp }}/pr-review
      PR_NUMBER: ${{ github.event.pull_request.number }}
      HEAD_REF: ${{ github.head_ref }}
      BASE_REF: ${{ github.base_ref }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0                 # full history, the review needs the merge-base

      - name: Install Antigravity CLI and pr-review
        run: |
          set -euo pipefail
          curl -fsSL https://antigravity.google/cli/install.sh | bash   # pin once a versioned installer exists
          git clone --depth 1 --branch "$AI_TOOLKIT_REF" https://github.com/Mark-Hine/ai-toolkit.git "$RUNNER_TEMP/ai-toolkit"
          mkdir -p ~/.gemini/config/plugins
          ln -sfn "$RUNNER_TEMP/ai-toolkit/antigravity/plugins/pr-review" ~/.gemini/config/plugins/pr-review
          echo "PR_REVIEW_SKILL_DIR=$RUNNER_TEMP/ai-toolkit/antigravity/plugins/pr-review/skills/pr-review" >> "$GITHUB_ENV"

      - name: Run Antigravity PR review
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}   # scoped to this step only
          PR_REVIEW_MODE: ci
        run: |
          set -euo pipefail
          mkdir -p "$REVIEW_ARTIFACT_DIR"
          ~/.local/bin/agy --sandbox --dangerously-skip-permissions --print-timeout 45m \
            --add-dir "$REVIEW_ARTIFACT_DIR" \
            -p 'Use the pr-review skill in CI mode. Review the PR named by PR_NUMBER, HEAD_REF and BASE_REF. Write pr-review-<PR#>-<YYYY-MM-DD>.json and .md to REVIEW_ARTIFACT_DIR. Do not post findings.'

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: pr-review
          path: ${{ env.REVIEW_ARTIFACT_DIR }}

      - name: Post findings to PR
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          set -euo pipefail
          shopt -s nullglob
          files=("$REVIEW_ARTIFACT_DIR"/pr-review-*.json)
          [ "${#files[@]}" -eq 1 ] || { echo "Expected one findings JSON, found ${#files[@]}"; exit 1; }
          python3 "$PR_REVIEW_SKILL_DIR/scripts/post_review.py" "${files[0]}" --host github --fail-on-verdict
```
<!-- layer-specific:end -->

The poster reads the repository and pull request number from `GITHUB_REPOSITORY` and the event
payload. It anchors each comment at `scope.source_head`. A finding on a line outside the diff goes
into the summary under "Outside the diff", because GitHub anchors review comments only on diff
lines. To warn instead of fail, drop `--fail-on-verdict`.

## Any other host

The findings JSON is host-neutral (`references/output.md`). For another host, publish it as an
artifact and gate on `verdict`, or add an adapter class to `post_review.py` with the same methods
as `AzureDevOps` and `GitHub`. The core decides what to create, reply to, resolve or reopen, and
the adapter maps that onto the host's API.
