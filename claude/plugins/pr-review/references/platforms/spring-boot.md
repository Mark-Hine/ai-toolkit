# Spring Boot platform pack

Grading criteria for reviewing a Spring Boot service change in Java or Kotlin, built with Gradle or Maven. Load this pack when the build applies `org.springframework.boot` and is not an Android build. It supplies the standards vocabulary that findings cite and the recipes that turn a suspicion into evidence. The platform-neutral review rules live in [`../protocol.md`](../protocol.md) §13 to §16 (volatile facts, `Unverified` grading, pragmatism guardrails, main-safety ownership), and their extensions in §17 to §20 (root cause, verification criteria, SHA ancestry, debug-variant exclusion). All of them apply here.

Before grading, record the Spring Boot, Spring Cloud and Java versions in the review's scope block. A version catalog or company BOM may hide them. When it does, read `dependencySubstitution`/`resolutionStrategy` blocks and the managed Tomcat or Jackson version, or run `dependencyInsight`, and mark the result `Unverified: inferred` if it stays indirect. Cite the reference docs for that version line, not the latest.

## Standards-basis block

Paste this into the review's Standards basis section, then append the verification sentence (template.md):

```markdown
Findings are graded against the published Spring, Java and API-security guidance, cited per finding:
**[BOOT-REF]** Spring Boot reference, https://docs.spring.io/spring-boot/ (version-matched) · **[MVC-ERRORS]** Spring MVC exception handling and `ProblemDetail`, https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-exceptionhandler.html · **[DI-CTOR]** https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html · **[OPENFEIGN]** https://docs.spring.io/spring-cloud-openfeign/reference/spring-cloud-openfeign.html · **[ACTUATOR-ENDPOINTS]** https://docs.spring.io/spring-boot/reference/actuator/endpoints.html · **[BOOT-TESTING]** https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html · **[ORACLE-SECCODE]** Secure Coding Guidelines for Java SE · **OWASP ASVS 5.0.0** · **OWASP API Security Top 10 2023** · **RFC 9700** OAuth 2.0 Security BCP · **RFC 7636** PKCE · **RFC 9457** Problem Details.
```

## Architecture and layering

Spring publishes no layering doctrine, so grade against the layering this repo already uses (usually controller, service, facade or client, and model). A change that contradicts that layering is the finding.

- **Controllers stay thin.** A controller binds and validates the request, calls one service method, and maps the result. Business rules, remote calls and token handling inside a controller are a finding. Quote the lines.
- **Constructor injection ([DI-CTOR]).** Spring's rule of thumb is constructors for mandatory dependencies. New `@Autowired` fields in a class that otherwise uses constructor injection (or Lombok `@RequiredArgsConstructor`) are a Nit.
- **Wire models at the edge.** Request and response DTOs, Feign models and persistence entities stay distinct where the repo already separates them. A Feign response type returned straight from a public controller couples two contracts, so flag it when it is new in the delta.
- **Versioned APIs move together.** When the repo keeps parallel `v1`/`v2` controllers, services or clients, a behaviour change to one version needs an explicit decision for the other. Check every sibling of the changed method, including its callers in other services. An unmirrored fix is a Question for the author unless you can prove the sibling is unreachable, for example that no gateway route or client calls it.
- **Configuration binding ([EXTERNAL-CONFIG]).** New settings use `@ConfigurationProperties` or the repo's established pattern, with defaults that are safe in production. A new key needs a value in every environment profile the repo ships, or a default.

## Web contract

