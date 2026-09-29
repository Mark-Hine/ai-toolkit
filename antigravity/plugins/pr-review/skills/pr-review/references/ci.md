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
- **Posting:** the pipeline runs `scripts/post_azdo.py` from the installed skill. It creates inline threads
  at `file:line`, a summary thread, a reviewer vote. Idempotent across re-runs via
  `[pr-review:<ID>]` markers. Findings whose status is `open`, `regressed` or `partial` gate the
  vote. A thread a human resolved as Won't Fix or By Design is never reopened, and a resolved
  Question thread lifts that Question's gate.
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
  CODEX_VERSION: '<tested version>'  # the CLI version you tested
  AI_TOOLKIT_REF: 'main'             # pin to a tag in production

steps:
  - checkout: self
    fetchDepth: 0                    # full history, the review needs the merge-base

  - task: NodeTool@0
    inputs: { versionSpec: '22.x' }

  - bash: |
      set -euo pipefail
      npm install -g "@openai/codex@${CODEX_VERSION}"
      git clone --depth 1 --branch "$AI_TOOLKIT_REF" https://github.com/Mark-Hine/ai-toolkit.git "$AGENT_TEMPDIRECTORY/ai-toolkit"
      mkdir -p ~/.agents/skills
      cp -R "$AGENT_TEMPDIRECTORY/ai-toolkit/codex/skills/pr-review" ~/.agents/skills/pr-review
      echo "##vso[task.setvariable variable=PR_REVIEW_SKILL_DIR]$HOME/.agents/skills/pr-review"
    displayName: Install Codex and pr-review

  - bash: |
      set -euo pipefail
      codex exec --ephemeral --sandbox workspace-write \
        --add-dir "$REVIEW_ARTIFACT_DIR" \
        'Use $pr-review in CI mode. Review the PR named by the SYSTEM_PULLREQUEST_* variables. Write pr-review-<PR#>-<YYYY-MM-DD>.json and .md to REVIEW_ARTIFACT_DIR. Do not post findings.'
    displayName: Run Codex PR review
    env:
      CODEX_API_KEY: $(CODEX_API_KEY)  # secret, scoped to this step only
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
      python3 "$PR_REVIEW_SKILL_DIR/scripts/post_azdo.py" "${files[0]}" --fail-on-verdict
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

## Any other CI system

The design is deliberately splittable: the skill produces the findings JSON (host-agnostic, see
`references/output.md`). Only the poster is Azure DevOps-specific. For another host, publish the
JSON as an artifact and gate on `verdict`, or write a small adapter against the same file. The
poster's internals already separate the generic findings-to-actions core from the ADO REST calls.
<!-- layer-specific:start -->
For GitHub Actions use the official `openai/codex-action` with its authenticated proxy, then map findings to
`gh pr review --request-changes` or review comments via the GitHub API. Markers and idempotency
carry over unchanged.

## Runner setup

Install the Codex CLI with `npm install -g @openai/codex@<version>` in a provisioning step, before exposing any API credential. Codex executes CI reviews with [`codex exec`](https://learn.chatgpt.com/docs/non-interactive-mode). Keep the review credential scoped to the review invocation. On GitHub Actions, prefer the official [Codex action](https://developers.openai.com/codex/github-action) and its authenticated proxy. No credentials are installed by the local toolkit installer.
<!-- layer-specific:end -->
