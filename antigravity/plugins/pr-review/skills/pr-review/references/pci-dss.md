---
verified: 2026-09-16
sources:
  - https://www.pcisecuritystandards.org/document_library/
---

# PCI DSS orientation map

Load this file when a change displays, receives, stores, logs or transmits cardholder data (CHD,
the PAN at minimum) or sensitive authentication data (SAD, which is the card verification code, the
PIN or the PIN block). PCI DSS v4.0.1 is not a mobile standard, so MASVS stays the grading
framework. A finding that breaks an obligation cites the PCI DSS requirement beside the MASVS
control, so the review uses the language the client's QSA and compliance team already use.

Whether the app is in scope, as part of the cardholder data environment (CDE) or connected to it,
is a compliance question. Raise it as a Q for the author rather than deciding it in the review. The
requirement numbers label a finding. They are not a scoping verdict.

Read the standard at review time (protocol.md §13). The numbers below were checked against the
v4.0.1 PDF on 2026-09-16 and are an orientation aid, not a substitute for the requirement text.
Cite a requirement as `PCI DSS 4.0.1 Req 3.4.1` with [PCI-DSS].

| Requirement | What it says (paraphrase) | What to look for in a change |
|---|---|---|
| 3.3.1 · 3.3.1.2 · 3.3.1.3 | SAD is not stored after authorization, even if encrypted. The card verification code, PIN and PIN block are not stored after authorization | CVV or PIN written to a database, preferences, a log, a crash report, an HTTP-inspector store or a screenshot cache |
| 3.3.3 | Issuers and companies that support issuing services may store SAD only for a legitimate, documented issuing business need, and must secure it | An issuer app that shows a CVV may display it, but must not keep it on the device |
| 3.4.1 | PAN is masked when displayed, with the BIN and last four at most, unless there is a legitimate business need to see more | Full PAN on a list screen or in a recents thumbnail, or an endpoint returning the full PAN to a screen that shows only the last four |
| 3.5.1 | PAN is rendered unreadable anywhere it is stored, by hashing, truncation, tokenisation or strong encryption | PAN in an unencrypted local store, cache or log |
| 4.2.1 | Strong cryptography protects PAN in transit over open public networks, and only trusted keys and certificates are accepted | TLS configuration, cleartext permitted, trust-all managers and pinning posture, which pair with NETWORK-1 and NETWORK-2 |
| 6.2.1 · 6.3.1 · 6.3.2 | Bespoke software is developed securely, vulnerabilities are identified and managed, and an inventory of bespoke and third-party components is kept | Dependency scanning in CI and an SBOM or lockfile, which pair with CODE-3 |
| 8.4.2 | MFA for all non-console access into the CDE | Rarely the app's obligation. It matters where the app is an admin channel |
| 10.2.1 · 10.3.1 | Audit logs are enabled for all system components and cardholder data, and read access is limited to a job-related need | Client-side logging that carries PAN or SAD, and where those logs go |
| 11.4.2 · 11.4.3 · 11.4.4 | Internal and external penetration testing follows a defined method at least every 12 months **and after any significant infrastructure or application upgrade or change**, and exploitable findings are corrected and re-tested | A change that rewrites a card flow is a significant change. Ask whether the post-change penetration test is planned |
| 12.8.1 · 12.8.2 | A list of the third-party service providers that account data is shared with, and written agreements with each | A new card-data SDK or host the change starts sending data to |

Mobile-specific PCI SSC standards (MPoC, and the sunsetting SPoC and CPoC) govern payment acceptance
on commercial off-the-shelf devices. They do not apply to an issuer's card-servicing app, so do not
cite them for one.

<!-- Source links -->
[PCI-DSS]: https://www.pcisecuritystandards.org/document_library/