- **Binding and transport.** Credentials, tokens, device identifiers and PII travel in the body or a header, never in a query string, because gateway and access logs record the URL (ASVS V14 Data Protection). `@RequestParam` on a `POST` for such a value is a finding.
- **Backward compatibility.** New request fields and parameters are optional, or every caller ships first. Removed or renamed response fields break deployed clients. Check the callers in sibling repos, or raise a Question (generic.md "Contract changes").
- **Validation.** `@Valid` or `@Validated` on request bodies, with constraints on the DTO. A new endpoint that trusts unvalidated input for an identifier, redirect target or amount is Major, and a Blocker once verified on a money or authorisation path (protocol.md §3).
- **Error mapping ([MVC-ERRORS], [RFC9457]).** Failures map through `@ControllerAdvice`/`@ExceptionHandler` to consistent status codes, and `ProblemDetail` where the repo uses it.
  - An upstream 4xx that surfaces as a 500, or a failure that returns 200 with an error body.
  - A new exception type or handler that overlaps an existing handler, where ordering decides which one runs.
  - Messages that echo stack traces, internal hostnames or upstream error bodies to the client.
- **Status codes.** 401 means unauthenticated and 403 means forbidden. OAuth token endpoints return the RFC 6749 error JSON (`invalid_grant`, `invalid_client`) where the client expects it.

## Security against ASVS 5.0.0 and API Top 10 2023

Cite the ASVS 5.0.0 chapter and requirement ID ([ASVS5]) and, for an endpoint, the API Top 10 2023 ID ([API-TOP10-2023]). ASVS chapter numbering changed completely from 4.0.3, so never cite a 4.x ID against 5.0.

| Area | ASVS 5.0.0 · API Top 10 | What to check in the delta |
|---|---|---|
| OAuth and OIDC flows | V10 OAuth and OIDC · API2 | Authorization code with PKCE (S256) where the client is public ([RFC7636]). `code_verifier` checked server-side against the stored challenge. Codes are single-use and short-lived. `state` and `nonce` are bound to the request. `redirect_uri` is matched exactly against a registered value, never by prefix or regex ([RFC9700]). Client authentication for confidential clients. |
| Tokens | V9 Self-contained Tokens · API2 | JWT and JWE algorithms are pinned server-side, never taken from the token header. `aud`, `iss` and `exp` are validated. Keys come from a secret store or KMS, not `application.yml` or the repo. Refresh rotation and revocation behave as documented. |
| Identity-provider calls | V6 Authentication · API2 | Parameters the provider documents as required for a mode are passed on every flow that mode affects, including login, refresh and logout. Cite the provider's own API reference for the requirement. Provider error types map to distinct client errors instead of collapsing into one 401. ID tokens are validated per [OIDC-CORE] where the service consumes them. |
| Authorisation | V8 Authorization · API1, API3, API5 | Every new endpoint enforces who may call it and for which object. Identifiers taken from the path or body are checked against the caller, not trusted. |
| Input | V1 Encoding and Sanitization, V2 Validation and Business Logic · API6 | Injection surfaces such as string-built queries, SpEL, templates, shell and LDAP. Business-flow limits (attempt counters, OTP retries) are enforced server-side. |
| Rate and resource limits | V2 Validation and Business Logic, V6 Authentication · API2, API4 | Login, OTP, password-reset and token endpoints have throttling or lockout, here or at the gateway. Say which. |
| Outbound calls | V1 Encoding and Sanitization (SSRF), V15 Secure Coding and Architecture · API7, API10 | URLs built from caller input (SSRF, confirm the requirement ID per protocol.md §13). Upstream responses are validated before they are trusted. |
| Configuration | V13 Configuration · API8 | Actuator exposure (since Boot 2.5 only `health` is exposed over HTTP by default ([ACTUATOR-ENDPOINTS]), and Boot 2.0 to 2.4 also exposed `info`). Anything more needs authentication. Debug logging, `show-sql`, permissive CORS and stack traces in error responses stay out of production profiles. |
| Logging | V16 Security Logging and Error Handling | No tokens, codes, verifiers, passwords, device secrets or PII in log lines, including Feign `loggerLevel: full` and request-logging filters ([LOGGING-CS]). Log values that come from callers are sanitised against CR/LF injection. |
| Dependencies | V15 Secure Coding and Architecture · API9 | New libraries, and version bumps with their provenance. An API that is deprecated or retired and still routed is an API9 inventory question. |

