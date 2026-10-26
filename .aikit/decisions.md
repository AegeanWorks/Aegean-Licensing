# Decisions

Why this project is built the way it is, oldest first. One entry per decision that changes a
contract, a dependency, a data format or the architecture; IDs are consecutive and never reused.

<!-- Entry format:
### ADR-NNN: <decision in one line>
- **Date**: YYYY-MM-DD
- **Status**: Accepted
- **Context**: <what forced the decision>
- **Decision**: <what was decided>
- **Consequences**: <what follows, including what it costs>
-->


### ADR-001: Pure Standard Library Dual-Licensing Framework & Cryptographic Tooling
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: AegeanWorks software is published under GNU AGPL-3.0 for open collaboration, but commercial entities require closed-source operations and copyleft waivers without enterprise bureaucracy (MSAs, SLAs, W-9s). Additionally, repository audits across the portfolio require clear delineation between code and domain assets, inbound contributor rights, and automated verification.
- **Decision**: Establish the Aegean-E Commercial License (AECL-1.0) with binding standard terms (Exhibit A) and pure standard-library tooling (aegean_licensing) providing: (1) canonical SHA-256 certificate hashing and optional HMAC-SHA256 signatures, (2) tamper detection and expiration/scope verification, (3) repository compliance auditing, and (4) standard licensing templates.
- **Consequences**: Zero external dependencies required. Certificates are portable, tamper-evident, and auditable in ~2ms. License grants are strictly AS-IS pure copyright waivers without technical support obligations.


### ADR-002: Draft Personal Use License (AL-PU 1.0) and Backward Compatibility Policy
- **Date**: 2026-10-25
- **Status**: Proposed
- **Context**: AegeanWorks is evaluating a transition toward a custom source-available model where personal non-commercial use is free under the Aegean Licensing Personal Use License (AL-PU 1.0), while commercial and organizational use requires prior written authorization. Crucially, earlier releases (e.g., under AGPL-3.0) and third-party contributions cannot be retroactively modified without legal authority.
- **Decision**: Draft AL-PU-1.0-DRAFT.md, COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md, and establish BACKWARD-COMPATIBILITY-DRAFT.md affirming that: (1) existing AGPL-3.0 grants are preserved and cannot be retroactively revoked, (2) older versions reissued by AegeanWorks adopt new terms only when authorized, and (3) a clear migration and legal checklist precedes any operative transition.
- **Consequences**: Provides transparency for future licensing evolution while legally protecting existing community users and open source integrity.


### ADR-003: Optimization of AL-PU 1.0 Draft for Maximum Commercial Conversion & Personal Protection
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The initial AL-PU v0.2 draft had commercial leakage points (unclear startup transitions, freelancer ambiguity, and contributor IP bottlenecks) while risking chilling individual students. Additionally, it lacked a structured commercial agreement draft and a non-litigious conversion ramp for unauthorized commercial users.
- **Decision**: Update AL-PU-1.0-DRAFT.md (to v0.3) and COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md to: (1) carve out free self-study for enrolled students, (2) define explicit commercialization triggers (first revenue, third-party deployment, client delivery), (3) mandate commercial licensing for billable freelance/consulting work, (4) bind public PRs to the inbound CLA, (5) introduce a Commercial Cure Ramp in Section 9.1 to monetize infringers directly, and (6) establish a 3-tier commercial framework backed by cryptographic License Grant Certificates.
- **Consequences**: Protects grassroots student and developer adoption while maximizing commercial conversion and revenue capture from startups, consulting firms, and enterprise cloud operators.


### ADR-004: Configurable License Types, Multi-Model Auditor and Expanded Template Suite
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The aegean-license CLI was hardcoded to AECL-1.0 and its template generator only produced basic AGPL boilerplate. Furthermore, the repository auditor rejected any repository not starting with AGPL-3.0, preventing future verification of projects adopting AL-PU 1.0 or checking for required policies.
- **Decision**: (1) Add --type argument to issue enabling tiered certificates (e.g. ACLA-1.0-Tier1, ACLA-1.0-Enterprise), (2) expand templates.py and template command with al-pu, acla, cla, asset-policy, and backward-compat, and (3) update auditor.py to recognize both AGPL-3.0 and AL-PU-1.0 bases, with an optional --check-policies verification flag.
- **Consequences**: Provides end-to-end tooling for both the present dual-licensing setup and future custom license transitions with 36 passing unit tests.


