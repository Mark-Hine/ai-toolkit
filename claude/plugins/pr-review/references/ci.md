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

  - bash: |
      npm install -g @anthropic-ai/claude-code
      claude -p "/pr-review ci: review PR $(System.PullRequest.PullRequestId), \
        source $(System.PullRequest.SourceBranch) target $(System.PullRequest.TargetBranch). \
        Write findings.json and the document to $(Build.ArtifactStagingDirectory)." \
        --permission-mode acceptEdits
    displayName: Run PR review
    env:
      ANTHROPIC_API_KEY: $(ANTHROPIC_API_KEY)   # secret variable
      PR_REVIEW_MODE: ci

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
A GitHub Actions sketch: run the same `claude -p` step, then map findings to
`gh pr review --request-changes` / review comments via the GitHub API; markers and idempotency
carry over unchanged.