[ORACLE-SECCODE] backs Java-specific points such as deserialisation, `SecureRandom` against `Random`, and immutable handling of secrets.

## Spring Security configuration

Graded against [SEC-OAUTH2] and the Spring Security reference for the pinned line.

- **Filter chain matchers.** Read every `SecurityFilterChain` bean the delta touches. A new endpoint must fall under a matcher that authenticates it. A broad `permitAll()` pattern, or a matcher order where a general rule shadows a specific one, is Major, and a Blocker once verified to expose an authenticated resource.
- **Method security.** `@PreAuthorize` and `@Secured` do nothing without `@EnableMethodSecurity` (or the older `@EnableGlobalMethodSecurity`). Confirm it is enabled before counting an annotation as a control.
- **CSRF.** Disabling CSRF is correct for a stateless bearer-token API and wrong for any cookie-authenticated endpoint. Check which kind the delta adds.
- **CORS.** `allowCredentials(true)` with a wildcard origin or origin pattern is a finding. Allowed origins come from configuration per environment.

## Persistence and transactions

- **Transaction boundaries.** `@Transactional` on a private method, or called from the same class (self-invocation), has no effect because the proxy is bypassed. Multi-step writes that must succeed together need one transaction around them.
- **Queries.** Lazy associations read in a loop (N+1), unbounded `findAll`, and string-built JPQL or SQL. `spring.jpa.open-in-view` left at its default of `true` keeps sessions open through rendering, which Boot logs a warning about.
- **Migrations.** Flyway or Liquibase changes follow the generic pack's deploy and migration ordering rules.

## Concurrency

This is where the pack expresses protocol.md §16. The class that performs blocking work owns running it on the right executor.

- **Executors.** `@Async` without a configured `TaskExecutor`, unbounded pools, and `CompletableFuture.supplyAsync` without an executor, which falls back to the common pool.
- **Context propagation.** `SecurityContext`, MDC and other `ThreadLocal` state do not follow work onto another thread unless the executor propagates them. A new async path that reads the current user needs this.
- **Reactive code.** Blocking calls (JDBC, `RestTemplate`, `.block()`) inside a WebFlux or Reactor pipeline stall the event loop.
- **Shared state.** Mutable fields on singleton beans (controllers, services) are shared across requests.

## Outbound calls (Feign and HTTP clients)

- **Timeouts ([OPENFEIGN]).** Set `connectTimeout` and `readTimeout` per Feign client or in `default`. `RestTemplate`, `RestClient` and `WebClient` have no default read timeout, so a new one without explicit timeouts can hang a request thread indefinitely. State the effective timeout for the pinned version.
- **Retries.** Spring Cloud OpenFeign creates `Retryer.NEVER_RETRY` by default, which differs from plain Feign. A retry added in the delta must target idempotent calls only. Retrying a token exchange or a one-time code redemption is a Blocker once verified, because the second attempt fails or double-spends.
- **Error decoding.** Without a custom `ErrorDecoder`, every non-2xx becomes a `FeignException` and usually a 500 upstream. A new call path needs a decision about which upstream statuses pass through.
- **Overloads.** Two Feign methods on the same path with different parameters must produce the intended request. Check the query and body the new overload actually sends.

## Tests and build