### ADR-005: Automated Certificate Webhook, CLA Workflow and Portfolio Migration Plan
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: Commercial licensing still required manual certificate issuance, contributor IP was verified ad hoc, and the portfolio had no documented project-by-project transition path from AGPL-3.0 to AL-PU 1.0 / ACLA-1.0.
- **Decision**: (1) Add a pure-standard-library serve subcommand backed by aegean_licensing/webhook.py; it authenticates with a constant-time Bearer-token check, caps request bodies at 1 MiB, signs only with the server-configured key, and archives certificates through the existing atomic issuer. (2) Add a GitHub Actions workflow that requires an /agree-cla comment from external contributors. (3) Add policies/PORTFOLIO-MIGRATION-PLAN.md plus template migration and template cla-action generators.
- **Consequences**: Certificates can be issued automatically after payment without exposing signing material to callers. The workflow adds no runtime dependency. The migration plan is advisory until each project's release gate and legal review are complete.


### ADR-006: Fail-Closed Webhook Contract and Idempotent Certificate Issuance
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The first webhook implementation was fail-open: without --token any client that could reach the port could mint a perpetual, portfolio-wide certificate. It also trusted a client-supplied signing key (now ignored), accepted arbitrary field types, leaked exception text, issued duplicate certificates on payment retries, and ran single-threaded without a socket timeout.
- **Decision**: (1) Refuse to bind a non-loopback host without a Bearer token; (2) derive cert_id as uuid5 of an Idempotency-Key, replay the stored certificate on an identical retry, and return 409 on conflicting reuse; (3) validate every field (strings, project list, ISO expires_at, mutually exclusive perpetual/term-limited) before issuance; (4) serve on a threaded HTTP server with a 30-second request timeout and generic error bodies; (5) enforce the perpetual/expiry invariant in both issue_certificate and verify_certificate; (6) make the CLA workflow re-run on labels so a signed PR becomes green, and correct the migration plan's draft status and file references.
- **Consequences**: Retries are safe, anonymous minting requires an explicit loopback bind, and malformed certificates are rejected at verification rather than trusted. Unsigned issuance is still possible on loopback and is warned about at startup; a deployment without --key gets tamper-evident but not authenticating certificates. HTTP/1.0 responses remain plain text over the network, so TLS termination stays the operator's responsibility. A payment provider's own webhook signature is still not verified; deployments must place a verifying proxy or gateway in front of /issue.


### ADR-007: Rate Limiting, Direct TLS, Durable CLA Register, and Payment-Agnostic Issuance
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: After the webhook hardening review, three gaps remained: any authenticated or loopback caller could loop /issue without limit, the server spoke plain HTTP only, and CLA acceptance lived solely in a PR comment that a contributor could edit or delete. AegeanWorks also decided to accept wallet payments instead of Stripe, so certificate issuance must be triggered by an external payment watcher rather than a provider SDK.
- **Decision**: (1) Add aegean_licensing/ratelimit.py, a lock-protected token bucket with a bounded client table and injected clock, applied to POST /issue only; (2) add ssl-based TLS with mandatory certificate/key pairing and TLS 1.2 minimum; (3) make .github/cla-signatures.json the durable acceptance register, written by the workflow with conflict retries and consulted before comments; (4) keep the server payment-agnostic and define the wallet watcher contract: the watcher confirms the transfer to the operator's address, then calls /issue with a Bearer token and an Idempotency-Key derived from the transaction ID; (5) bundle licenses/, policies/, and the CLA workflow into wheels via setup.py and aegean_licensing/bundler.py, declare aegean_licensing as the only package, adopt PEP 639 license metadata (setuptools>=77), and ship the same documents in sdists through MANIFEST.in.
- **Consequences**: Runaway callers are throttled per IP, transport security no longer depends on a proxy, and CLA acceptance survives comment deletion. The wallet address, price list, and watcher remain operator configuration and are deliberately absent from the repository; the server still trusts its Bearer-token holder, so the watcher must stay on loopback or a private network.

### ADR-008: Auditable CLA Register, Trusted-Proxy Keys, Safe Replays, and Escaped Certificate Text
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The second review left five concrete weaknesses: CLA acceptance was self-asserted by comment with no evidence or revocation path, throttling collapsed to one bucket behind a proxy, replay returned an unsigned archived certificate even when a signing key was configured, idempotency ignored notes, and certificate text could inject Markdown or carry terminal escape characters. None of these depend on the still-pending wallet address.
- **Decision**: (1) Version the CLA register to 2, record the agreeing comment URL as evidence, and honour a maintainer-owned revoked array before any acceptance check; (2) add --trusted-proxy so the limiter reads the first valid X-Forwarded-For hop only from configured proxies; (3) on replay, re-sign and atomically re-persist an archived certificate when its signature does not match the current server key, and include notes in the idempotency identity; (4) validate every certificate field against control and non-printable Unicode and escape Markdown when rendering; (5) add a CI workflow that runs the suite on Python 3.10-3.13 and verifies wheel contents.
- **Consequences**: CLA records are auditable and revocable, proxy deployments get per-client buckets without trusting spoofed headers, replays always return a certificate verifiable with the configured key, and licensee text cannot alter the rendered document. Revocation remains a repository-owner action through the JSON file rather than an in-app control, and the watcher/payment layer still awaits the operator's wallet address and order model.

