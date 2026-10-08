# pr-review

Formal pull request and release promotion review plugin for Google Antigravity.

Produces verified JSON (`findings.json`) and Markdown review deliverables citing published standards, grading findings (Blocker, Question, Major, Nit), scoping approvals, and verifying environment promotions.

## Skill

- `/pr-review`: Write a formal PR or release-promotion review with verified findings, standards citations, JSON and Markdown artifacts.

## References (`references/`)

- `protocol.md`: Rules of engagement, grading criteria, adversarial pass, and severity guidelines.
- `template.md`: Section contract for the rendered review document.
- `output.md`: Schema for the machine-readable `findings.json` artifact.
- `platforms/`: Platform-specific grading packs (`android.md`, `ios.md`, `spring-boot.md`, `react-nextjs.md`, `generic.md`).
- `ci.md`: Pipeline and headless execution reference, with Azure DevOps and GitHub Actions examples.
- `posting.md`: Posting a review from a local session to Azure DevOps or GitHub.
- `pci-dss.md`: PCI DSS v4.0.1 orientation map, loaded when a change touches card data.

## Helpers (`scripts/`)

- `post_review.py`: Posts `findings.json` to an Azure DevOps or GitHub pull request as anchored threads, one summary comment and an optional vote.
- `post_azdo.py`: Alias for `post_review.py --host azure`.
- `check_ancestry.py`: Checks that every commit a review cites is an ancestor of the ref it is published against (protocol §19).