- **Test scope ([BOOT-TESTING]).** `@WebMvcTest` slices cover binding, validation and error mapping with `MockMvc`. `@SpringBootTest` covers wiring and configuration. A controller test that mocks the service and only asserts the mock was called proves nothing about the contract, so the assertions should cover status, body and headers. Check test annotations against the pinned line, because `@MockBean` is deprecated from Boot 3.4 in favour of `@MockitoBean` and Boot 4 moves `@WebMvcTest` into its own module (verify per protocol.md §13).
- **Tests that cannot fail.** Assertions on a mock's own stubbed return value, `verify` without argument matchers on the changed parameter, tests with no assertions, or `@Disabled` added in the delta. Grade by the risk of the path the test pretends to cover. It is a Blocker only when that path is a protocol.md §3 surface such as auth, money or privacy, and Major otherwise (generic.md "Tests"). A CI step that cannot fail is always a Blocker (protocol.md §3).
- **Auth paths.** New OAuth, token and refresh code needs tests for the failure paths: bad verifier, expired or replayed code, wrong client, and missing optional parameters. Happy-path-only coverage for an auth change is Major.
- **Build files.** Read `build.gradle`/`pom.xml`, version catalogs, lockfiles and `dependencySubstitution` changes. A forced version without a comment is a Question.
- **Version currency.** Check the Boot line against [BOOT-SUPPORT] at review time and record the date (protocol.md §13). Raise it as a finding only when the delta changes the pinned version or deepens reliance on an unsupported line (protocol.md §1). Otherwise record it in the scope block as context.
- **Repo-adopted plugins.** Licence-header, Sonar, JaCoCo, Checkstyle, Spotless or PMD configuration is a citable standard (generic.md). A change that breaks it is a finding even when CI does not run the check.

## Churn and provenance

- **Formatter sweeps.** Reformatting files the change does not otherwise need is graded under protocol.md §7. Quantify it with `git diff -w --stat`. Ask for it to be reverted or split into its own commit when it hides the functional diff, rewrites a file with no functional change, or touches a security-sensitive class. A formatter that damages comments or Javadoc is a Nit defect in its own right.
- **Licence and copyright headers.** When the repo ships a header file and a licence plugin (for example `com.github.hierynomus.license` with `LICENSE_HEADER.txt`), the header is an adopted standard. Removing it from files the delta touches contradicts repo config. When the header asserts third-party copyright or licence terms, removal is also a provenance question for the code owner, so grade it **Q** and ask for the headers to be restored or the decision cited ([LICENSE-PLUGIN]).
- **Unused and dead code.** Removed imports and dead branches are welcome. New commented-out code and unreferenced constants are Nits.

> **PRAGMATISM GUARDRAILS, DO NOT FLAG.** These are legitimate choices that Spring's docs do not rank. Unless the repo has adopted a standard that the change contradicts, do **not** raise findings for:
> - the absence of hexagonal, onion or clean-architecture layers, ports or use-case classes
> - no interface per service or per Feign client
> - Lombok, records, MapStruct or hand-written mappers
> - package names inherited from a vendor or a previous owner
> - Gradle against Maven, Groovy DSL against Kotlin DSL, or a company BOM or version catalog
> - field injection that already exists in files the delta does not touch
> - formatting that the repo's own formatter accepts
>
> Flag *a broken contract, an unenforced security control, a sibling version left inconsistent, or an untested auth path*.

## Recipes

```bash
# Churn first: how much of the delta is whitespace? (protocol.md §7)
git diff --stat MERGE_BASE SOURCE_HEAD
git diff -w --stat MERGE_BASE SOURCE_HEAD

# Sibling versions of a changed method (v1/v2 controllers, services, clients)
git grep -n '<methodName>' SOURCE_HEAD -- 'src/main'

# Who calls this endpoint? Search sibling repos and gateway config, not just this one
git grep -n '/v2/<resource>/<path>' SOURCE_HEAD

# Boot, Cloud and Java versions when a catalog or BOM hides them ([GRADLE-INSIGHT])
./gradlew dependencyInsight --dependency spring-boot --configuration runtimeClasspath
./gradlew dependencyInsight --dependency tomcat-embed-core --configuration runtimeClasspath

# Headers removed by the delta
git diff MERGE_BASE SOURCE_HEAD | grep -c '^-.*Copyright'

# Settle a claim by running it, in a scratch worktree at SOURCE_HEAD
./gradlew test --tests '<TestClass>'
./gradlew licenseMain   # when the repo applies the licence plugin
```

## Source registry (canonical URLs for Refs lines)