### ADR-009: Internal Wallet Orders, Confirmation-Based Settlement, and Versioned Payment State
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: Certificate issuance could be automated over HTTP, but nothing connected a real payment to an issuance. The operator pays in wallet and will supply the wallet and address at runtime, so the tool must attribute an incoming transfer to one buyer without a payment provider and without asking the buyer to report a transaction id.
- **Decision**: (1) Split the flow into five single-role modules: storage (atomic JSON), pricing (versioned tier list and piconero conversion), orders (order records and the versioned order store), monero (wallet RPC client and transfer parsing), and payments (the watcher). (2) Reserve a fresh payment address per order via make_integrated_address, so the payment reference identifies the order. (3) Treat the wallet as the source of truth: sum *confirmed* transfers per payment reference on every poll, never reduce a recorded total, mark underpaid below the price, expired after the TTL, and issue once. (4) Derive the certificate id from the order id (uuid5) so issuance is stable across restarts. (5) Version both the price list and orders.json; a loader refuses an unknown version without modifying the file.
- **Consequences**: A paid order produces a verifiable certificate with the transaction id in its notes, and the flow needs no HTTP endpoint, no proprietary provider, and no daemon in tests. The operator must run wallet RPC and keep the state directory private; the price list must be edited by the operator because prices and the wallet remain deployment configuration. Underpayment requires a manual follow-up in this version, since no automatic refund or partial-issuance policy exists.

### ADR-010: Advisory State Locks, Per-Order Fault Isolation, and Operator Settlement Commands
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The internal settlement flow worked for the happy path but three operational holes remained: two watchers could settle the same state directory, a single failed issuance aborted the whole pass and left paid orders stuck, and there was no way to close an abandoned order or to record a settlement that happened outside the watcher (another rail, a manual decision, or a recovered payment).
- **Decision**: (1) Add `state_lock` to `storage.py`: an `O_CREAT|O_EXCL` lock file with a bounded wait, a 30-second stale limit, and guaranteed removal, and take `orders.json.lock` around every read-modify-write in `OrderStore`. (2) Have `payments watch` hold `.watch.lock` for its lifetime and refuse a second watcher. (3) Move issuance into `payments.issue_order`, which converts a failure into a `PaymentEvent` with an error instead of raising, leaving the order `paid` for the next pass. (4) Add `payments cancel`, which closes pending, underpaid, or expired orders, and `payments grant`/`payments issue` for manual settlement and retry.
- **Consequences**: One watcher per state directory, no lost order updates, no pass aborted by one bad order, and an explicit path for orders that will never pay. Cancellation is terminal and audited through `cancel_reason`; a cancelled order cannot be reopened, so a buyer who pays late needs a new order or a manual `grant` on a fresh one. Lock files are ordinary files, so a stale lock older than 30 seconds is reclaimed automatically; a live process holding the lock for more than 30 seconds between writes would have it stolen, which no current command does.

### ADR-011: Licensing and Payment Are Arranged Privately by Email
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The public documents began describing a specific crypto rail, prices, and direct payment steps. That is operationally and legally wrong for this business: terms, fees, and payment method vary per order, and publishing a rail turns the repository into a sales channel it is not meant to be.
- **Decision**: All commercial documents (`COMMERCIAL.md`, `licenses/AECL-1.0.md`, `licenses/COMMERCIAL_FAQ.md`, the Order Form) describe licensing as an email conversation with `aegean-licensing@proton.me`; fees and payment method are recorded in the Order Form, and no prices, addresses, or payment steps are published in the repository. The settlement modules remain internal operator tooling and are not part of the customer-facing process; their README section is removed and the example price list is deleted.
- **Consequences**: The public repository contains no offer, price, or payment instructions. A buyer must contact the licensor, and the certificate is issued after written confirmation of the agreed payment. The internal tooling can change or be removed without affecting any public commitment.

