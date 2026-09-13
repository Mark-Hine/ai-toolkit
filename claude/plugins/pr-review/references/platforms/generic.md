# Platform pack — generic

Load this pack when the repo is neither Android nor iOS. There is no single authority to cite for
"software in general", so the grading posture shifts: instead of measuring the change against an
external doctrine, measure it against **the standards the project has already adopted** and against
the language/framework's own official documentation. A finding that says "this contradicts the
convention used in the other 40 files" is stronger than one that cites a blog post.

The platform-neutral review rules — volatile facts, `Unverified` grading, pragmatism guardrails,
main-safety ownership — live in [`../protocol.md`](../protocol.md) §13–§16, and their extensions —
root cause not symptom, verification criteria, SHA ancestry, debug-variant exclusion — in §17–§20.

> **PRAGMATISM GUARDRAILS — DO NOT FLAG:** with no ecosystem doctrine to anchor against, the risk
> here is grading the repo against your own preferences. Unless the project has adopted a standard
> that the change contradicts, do **not** raise findings for:
> - the choice of architectural pattern, folder layout, or module boundaries;
> - the absence of a DI container, an interface per class, a use-case layer, or a repository
>   abstraction;
> - ORM vs query builder vs raw SQL; monorepo vs polyrepo; the test framework or assertion style;
> - formatting and naming that the project's own formatter and linter accept;
> - the language or framework itself, or its version, absent a stated support or security reason.
>
> Flag *contradiction with the standard this repo has adopted*, not divergence from the one you
> would have picked. If the repo has adopted nothing on the point, the reviewable question is
> whether the change is consistent with the rest of the tree (protocol.md §15).

## Establishing the standards basis (do this first)

Before reviewing, spend a few minutes finding what this repo already commits to, and cite *that*:

- **Linters and formatters** — config files (`.eslintrc`, `ruff.toml`, `.rubocop.yml`, `detekt.yml`,
  `.editorconfig`, compiler strictness flags). A rule the project has enabled is a citable standard;
  a config the tree visibly violates, with no CI enforcing it, is itself a finding.
- **CI configuration** — what actually gates a merge. A test step that cannot fail (`|| true`,
  `continue-on-error`, a task name that matches nothing) is a blocker-class finding regardless of
  language, because it silently certifies everything else.
- **Contributing/architecture docs** — `CONTRIBUTING.md`, ADRs, `docs/`. Written team decisions are
  the strongest possible citation.
- **The language/framework's official guidance** — the canonical docs site for the stack in play.
  Prefer it over third-party opinion, and verify anything volatile at review time (protocol.md §13).
- **Security** — OWASP ASVS for application-security requirements and the OWASP Top 10 for web
  risks; for an API, add the OWASP API Security Top 10. Cite the specific control, not "OWASP".

Record whatever you settle on in the review's Standards basis section so every finding's citation
resolves to something the reader can open.

### Which authority to cite, by stack

The repo's own adopted config still outranks everything below — this table is what to reach for
*after* that, so a finding cites a canonical source rather than a blog post. Verify anything
volatile at review time (protocol.md §13); prefer the version of the doc matching the version the
repo pins.

| Stack in play | Cite |
|---|---|
| JavaScript / TypeScript | MDN for language and web APIs; the runtime's own docs (Node/Deno/Bun); the framework's official docs; the TS handbook for type questions |
| Python | the relevant PEP (PEP 8/484/604…) plus the project's `ruff`/`mypy`/`pyproject` config; library docs for API use |
| Go | Effective Go, the Go style guide, and `go vet`/staticcheck rule IDs |
| JVM (Java / Kotlin / Spring) | the framework reference docs; Kotlin coding conventions; the JDK API docs for concurrency and time |
| .NET / C# | Microsoft Learn framework design guidelines and the .NET API docs |
| Ruby / Rails | the Rails guides and the project's `.rubocop.yml` |
| PHP / Laravel | PSR standards and the framework's own docs |
| Rust | the Rust API guidelines, the book, and `clippy` lint names |
| SQL and schema migrations | the engine's own documentation for locking, transactional DDL, and index-build behaviour |
| Terraform / IaC | the provider's resource docs plus the relevant CIS benchmark |
| Containers / Kubernetes | upstream Docker/Kubernetes docs plus the CIS benchmark for the runtime |
| CI / build pipelines | the CI product's own docs for the step semantics you are relying on |