| Key | Source |
|---|---|
| [BOOT-REF] | https://docs.spring.io/spring-boot/ (select the version line the repo pins) |
| [BOOT-SUPPORT] | https://spring.io/projects/spring-boot#support (OSS and commercial support end dates per line) |
| [MVC-ERRORS] | https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-exceptionhandler.html (`@ExceptionHandler`, `@ControllerAdvice`, `ProblemDetail`) |
| [RFC9457] | https://www.rfc-editor.org/rfc/rfc9457 (Problem Details for HTTP APIs, obsoletes RFC 7807) |
| [DI-CTOR] | https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html ("use constructors for mandatory dependencies") |
| [SEC-OAUTH2] | https://docs.spring.io/spring-security/reference/servlet/oauth2/index.html |
| [OPENFEIGN] | https://docs.spring.io/spring-cloud-openfeign/reference/spring-cloud-openfeign.html (timeouts, `Retryer.NEVER_RETRY` default, `ErrorDecoder`) |
| [ACTUATOR-ENDPOINTS] | https://docs.spring.io/spring-boot/reference/actuator/endpoints.html ("only the health endpoint is exposed over HTTP") |
| [EXTERNAL-CONFIG] | https://docs.spring.io/spring-boot/reference/features/external-config.html |
| [BOOT-TESTING] | https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html (`@WebMvcTest`, `@SpringBootTest`, MockMvc) |
| [ORACLE-SECCODE] | https://www.oracle.com/java/technologies/javase/seccodeguide.html |
| [ASVS5] | https://github.com/OWASP/ASVS/tree/v5.0.0/5.0 (OWASP ASVS 5.0.0, project page https://owasp.org/projects/asvs) |
| [API-TOP10-2023] | https://api-security.owasp.org/editions/2023/en/0x11-t10 |
| [LOGGING-CS] | https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html |
| [RFC9700] | https://www.rfc-editor.org/rfc/rfc9700 (OAuth 2.0 Security BCP, BCP 240) |
| [RFC7636] | https://www.rfc-editor.org/rfc/rfc7636 (PKCE) |
| [OIDC-CORE] | https://openid.net/specs/openid-connect-core-1_0.html (errata set 2) |
| [GRADLE-INSIGHT] | https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html |
| [LICENSE-PLUGIN] | https://github.com/hierynomus/license-gradle-plugin (`licenseMain` checks headers, `licenseFormatMain` applies them) |

<!-- Source links. Keep in sync with the table above (primary URL per key) so [KEY] references render as links wherever this pack's content is pasted. -->
[BOOT-REF]: https://docs.spring.io/spring-boot/
[BOOT-SUPPORT]: https://spring.io/projects/spring-boot#support
[MVC-ERRORS]: https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-exceptionhandler.html
[RFC9457]: https://www.rfc-editor.org/rfc/rfc9457
[DI-CTOR]: https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html
[SEC-OAUTH2]: https://docs.spring.io/spring-security/reference/servlet/oauth2/index.html
[OPENFEIGN]: https://docs.spring.io/spring-cloud-openfeign/reference/spring-cloud-openfeign.html
[ACTUATOR-ENDPOINTS]: https://docs.spring.io/spring-boot/reference/actuator/endpoints.html
[EXTERNAL-CONFIG]: https://docs.spring.io/spring-boot/reference/features/external-config.html
[BOOT-TESTING]: https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html
[ORACLE-SECCODE]: https://www.oracle.com/java/technologies/javase/seccodeguide.html
[ASVS5]: https://github.com/OWASP/ASVS/tree/v5.0.0/5.0
[API-TOP10-2023]: https://api-security.owasp.org/editions/2023/en/0x11-t10
[LOGGING-CS]: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
[RFC9700]: https://www.rfc-editor.org/rfc/rfc9700
[RFC7636]: https://www.rfc-editor.org/rfc/rfc7636
[OIDC-CORE]: https://openid.net/specs/openid-connect-core-1_0.html
[GRADLE-INSIGHT]: https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html
[LICENSE-PLUGIN]: https://github.com/hierynomus/license-gradle-plugin