### ADR-012: Aegean License 1.0, Aegean Commercial License 1.0 and a Restricted Tier; No AGPL
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The owner wants AegeanWorks software free for personal use, paid for commercial use, and able to stop free distribution of a project that becomes too valuable. The repository still offered an AGPL-3.0 track (root LICENSE, templates, auditor, pyproject), but AGPL-3.0 lets anyone use the software commercially for free, and the owner asked for no AGPL. The owner also asked to rename the licenses to "Aegean" and to strengthen them using established source-available licenses as references.
- **Decision**:
  1. `licenses/AL-PU-1.0-DRAFT.md` becomes `licenses/AL-1.0.md`, the Aegean License 1.0 (`LicenseRef-AL-1.0`), and the root `LICENSE` is a verbatim copy. `licenses/AECL-1.0.md` becomes `licenses/ACL-1.0.md`, the Aegean Commercial License 1.0; `terms.json`, certificates, the CLI and the webhook default to `ACL-1.0`. No certificate was ever issued under `AECL-1.0`, so no alias is kept.
  2. Clauses adopted, with their source: terms are conditions as well as obligations (PolyForm); "Your Company" and "Control" definitions (PolyForm, Elastic License 2.0); patent license with patent-defense termination (PolyForm); a `Required Notice:` line and marking of modified copies (PolyForm, Elastic); one 30-day cure, then permanent termination of every Version (Elastic, Business Source License 1.1); each Version licensed separately (BSL 1.1); no circumvention of license checks (Elastic); no AI training (AIRCL); preserved fair use; severability with an explicit fallback for the AI clause; governing law Türkiye with Istanbul courts, matching ACL-1.0. ACL-1.0 also gains no circumvention, no AI training, no hosted resale and a restricted-version rule, each unless the certificate's scope allows it. Charities and schools stay outside free use, as the owner asked for personal use only.
  3. `licenses/RESTRICTED-NOTICE.md` is the All Rights Reserved notice for the restricted tier, filled by `templates.get_restricted_notice(project, since, commit)`; AIKit's `aikit license <name> --restrict` writes it.
  4. Templates, the auditor and `pyproject.toml` drop the AGPL track: the auditor fails an AGPL LICENSE or an AGPL `pyproject.toml`, accepts AL-1.0 (warning when its `Required Notice:` line is missing) and accepts the restricted notice without a COMMERCIAL.md. The CLA drops its open-source commitment and grants relicensing and patent rights; no contributor had signed it.
