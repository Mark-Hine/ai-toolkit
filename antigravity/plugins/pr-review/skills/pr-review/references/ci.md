# CI/CD integration

How to run this skill headless in a pipeline. The review itself is unchanged — same phases, same
grading, same adversarial pass — but CI mode never asks anything (protocol.md §24), writes both
artifacts to the staging directory, and lets the pipeline post `findings.json` to the PR.

## Contract

- **Trigger:** a PR-validation pipeline (branch policy build) — the review runs against the PR's
  merge-base..head, exactly like a local run.
- **Mode switch:** `PR_REVIEW_MODE=ci` in the environment.
- **Inputs:** source/target from the CI system's PR variables; everything else Phase 0 infers,
  recording each inference in the JSON's `scope.inferences`.
- **Outputs:** `findings.json` + the rendered markdown document in the artifact staging
  directory, published as build artifacts.
- **Posting:** the pipeline runs `scripts/post_azdo.py` — inline threads at `file:line`, a summary
  thread, a reviewer vote. Idempotent across re-runs via `[pr-review:<ID>]` markers.
- **Gating:** the poster's `--fail-on-verdict` exits 1 when the computed vote is negative, so a
  branch policy can require the step. Prefer gating on the vote (a human resolving a Question
  thread in the PR UI lifts the gate without a re-run) over gating on the JSON's verdict field.
- **Secrets:** the token comes from the pipeline (`System.AccessToken` or a PAT variable). It is
  never written into the JSON, the document, or the logs.

## Azure DevOps

The build identity needs **Contribute to pull requests** on the repo. Example:

```yaml
# azure-pipelines.yml — PR review stage (wire as the PR build via branch policy)
trigger: none            # PR-triggered via branch policy, not CI trigger

pool:
  vmImage: ubuntu-latest

variables:
  PR_REVIEW_MODE: ci

steps:
  - checkout: self
    fetchDepth: 0        # full history — the review needs the merge-base

  # Check out a pinned, trusted ai-toolkit revision separately and copy its
  # codex/skills/pr-review folder to ~/.agents/skills/pr-review before this step.
  # Provision the Codex CLI on the runner before exposing the secret.
  - bash: |
      codex exec --ephemeral --sandbox workspace-write \
        --add-dir "$REVIEW_ARTIFACT_DIR" \
        'Use $pr-review in CI mode. Review the PR named by the SYSTEM_PULLREQUEST_* variables. Write both artifacts to REVIEW_ARTIFACT_DIR. Do not post findings.'
    displayName: Run Codex PR review
    env:
      CODEX_API_KEY: $(CODEX_API_KEY)  # secret scoped to this step
      PR_REVIEW_MODE: ci
      REVIEW_ARTIFACT_DIR: $(Build.ArtifactStagingDirectory)

  - publish: $(Build.ArtifactStagingDirectory)
    artifact: pr-review
    displayName: Publish review artifacts

  - bash: |
      python3 "$(Build.SourcesDirectory)/scripts-path-to/post_azdo.py" \
        "$(Build.ArtifactStagingDirectory)"/pr-review-*.json --fail-on-verdict
    displayName: Post findings to PR
    env:
      SYSTEM_ACCESSTOKEN: $(System.AccessToken)
```

Notes:

- `SystemAccessToken` must be mapped into the step's env explicitly (as above) — it is not exposed
  by default.
- The poster reads org/project/repo/PR from the predefined variables
  (`SYSTEM_COLLECTIONURI`, `SYSTEM_TEAMPROJECT`, `BUILD_REPOSITORY_NAME`,
  `SYSTEM_PULLREQUEST_PULLREQUESTID`); flags override for local testing.
- To warn instead of fail, drop `--fail-on-verdict` and emit
  `##vso[task.complete result=SucceededWithIssues]` when the poster prints a negative vote.
- Re-runs on new pushes are the CI re-review: Phase R updates `findings.json` statuses, and the
  poster resolves threads whose `verify_fixed_when` now passes and reactivates regressions.

## Any other CI system

The design is deliberately splittable: the skill produces `findings.json` (host-agnostic —
`references/output.md`); only the poster is Azure DevOps-specific. For another host, publish the
JSON as an artifact and gate on `verdict`, or write a small adapter against the same file — the
poster's internals already separate the generic findings→actions core from the ADO REST calls.
For GitHub Actions use the official `openai/codex-action` with its authenticated proxy, then map findings to
`gh pr review --request-changes` / review comments via the GitHub API; markers and idempotency
carry over unchanged.

## Runner setup

Install the Codex CLI with `npm install -g @openai/codex` in a provisioning step, before exposing any API credential. Pin the tested CLI and toolkit versions in production. Make the PR refs and pinned toolkit skill available before starting the review. The example is a migration template, not a provisioned or tested Azure pipeline. No credentials are installed by the local toolkit installer.

Codex executes CI reviews with [`codex exec`](https://learn.chatgpt.com/docs/non-interactive-mode). Keep the review credential scoped to the review invocation. On GitHub Actions, prefer the official [Codex action](https://developers.openai.com/codex/github-action) and its authenticated proxy.
