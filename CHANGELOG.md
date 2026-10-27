# Changelog

All notable changes to Aegean Licensing documents are recorded here.

## Unreleased — Draft v0.3

- **Certificate format 2**: certificates carry a random 256-bit `serial` and a format-bound digest; format-1 certificates are rejected as `UNSUPPORTED_FORMAT`, and the public CLI no longer checks signatures, which need AegeanWorks' key (ADR-018).
- **Public verification specification**: `licenses/VERIFICATION.md` pins the format-2 canonicalization, ASCII escaping, project sorting, digest prefix and check order, with `licenses/verification-vector.json` as a known-answer vector for third-party and browser verifiers. The vector is explicitly not an issued certificate.
- **Malformed certificate files**: a JSON file holding a list, string, number or `null` is reported as `INVALID_FORMAT` instead of raising `AttributeError` from the format check.
- **Unknown register status**: a register entry whose `status` is anything other than `valid` or `revoked` is refused as malformed; it used to fall through as a valid certificate.
- **Game and science licenses**: added AGL-1.0 (DRM-free personal play, streaming, modding) and ASL-1.0 (non-commercial research, publication, reproducibility, non-commercial ML training), with `licenses/CATALOG.md` mapping each to the project it fits.
- **License hardening**: AGL-1.0 and ASL-1.0 now grant patents for their rights, AGL-1.0 promises no mandatory client/account and offline survival, and both state the asset/data boundary; the catalog compares the family with CC BY-NC, PolyForm, OpenRAIL, BSL/Elastic/SSPL, MIT/Apache/GPL and GOG's DRM-free model.
- **Permissive grant and security SLA**: added a named MIT/Apache-2.0 grant template and a commercial security-SLA exhibit, both drafts until signed.
- **SPDX/REUSE**: added the metadata policy and AIKit generation of REUSE.toml plus LICENSES/LicenseRef-*.txt.
- **Governance instruments**: added trademark, game-asset, data/weights, security, support, provenance, OpenRAIL and dual-license drafts/policies; the catalog marks drafts as non-operative until counsel review.
- **License 1.1**: AL-1.1, AGL-1.1 and ASL-1.1 add explicit security-research, moral-rights, data-protection and GPL/AGPL-compatibility terms; the 1.0 texts stay for Versions released under them. ACL-1.0 is unchanged.
- **Verification-only public package**: issuing, registering, revoking, audits and templates move to AegeanWorks' private operations tooling; this package keeps the certificate model, license registry, register reading and `verify` (ADR-017).
- **Review fixes**: the CLA check sets an `AegeanWorks CLA` commit status that a `/agree-cla` comment turns green and exempts organization members; CRLF notes, string allowances, malformed registers and repeated revocations are handled (ADR-016).
- **Company evaluation and KVKK notice**: AL-1.0 Section 4.3 allows one 28-day, non-production evaluation per company group; `licenses/PRIVACY.md` is the KVKK Article 10 privacy notice, emitted by `template privacy` (ADR-015).
- **Certificate allowances and ACL-1.0 gaps**: certificates carry checked `allowances` (`ai-training`, `hosted-service`) set with `issue --allow`; ACL-1.0 defines Competing Product, covers Personnel and the licensee's customers, settles ownership of modifications, tier changes and use beyond the certificate, and makes the English text control. The order form gains Allowances, Affiliates and a tier declaration (ADR-014).
- **Aegean License 1.0 and Aegean Commercial License 1.0**: the personal-use draft (AL-PU) becomes the Aegean License 1.0 (`licenses/AL-1.0.md`, also the root `LICENSE`) and AECL-1.0 becomes the Aegean Commercial License 1.0 (`licenses/ACL-1.0.md`). Both gain conditions-based acceptance, company and control definitions, patent defense, required notices, a single cure period, per-version licensing, no circumvention and no AI training. New `licenses/RESTRICTED-NOTICE.md` for projects withdrawn from distribution. The AGPL-3.0 track is removed from the root license, templates, auditor and packaging metadata; versions already released under AGPL-3.0 keep it (ADR-012).
- **Public certificate register and frozen agreements**: `licenses/issued.json` lists each issued certificate's id, digest, license type, date and status, with no personal data; `issue --register` records, `revoke` revokes, and `verify --register` reports `UNREGISTERED` or `REVOKED`. HMAC keys are never published, so the register is the public proof of authenticity. `terms.json` pins the sha256 of ACL-1.0, and issuance refuses an edited agreement. `--key-file` keeps the signing key out of shell history. The never-released Monero settlement tooling and the HTTP issuance server are removed: licensing is arranged by email (ADR-011, ADR-013).
- **License gaps closed**: AL-1.0 gains an own-work clause, how a Version's license is identified, how breach notice is given, survival, and export compliance; ACL-1.0 ends deployed-version rights on termination for breach, adds compliance certification, an AI-coding-assistant carve-out and register-based verification and revocation. Documentation moves from CC-BY-4.0 to AL-1.0.
- **License registry and certificate terms**: certificates now cite a registered license key, a validated tier, a controlled scope, legal identity fields, and the SHA-256 digest of the incorporated agreement text. Unknown types, tiers, or scopes are rejected at issuance and verification, and an unsigned certificate is reported as tamper-evident but not authentic.
- **Durable, auditable CLA register**: `.github/cla-signatures.json` now records the source comment URL as evidence and supports a `revoked` list maintained by repository owners; a revoked contributor fails the check even if a comment remains.
- **CI enforcement**: `.github/workflows/ci.yml` runs the test suite on Python 3.10–3.13 and verifies that a built wheel contains the legal documents and can emit templates outside a checkout.
- **Injection-resistant certificates**: text fields reject control and non-printable Unicode, and Markdown rendering escapes untrusted values.
- **Wheel-bundled legal documents**: `setup.py` now copies `licenses/`, `policies/`, and the CLA workflow into `aegean_licensing/resources/`, and the template reader falls back to them, so `template` works from an installed wheel without a repository checkout.
- **Packaging correctness**: Package discovery is explicit (`aegean_licensing` only), license metadata uses PEP 639 (`setuptools>=77`), `MANIFEST.in` ships the legal documents in sdists, and build artifacts are ignored.
- **CLA workflow re-check**: Agreement labels now trigger a fresh verification run (so a signed PR turns green), the `cla-signed` label is created on demand, `/agree-cla` must stand on its own line, and the CLA link is absolute.
- **Migration plan corrections**: Marked the plan draft and contingent, added a legal-approval gate, corrected source filenames, and replaced deprecated PEP 621 license metadata with PEP 639 guidance.
- **Automated CLA Verification**: Added `.github/workflows/cla-check.yml`, which requires contributors to comment `/agree-cla` and labels compliant pull requests `cla-signed`.
- **Portfolio Migration Plan**: Added `policies/PORTFOLIO-MIGRATION-PLAN.md` with per-project migration milestones, the six-step pre-migration release checklist, and user-facing transition FAQ. Available through `template migration` and `template cla-action`.
- **Commercial Monetization Triggers**: Explicitly defined the exact triggers where personal use ends and commercial licensing begins (third-party cloud deployment, first revenue, investment, client delivery).
- **Student & Academic Learner Protection**: Added explicit carveout protecting individual enrolled students and self-study learners from organizational restrictions.
- **Freelancer & Contractor Boundaries**: Clarified that billable client work, freelance deliverables, and contract hours require a Commercial License.
- **Inbound CLA Linkage**: Integrated Contributor License Agreement terms ensuring all public PRs grant dual-licensing rights to AegeanWorks.
- **Commercial Cure Ramp**: Added Section 9.1 permitting unauthorized commercial users to cure infringements by purchasing retroactive commercial licenses in lieu of immediate statutory litigation.
- **Commercial Tier Architecture**: Fleshed out `COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md` into a 3-tier structure (Indie/Startup, Enterprise/SaaS, OEM/Embedded) backed by cryptographic License Grant Certificates.

## Draft v0.2

- Added draft Aegean Licensing Personal Use License (AL-PU 1.0 draft v0.2).
- Added backward-compatibility policy for versioned licenses and older releases.
- Clarified that older versions newly distributed by the rights holder may use current terms only where legally authorized and expressly reissued under those terms.
- Clarified that valid earlier grants, including AGPL-3.0, cannot be retroactively revoked by this policy.