- **Consequences**: Commercial users need ACL-1.0. Releases already made under AGPL-3.0 (AIKit, Chronos, this repository's earlier versions) keep AGPL-3.0, which every document now says. The AI-training clause's enforceability is unsettled; the other terms survive without it. The texts have not had legal review.

### ADR-013: Public Certificate Register, Frozen Agreements and Removal of the Payment and Server Code
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: Certificates are signed with HMAC-SHA256, a symmetric scheme, but ACL-1.0 Section 6 told third parties to verify with Licensor's "published verification key": publishing that key would let anyone forge a certificate, and not publishing it left no third-party verification. Certificates cite the SHA-256 of the agreement text, so any later edit of an issued agreement would invalidate every certificate citing it. The never-committed Monero settlement stack (`monero.py`, `orders.py`, `payments.py`, `pricing.py`) and the HTTP issuance server (`webhook.py`, `ratelimit.py`, `serve`) automated a sales channel ADR-011 had replaced with private email arrangements, issued on payment without the vetting ACL-1.0 Section 4.5 reserves, and kept the signing key on a network-facing process. A review of the texts also found that a licensee terminated for breach kept its deployed versions forever.
- **Decision**:
  1. Add `aegean_licensing/register.py` and the committed `licenses/issued.json`: each issued certificate's id, digest, license type, issue date, status and revocation date and reason, never licensee data. `issue --register` records, `revoke` marks revoked, and `verify --register` returns `UNREGISTERED` or `REVOKED`; a registered certificate verifies as `VALID` without the key. Writes are atomic under the storage advisory lock.
  2. `terms.json` pins the sha256 of ACL-1.0; `license_terms.terms_digest` refuses an agreement whose text no longer matches, so issuance stops and verification reports `INVALID_FORMAT` until the changed terms are published as a new version. ACL-1.0 Section 6.6 states the rule.
  3. Delete the payment stack, the issuance server, the rate limiter, the `serve` and `payments` commands and their tests (about 1,570 lines of code and 1,440 of tests). `issue`, `verify`, `revoke`, `audit` and `template` remain.
  4. Add `--key-file` to `issue` and `verify`, mutually exclusive with `--key`.
  5. AL-1.0: own-work clause (5.2), Version license identified by its `LICENSE` file (10.4), how breach notice is given (11.6), survival (11.7), export compliance. ACL-1.0: termination for breach ends all rights including deployed versions and revokes the certificate in the register (5.3), annual compliance certification (6.5), frozen text (6.6), register-based verification (6.1 to 6.3), AI-coding-assistant carve-out, and AI-training and hosted-resale exceptions only where the certificate expressly allows them, since one certificate carries one scope. `ASSET_POLICY.md` moves documentation from CC-BY-4.0 to AL-1.0; documentation already released under CC-BY-4.0 keeps it.
- **Consequences**: Third parties can verify and see revocations without any secret. The register reveals how many certificates exist and when they were issued, never to whom. A wheel bundles a snapshot of the register that goes stale; verifiers should use the repository copy. Editing ACL-1.0 now fails the test suite. AL-1.0 has no pinned digest because no certificate cites it.

### ADR-014: Certificate Allowances and Commercial-License Gaps
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: ACL-1.0 lifted its AI-training and hosted-resale bans only where "the certificate expressly allows it", which a certificate could express only in free-text notes that no tool checks. A further review against PolyForm Shield (competition), Prosperity (trial, excuse), the Sustainable Use License (internal use, notices) and standard commercial EULA practice found that ACL-1.0 did not define "competing", did not cover contractors or the licensee's own customers, left the ownership of modifications open, had no rule for a licensee outgrowing its tier, and gave no remedy for use beyond the certificate. Its definition of a certificate still required a signature, and the order form still told buyers to verify with a published key. `license_terms.operative_license_keys` had no caller.
- **Decision**:
  1. A certificate carries `allowances`, a sorted list drawn from `licenses/terms.json` (`ai-training`, `hosted-service`). `issue --allow` (repeatable) sets them, the issuer refuses an unknown one, the verifier reports an unknown one as `INVALID_FORMAT`, and the digest covers them. ACL-1.0 Sections 3.9 and 3.10 now name the Allowance that lifts each ban.
  2. ACL-1.0 adds definitions of Allowance, Competing Product (after PolyForm Shield's "practical substitute" test) and Personnel; Personnel may act for the licensee and see source under confidentiality (2.6); customers may use the software only inside the licensee's product under flow-down terms (2.3); no use for a Competing Product (3.2); ownership of modifications and feedback (3.13); tier eligibility changes (3.14); fees for use beyond the certificate (3.15); the English text controls. Its sha256 in `terms.json` is re-pinned; no certificate has been issued, so ACL-1.0 is still unfrozen.
  3. AL-1.0 gains the English-text clause. The restricted notice declares later Versions confidential trade secrets.
  4. The order form adds Allowances, Affiliates and a tier-eligibility declaration and verifies through the register; the CLA's introduction drops the open-source wording; the FAQ states what personal data the licensor keeps. `operative_license_keys` is removed.
- **Consequences**: Exceptions are now checkable certificate data. A Prosperity-style 30-day commercial trial and a data-protection notice under Türkiye's KVKK were considered and left to the owner and counsel; the FAQ answer is a plain description, not a KVKK notice.

### ADR-015: A 28-Day Company Evaluation and a KVKK Privacy Notice
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: AL-1.0 licensed only individuals, so a company could not even try the software before buying; the owner chose a trial after reviewing Prosperity's 30-day commercial trial, and set it at 28 days. Certificates and Order Forms hold licensees' personal data and the CLA register holds GitHub usernames, so KVKK Article 10 requires an information notice. The owner also fixed the licensor's name as AegeanWorks (guideline G-001).
- **Decision**:
  1. AL-1.0 Section 4.3 grants each organization one 28-day evaluation, shared by every organization in its Control group and all their personnel and contractors, not restartable by a new person, account, copy or Version; non-production only; ending at 28 days or when an ACL-1.0 certificate is issued, after which the organization must hold that license or stop and delete its copies. Section 2.3 and Section 4 name it as the one organizational permission. COMMERCIAL.md, the FAQ, the licensing notice and the templates summarize it.
  2. `licenses/PRIVACY.md` is the KVKK Article 10 notice, with Turkish controlling and an English translation: controller AegeanWorks; data of licensees, inquirers, contributors and violators; purposes; Article 5(2) bases (c), (ç), (d), (e), (f), without consent; collection by email, Order Form, the issuance tool and GitHub comments; transfers to authorities and advisers and abroad through Proton (Switzerland) and GitHub (United States) under Article 9; retention for the license term plus statutory periods such as Turkish Commercial Code Article 82; Article 11 rights; Article 13 and 14 requests and complaints. `templates.get_privacy_notice` and `template privacy` emit it; the FAQ, README and Order Form refer to it, the last as an acknowledgment, not a consent.
- **Consequences**: Companies can evaluate before buying, and the trial's limits are checkable facts (start date on request, no third-party access). Whether AegeanWorks must register in VERBİS, and the safeguards for each transfer abroad, depend on facts the notice cannot settle: the 2025 Board decision changed the exemption criteria, and the standard-contract regime requires notifying the Authority within five business days of signing.

### ADR-016: Review Fixes Before the First Push of the Aegean Licenses
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: A review of every change since the last push found: the CLA check's verdict was the failing job of the pull-request run, which a later `/agree-cla` comment run could not turn green, because a comment run is not attached to the pull request's head and labels added by the workflow token start no new run; maintainers were exempt only when their login equalled the organization's, which never happens; the bot comment still promised dual licensing under community terms; certificate notes with Windows line endings were rejected; an allowance given as a string was split into characters; a register entry with unknown fields crashed `verify`; a second revocation overwrote the first.
- **Decision**: The CLA workflow reads the pull request for its head sha and sets an `AegeanWorks CLA` commit status on every outcome (`statuses: write`), exempts `OWNER` and `MEMBER` author associations and bots, and states the AL-1.0 and ACL-1.0 rationale. `normalize_text` turns CRLF and CR into newlines where newlines are allowed; `cert_from_dict` treats a string as one allowance; `load_register` reports a malformed entry as `ValueError`, which `verify` returns as `INVALID_FORMAT`; a revoked certificate keeps its first revocation. Each fix has a failing-first test.
- **Consequences**: The CLA status must be made a required check in branch protection to gate merges.

### ADR-017: Issuing and Operations Tooling Moves to a Private Repository
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The owner decided the licensing tools should not be given to others. Verification must stay public: ACL-1.0 Section 6 promises anyone can check a certificate against the public register. Security does not depend on hiding the issuer (authenticity is the register plus a private key), but issuing, revoking, portfolio audits and templates serve only AegeanWorks. Versions already pushed, which contain the issuer, auditor and templates, stay in this repository's history.
- **Decision**: This public package keeps the certificate model and digest (`cert.py`), the license registry and frozen agreement digests (`license_terms.py`), a read-only register (`register.py`), the verifier and a `verify`-only CLI, plus wheel bundling. The issuer, register writes, auditor, templates, certificate Markdown, scope/tier/allowance validation, storage and sanitizing move to the private AIKit project `aegean-licensing-ops` (package `aegean_licensing_ops`, CLI `aegean-ops`), which depends on this package and is in the restricted tier. Public tests build certificates with a test-only fixture (`tests/fixtures.py`) from the public model; the ops tests issue and then verify through this package.
- **Consequences**: `aegean-license issue`, `revoke`, `audit` and `template` no longer exist publicly. The certificate format stays defined in one place, here. The CI smoke test checks `verify` and the frozen ACL-1.0 digest instead of `template`.

### ADR-018: Certificate Format 2 with a Random Serial; Signature Checks Are Private
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The owner asked that verification change so that older certificates no longer work and that full verification needs both the public package and the private operations tooling. The issuer published before ADR-017 remains in this repository's history, so anyone can still produce format-1 certificates with it. The public promise in ACL-1.0 Section 6 (anyone may verify against the register) had to stay true.
- **Decision**: Certificates gain `format` (now 2) and `serial`, 64 random lowercase hex characters. The digest is SHA-256 over `aegean-certificate/2\n` plus the canonical payload, and the HMAC signature runs over `aegean-signature/2\n` plus the payload, so the two never hash the same bytes and no format-1 digest equals a format-2 one. The verifier returns `UNSUPPORTED_FORMAT` for any format other than 2, before the digest check, and `INVALID_FORMAT` for a malformed serial. The public CLI loses `--key` and `--key-file`: its `[PASS]` now rests on the register. The private `aegean-ops verify` requires the register and the signing key together and reports `AUTHENTIC` only when both pass. Three verifier tests that built certificate dicts by hand now include `format` and `serial`; their assertions are unchanged.
- **Consequences**: No certificate had been issued, so none is invalidated. Anyone can still check a certificate's format, terms, allowances and register listing; only AegeanWorks can prove the signature.

### ADR-019: An Unknown Register Status Is Malformed, Not Valid
- **Date**: 2026-10-26
- **Status**: Accepted
- **Context**: A review of the format-2 change found that `load_register` accepted any `status` string. The verifier tested only `status == "revoked"`, so a register entry written as `"revoked "` (trailing space), `"suspended"` or any other value fell through as a valid, unrevoked certificate. A register is public and may be edited by mistakes or by hand, so an unrecognised state must not silently grant a license.
- **Decision**: `load_register` accepts only `valid` and `revoked`; any other status raises `ValueError` naming the certificate. `verify_certificate` already turns a register read error into `INVALID_FORMAT`, so a misspelled revocation refuses verification instead of passing it.
- **Consequences**: A future status value needs a code change and a new ADR before a register may carry it. This is deliberate: an unknown state is not evidence of a valid grant.
- Cross-principle check: no principle section changed. Serves PRINCIPLE-003 (an unrecognised value is not a valid state) and PRINCIPLE-016 (consecutive ADR register).

### ADR-020: Game and Science Licenses, and a Catalog
- **Date**: 2026-10-26
- **Status**: Accepted
- **Context**: AL-1.0 covers software, but games need streaming, modding, an asset boundary and a DRM-free promise, and non-commercial research needs publication, reproducibility sharing and non-commercial ML training. Fitting either into AL-1.0 by hand would create a fourth undocumented variant per project. AIKit also had to pick a license and a project's title/description consistently.
- **Decision**: Add `AGL-1.0` and `ASL-1.0` as AL-1.0 plus a domain addendum; AL-1.0 applies where they do not differ. AGL-1.0 grants personal play, recording/streaming (including monetized channels), modding and free mods, and makes DRM-free distribution a covenant: the licensor ships no DRM and a distributor may not add activation, always-online checks or play-blocking telemetry. ASL-1.0 grants non-commercial research and teaching, publication, reproducibility sharing, text/data mining and non-commercial ML training, with a non-commercial share-alike for published modifications; industry-sponsored and commercial use still needs ACL-1.0. `licenses/CATALOG.md` explains which to use and names the remaining gaps. Both texts, and the catalog, are pinned by AIKit in `licenses/PIN.json`; `terms.json` stays commercial-only (certificates cite ACL-1.0).
- **Consequences**: The three personal licenses are variants of one base, so a change to AL-1.0 can be mirrored deliberately. AGL-1.0 cannot prevent a platform from imposing its own DRM outside a build's files, and ASL-1.0 is not an open-source license; both limits are stated in the catalog. A game or science project still needs an asset/data grant where its art, audio, datasets or weights are not code.
- Cross-principle check: no principle section changed. Serves PRINCIPLE-005 (the catalog documents the model), PRINCIPLE-009 (one license catalog), PRINCIPLE-011 (the limits are stated where a user meets them) and PRINCIPLE-016 (consecutive ADR register).

### ADR-021: License Hardening After a Standards Review
- **Date**: 2026-10-26
- **Status**: Accepted
- **Context**: A review against PolyForm Noncommercial 1.0.0, Creative Commons BY-NC 4.0, the OpenRAIL family, GOG's DRM-free model, the OSI Open Source Definition and SPDX custom identifiers found gaps in the first AGL-1.0/ASL-1.0 drafts: the game/science variants did not grant patents for their broader rights, the DRM-free promise did not cover mandatory clients, offline survival or consumer rights, and the asset/data boundary was stated only in the catalog even though ACL-1.0 covers code and logic only. ASL-1.0 also allowed industry funding without direction, left third-party and personal data implicit, and had no ethics/lawful-use clause.
- **Decision**:
  1. AGL-1.0 and ASL-1.0 each add an explicit patent license for the rights they grant, with the AL-1.0 patent-defense termination; they do not cover third-party or modifier patents.
  2. AGL-1.0 defines an Asset Manifest (normally `ASSETS.md`), states that unlisted assets may be used only to play the game and not extracted or included in a mod, and says commercial asset use needs a separate grant. ASL-1.0 defines Project Data as owned or sublicensable data only, keeps third-party data under its own terms, forbids personal data without a lawful basis, and requires a separate data/weights grant for commercial use.
  3. AGL-1.0's DRM-free promise now covers no mandatory client, launcher, account binding or activation; no added DRM in a permitted mod or patch; an anti-cheat carve-out limited to multiplayer integrity; offline play after online services end; mandatory consumer rights; and a no-compatibility-warranty line. This follows GOG's DRM-free definition without overpromising platform behavior.
  4. ASL-1.0 requires that an industry sponsor neither funds nor directs the free research, adds research-ethics, privacy, clinical and lawful-use limits, clarifies that reproducibility sharing is allowed but substitute dataset/model redistribution is not, and makes model outputs the researcher's responsibility.
  5. `licenses/CATALOG.md` now compares the family with CC BY-NC, PolyForm, OpenRAIL, BSL/Elastic/SSPL, MIT/Apache/GPL and GOG; states the OSI/NonCommercial distinction; and lists the remaining gaps.
- **Consequences**: The free tiers now have patent grants and domain-appropriate boundaries, so a commercial certificate can cover code while the asset/data grant is negotiated separately. The texts remain custom, non-OSI and not legal advice; non-commercial remains fact-specific, assets/data still need a grant, and counsel review is still required. The changes are not retroactive: licenses already granted for a released Version keep their text.
- Cross-principle check: no principle section changed. Serves PRINCIPLE-003 (claims checked against external standards), PRINCIPLE-005 (catalog documents the model and limits), PRINCIPLE-016 (consecutive ADR register) and PRINCIPLE-019 (no personal data in the public register or catalog).

### ADR-022: Personal Licenses Move to 1.1
- **Date**: 2026-10-26
- **Status**: Accepted
- **Context**: A comparison with more than twenty licenses (MIT, Apache-2.0, BSD-3, ISC, MPL-2.0, EPL-2.0, LGPL, GPL, AGPL, Unlicense/CC0, CC BY/BY-NC/BY-NC-SA, PolyForm Noncommercial/Small Business/Perimeter, Prosperity, Parity, BSL, Elastic 2.0, SSPL, FSL, OpenRAIL, Hippocratic, OFL, ODbL/CDLA, Godot/Unreal/Unity) confirmed the family's direction but exposed three gaps in AL/AGL/ASL: no explicit security-research permission beside the no-circumvention clause, no moral-rights/data-protection terms, and no statement that the non-commercial restriction is incompatible with GPL-3.0/AGPL-3.0. Existing Versions must keep their grants, so the texts cannot be edited in place.
- **Decision**: Publish AL-1.1, AGL-1.1 and ASL-1.1 beside the 1.0 texts. AL-1.1 adds Section 12.1 security research, third-party-component language, moral rights, data-protection/consumer-law and a GPL/AGPL compatibility statement. AGL-1.1 adds the same security-research permission to its no-circumvention clause. ASL-1.1 adds research-integrity language. The 1.0 files remain for Versions released under them; the root LICENSE, package metadata, README, catalog, asset policy and AIKit pins move to 1.1. ACL-1.0 is unchanged because commercial terms did not change.
- **Consequences**: Existing projects remain on 1.0 until the owner applies `--set`, which writes 1.1; new projects start on 1.1. The two versions are both pinned and both recognized. A project cannot silently upgrade via `publish --license auto`; the upgrade is reported and requires an explicit `--set`. The family remains source-available, not OSI open source, and is not GPL/AGPL compatible.
- Cross-principle check: no principle section changed. Serves PRINCIPLE-003 (claims checked against external licenses), PRINCIPLE-005 (catalog and README name the current text), PRINCIPLE-016 (consecutive ADR register) and PRINCIPLE-019 (no personal data added).

### ADR-023: Legal Review Checklist and Archived Drafts
- **Date**: 2026-10-26
- **Status**: Accepted
- **Context**: The license family has operative 1.1 texts plus older AL-PU, AECL and commercial-template drafts in the same directory. The catalog said counsel review was pending but gave a reviewer no hand-off. That makes it too easy to copy a superseded draft or treat an unreviewed text as release-ready.
- **Decision**: Add `licenses/LEGAL-REVIEW-CHECKLIST.md` as the counsel hand-off, covering precedence, grants, game/science/commercial terms, assets/data, consumer/privacy, trade controls and operability. The catalog names the archived drafts (`AL-PU-1.0-DRAFT.md`, `AECL-1.0.md`, `COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md`) as non-operative history and links the checklist. The checklist is explicitly not legal advice; a version is release-ready only after counsel signs the applicable items.
- **Consequences**: The remaining legal gap is now a reviewable checklist instead of an implicit promise. Archived drafts stay available for history but cannot be mistaken for current terms. The checklist must be maintained when a license version changes.
- Cross-principle check: no principle section changed. Serves PRINCIPLE-005 (living documentation), PRINCIPLE-016 (ADR register and synchronized docs) and PRINCIPLE-019 (no personal data added).

### ADR-024: Remaining Governance Instruments Are Drafted
- **Date**: 2026-10-26
- **Status**: Accepted
- **Context**: The catalog listed seven missing instruments: trademark, game asset-pack, data/model weights, security, support, provenance, OpenRAIL and dual licensing. Leaving them as prose gaps made every commercial conversation start from a blank page.
- **Decision**: Add `licenses/TRADEMARK-POLICY.md`, `licenses/commercial/GAME-ASSET-ADDENDUM-DRAFT.md`, `licenses/commercial/DATA-WEIGHTS-ADDENDUM-DRAFT.md`, `licenses/OPENRAIL-ATTACHMENT-DRAFT.md`, `policies/SECURITY-DISCLOSURE.md`, `policies/SUPPORT-POLICY.md`, `policies/PROVENANCE-POLICY.md` and `policies/DUAL-LICENSE-POLICY.md`. The catalog links them, marks the commercial and OpenRAIL attachments as drafts that bind only when named in an Order Form or project LICENSE, and leaves counsel review as the remaining gate. The ops `template` command can emit each document.
- **Consequences**: Commercial and research conversations have a concrete starting exhibit; a draft is still not operative, and a permissive/GPL-compatible grant still needs a signed writing. The catalog now distinguishes drafted from missing, and a future review can approve or reject each instrument explicitly.
- Cross-principle check: no principle section changed. Serves PRINCIPLE-005 (living documentation), PRINCIPLE-016 (ADR register and synchronized docs) and PRINCIPLE-019 (no personal data added).

### ADR-025: Permissive Grant and Security SLA Templates
- **Date**: 2026-10-26
- **Status**: Accepted
- **Context**: The dual-license policy allowed a written MIT/Apache-2.0 grant, but no template, and the support policy allowed a security SLA only in an Order Form, with no exhibit. Both gaps forced every request to start from a blank page.
- **Decision**: Add `licenses/commercial/PERMISSIVE-GRANT-TEMPLATE.md` and `licenses/commercial/SECURITY-SLA-EXHIBIT-DRAFT.md`; link them from the catalog and expose them as ops template kinds. Both are drafts that bind only when signed as part of a grant or Order Form.
- **Consequences**: A permissive/GPL-compatible request and a commercial security commitment now have a reviewable starting text. A template is not a grant or an SLA; the signature, scope and fee remain deliberate.
- Cross-principle check: no principle section changed. Serves PRINCIPLE-005 (living documentation), PRINCIPLE-016 (ADR register and synchronized docs) and PRINCIPLE-019 (no personal data added).
