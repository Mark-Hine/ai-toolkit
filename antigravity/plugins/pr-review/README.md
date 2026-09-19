# pr-review

Formal pull request and release promotion review plugin for Google Antigravity.

Produces verified JSON (`findings.json`) and Markdown review deliverables citing published standards, grading findings (Blocker, Question, Major, Nit), scoping approvals, and verifying environment promotions.

## Skill

- `/pr-review`: Write a formal PR or release-promotion review with verified findings, standards citations, JSON and Markdown artifacts.

## References (`references/`)

- `protocol.md`: Rules of engagement, grading criteria, adversarial pass, and severity guidelines.
- `template.md`: Section contract for the rendered review document.
- `output.md`: Schema for the machine-readable `findings.json` artifact.
- `platforms/`: Platform-specific grading packs (`android.md`, `ios.md`, `generic.md`).
- `ci.md`: Pipeline and headless execution reference.

## Helpers (`scripts/`)

- `post_azdo.py`: Helper script to post formatted review comments to Azure DevOps pull requests.
