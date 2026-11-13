---
verified: 2026-11-13
sources: inline
---

# Spec-driven feature work

Follow this path when the task names a spec folder that holds `requirements.md`, `design.md` and `tasks.md`, such as "implement T3 from `docs/specs/<feature>/tasks.md`". The spec is the source of truth. It replaces the feature playbook's intake, discovery and plan steps, and it changes how the tests, review, commit and report steps run. The playbook's other steps run as written.

When the repo has a spec README, usually `docs/specs/README.md`, read it first. Its conventions win over this file.

## Intake

- Read `requirements.md`, `design.md` and `tasks.md` in full. Then read the named task group, its "Done when" checks, the criteria and design sections it lists, and its rows in the traceability table.
- Quote the criterion IDs the task group delivers, such as R3.1 to R3.8. They are the acceptance criteria. Do not fetch criteria from Jira, because in a spec repo the ticket carries none.
- Take the branch name, the base branch, the pull request target and the commit format from `tasks.md` when it names them. Otherwise use the playbook's branch convention.
- Stop and ask when the task group depends on unfinished work, or when a criterion it lists carries `[NEEDS CLARIFICATION]`. Never settle an open question in code.

## Discovery and plan

Skip the playbook's discovery and plan steps, and do not ask for plan approval. `design.md` already names the files, the decisions and the patterns to follow, and `tasks.md` orders the work.

- Read each file the design cites before editing it, and check that its `file:line` references still match. When the code has moved, follow the code and record the drift for the spec change below.
- Search the codebase only for something the design leaves out, and only for that thing.
- When the task changes UI, still capture the touched screens and label them `before`, as the discovery step asks.

## Tests first

- Write the tests the task group lists before the code. Run them, watch them fail for the expected reason, and quote the failing summary.
- Name each test after the behaviour, and put the criterion ID in the test name or in a comment beside it, as `tasks.md` asks.
- Write the code until the tests pass. Then run every "Done when" check the task group lists and quote each command and its result.

## Keep the spec current

- Tick each box in the task group, and each "Done when" check that passed, in the same branch as the code. Under a device check, add the date and what was observed, as the finished task groups do. Leave a box unticked when its check did not run, and say why.
- When the code proves a requirement, the design or a task wrong, change the spec in the same branch and report the change. Keep criterion IDs stable, and strike through a removed criterion instead of renumbering. A branch never leaves the code and the spec disagreeing.

## Review

Brief the kit's reviewer agent with the criterion IDs the task group delivers and the paths of the 3 spec documents, as well as the diff range. Ask it to grade each criterion as met or missing, and to check that any spec change matches the code. Then confirm and fix findings as the playbook's review step says.

## Commit, pull request and Jira

- Use the commit format and the pull request target from `tasks.md`.
- List the criteria the pull request delivers in its description, such as "Delivers R3.1 to R3.8", and name any spec change.
- Leave spec links and criterion IDs out of Jira comments and fields, unless the repo's spec README says otherwise.

## Report

Add these to the playbook's report:

- each criterion delivered, with the test or check that proves it
- the boxes ticked, and any left open with the reason
- each spec change and the code that proved the spec wrong