Where the finding is a security control rather than a style or API question, cite the OWASP control
above instead — ASVS for application requirements, the API Top 10 for endpoints — naming the
specific control, not "OWASP".

## What to grade

These are the failure classes worth hunting in almost any change. They are lenses, not a checklist —
depth belongs where the risk is.

**Correctness at boundaries.** Error paths that swallow failures (empty `catch`, ignored return
values, a failure branch that routes to a success screen); results collapsed into sentinels (`""`,
`0`, `null`) that the caller must reinterpret; off-by-one and empty-collection edges in new parsing
or pagination; time zones and locale in date/money formatting.

**Contract changes.** Any change to a wire format, database schema, public API, queue message, or
config key: is the other side deployed and compatible, and is the change backward-compatible for
in-flight clients and rows? Renamed or retyped fields, newly required fields, and changed
enum/status vocabularies are the classic breakages, and they are questions for the author (Q), not
assertions, unless you can verify the far side yourself.

**Deploy and migration ordering.** A change can be backward-compatible and still break, because
compatibility is a property of the *sequence*, not of the endpoint. For any schema or wire change,
ask: is it staged expand-then-contract — add the new field or column, backfill, switch readers,
and only drop the old one in a later release — or does one deploy do all of it at once? What
happens to rows and messages written by the old code while the rollout is in flight, and to rows
written by the new code if it is rolled back? Is the migration reversible, and is there a down
path that doesn't lose data? Where a service and its consumers both change, which side must ship
first, and does anything enforce that order? For a live table, will the migration hold a lock or
rewrite the table — the engine's own docs (see the table above) are the citation, not folklore.
Same grading rule as the rest of this lens: **Q** for the author unless you can verify the far
side or the deploy mechanism yourself.

**State and data flow.** One owner per piece of state; no hidden writes behind read-shaped names (a
`get*` that mutates a cache); persisted flags with several writers and no clear lifetime, especially
where a stale value changes a later decision; caches whose invalidation is spread across callers.

**Security and privacy.** Secrets or credentials in code, config, or logs; PII in URLs, query
strings, or log lines (the connection may be encrypted; the server's access log is not);
authentication and authorisation checks enforced server-side, not merely in the client; injection
surfaces (string-built SQL, shell, template); unsafe deserialisation; new dependencies and their
provenance.

**Concurrency and resources.** Unbounded pools and unclosed resources; work launched without a
cancellation story; shared mutable state without synchronisation; blocking calls on latency-critical
paths. Note that swallowing a cancellation signal and reporting it as an error is a common, subtle
regression.

**Tests.** Does the riskiest code in the change have any? Tests that assert defaults rather than the
scenario they name, tests with deleted assertions, and test files that no longer compile are worse
than absent tests, because they read as coverage.

**Public interface quality.** For any shared component, library function, or endpoint the change
adds or alters: does the name mean what it does, can a caller misuse it accidentally, and is the
dangerous option the easy one? A callback wired to the wrong parameter, or a flag whose default is
the unsafe case, is a defect in the interface, not just in the caller.

**Dead and half-wired code.** State that is written but never read, actions with no handler, routes
with no destination, feature flags with no reader. Each compiles and looks intentional, which is
what makes it expensive later.

## Source registry

Fill this in per review with what you actually cited — the project's own configs and docs first,
then the canonical references for the stack. A few that apply broadly:

| Key | Source |
|---|---|
| [ASVS] | https://owasp.org/www-project-application-security-verification-standard/ |
| [TOP10] | https://owasp.org/www-project-top-ten/ |
| [API-TOP10] | https://owasp.org/www-project-api-security/ |
| [CHEATSHEETS] | https://cheatsheetseries.owasp.org/ |
| [SEMVER] | https://semver.org/ |
| [CIS] | https://www.cisecurity.org/cis-benchmarks |

<!-- Source links -->
[CIS]: https://www.cisecurity.org/cis-benchmarks
[API-TOP10]: https://owasp.org/www-project-api-security/
[ASVS]: https://owasp.org/www-project-application-security-verification-standard/
[CHEATSHEETS]: https://cheatsheetseries.owasp.org/
[SEMVER]: https://semver.org/
[TOP10]: https://owasp.org/www-project-top-ten/
