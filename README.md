# aegean-licensing

[![Built with AIKit](https://img.shields.io/badge/built%20with-AIKit-6f42c1)](https://github.com/AegeanWorks/AIKit)

**Status: The Aegean License 1.0 and Aegean Commercial License 1.0 are the operative texts. Legal review is recommended before relying on either in a dispute.**

A central home for the licensing terms, license-version history, commercial licensing process, certificate tooling, and backward-compatibility policy for projects published under the Aegean brand.

---

## ⚡ 30-Second Cold-Start Quick Reference

- **Runtime Prerequisites**: Python >= 3.10 (Standard Library only; zero external runtime dependencies)
- **Build**: `pip wheel .` (build-time only: `setuptools>=77`); wheels and sdists ship the legal documents
- **CI**: `.github/workflows/ci.yml` runs the suite on Python 3.10–3.13 and verifies the built wheel
- **Canonical Regression Shield Gate**:
  ```bash
  python -m unittest discover tests
  ```

### 🛠️ AIKit Commands (run from the AIKit folder)
| Role | Command |
|---|---|
| Status, task and gates | `python aikit.py status aegean-licensing` |
| Phase 4: every gate | `python aikit.py check aegean-licensing` |
| Repair memory and map, then check | `python aikit.py fix aegean-licensing` |
| Resume an interrupted task | `python aikit.py resume aegean-licensing` |

---

## 📜 Intended Policy & Licensing Model

- **Personal Use**: Free for an individual's own private, non-commercial use under the Aegean License 1.0 ([`licenses/AL-1.0.md`](licenses/AL-1.0.md), `LicenseRef-AL-1.0`).
- **Game Use**: Games and interactive works use the Aegean Game License 1.0 ([`licenses/AGL-1.0.md`](licenses/AGL-1.0.md), `LicenseRef-AGL-1.0`): free personal play, streaming, private servers, modding and free mods, with a DRM-free covenant (no mandatory client, account binding or activation) that forbids adding DRM to a permitted mod or patch. Assets are licensed only when the LICENSE or asset manifest lists them.
- **Science Use**: Non-commercial research and teaching use the Aegean Science License 1.0 ([`licenses/ASL-1.0.md`](licenses/ASL-1.0.md), `LicenseRef-ASL-1.0`): publication, reproducibility sharing, text/data mining and non-commercial ML training. It is non-commercial source-available, not open source.
- **Which One**: [`licenses/CATALOG.md`](licenses/CATALOG.md) maps each license to the project it fits and lists the gaps still open (trademark, data/model weights, game asset packs, security and support policies).
- **Commercial & Organizational Use**: Requires the paid Aegean Commercial License 1.0 ([`licenses/ACL-1.0.md`](licenses/ACL-1.0.md)) before the use begins (`aegean-licensing@proton.me`); ACL-1.0 covers code and logic, so art, audio, datasets and model weights need a separate grant under [ASSET_POLICY.md](licenses/ASSET_POLICY.md). Each company may first evaluate for 28 days, once per company group, non-production only (AL-1.0 Section 4.3).
- **Privacy**: Personal data in licensing is processed as the KVKK notice in [`licenses/PRIVACY.md`](licenses/PRIVACY.md) describes.
- **Restricted Tier**: A project too valuable to distribute switches to the All Rights Reserved notice in [`licenses/RESTRICTED-NOTICE.md`](licenses/RESTRICTED-NOTICE.md) from a recorded cutoff commit; earlier versions keep their license.
- **No AGPL**: AegeanWorks makes no new release under AGPL-3.0.
- **Explicit Versioning**: Each release must identify its governing license and version.
- **Older Versions & Reissuance**: Older versions may be reissued under the current Aegean license only where the rights holder controls the necessary rights and the release is clearly marked as such.
- **Backward Compatibility & Non-Retroactivity**: Existing permissions granted under prior licenses—including AGPL-3.0—are not retroactively revoked. The new license cannot force existing recipients to give up a valid earlier grant. See [BACKWARD-COMPATIBILITY-DRAFT.md](policies/BACKWARD-COMPATIBILITY-DRAFT.md).

> **Operational Notice**: The root `LICENSE` is a verbatim copy of `licenses/AL-1.0.md`. Every repository or release it governs carries that exact text, and its release notes name the license version.

### Pre-Release Checklist

1. Keep AegeanWorks as the named licensor and `aegean-licensing@proton.me` as the contact in every text.
2. Confirm copyright ownership and contributor rights for every project.
3. Decide the migration plan for each repository, including Chronos's prior AGPL-licensed releases.
4. Obtain legal review for the final custom license and commercial agreement.

---

## 💻 Certificate Verification

This repository publishes the license texts, the public register of issued certificates and a
pure standard-library verifier (`aegean-license` or `python -m aegean_licensing`). Issuing,
registering and revoking certificates, portfolio audits and templates are AegeanWorks' private
operations tooling and are not distributed (ADR-017).

### 1. Verify a Certificate
```bash
python -m aegean_licensing verify license_certificate_<id>.json --project chronos   --register licenses/issued.json
```

The register (`licenses/issued.json`) is the public proof of authenticity: it lists each issued
certificate's id, digest, license type, date and status, never licensee data. An HMAC signature
can be checked only with the signing key, which is never published (ADR-013). A certificate
missing from the register is `UNREGISTERED`; a revoked one is `REVOKED`. Always use the register
from this repository, not a copy supplied with the certificate.

Only **format 2** certificates verify: each carries a random 256-bit `serial`, and its digest
is bound to the format-2 domain. Any format-1 certificate, including one made with the issuer
this repository published before ADR-018, is `UNSUPPORTED_FORMAT`. Checking the issuer's HMAC
signature needs AegeanWorks' secret key, so that step is private.

### 2. Allowances
A certificate lists the ACL-1.0 exceptions it grants (`ai-training`, `hosted-service`); the
vocabulary lives in `licenses/terms.json`, and `verify` rejects any other value.

### 3. Commercial Licensing

Commercial licensing is arranged privately by email. Nothing is sold, ordered, or paid for
through GitHub or this repository, and no prices or payment details are published here.

1. Email `aegean-licensing@proton.me` with the legal licensee name, registration or tax id,
   address, country, project(s), tier, intended scope, and desired term.
2. The licensor replies with the applicable terms and fees. The parties record them in an Order
   Form that incorporates `licenses/ACL-1.0.md`.
3. After the agreed payment is confirmed in writing, the licensor issues the certificate and
   records it in the public register. Anyone can then check it:

   ```bash
   python -m aegean_licensing verify license_certificate_<id>.json --register licenses/issued.json
   ```

A certificate's SHA-256 digest proves only that the record is internally consistent; the register
proves it was issued and not revoked. See `COMMERCIAL.md` and `licenses/COMMERCIAL_FAQ.md`.

### 4. Contributor License Agreement automation

`.github/workflows/cla-check.yml` requires external contributors to comment
`/agree-cla`. Accepted logins are recorded with the comment URL as evidence in
`.github/cla-signatures.json` on the default branch, so acceptance survives later
comment edits or deletion. A maintainer can revoke an acceptance by adding the login
to the register's `revoked` array; the workflow then fails future checks for that
contributor. Each run sets the `AegeanWorks CLA` commit status on the pull request's head, so
a `/agree-cla` comment turns it green without a new push; make that status a required check. The
workflow also labels the pull request `cla-signed`. Organization owners and members, and bots,
are exempt.

The workflow proves acceptance, not approval: merge rights still come from branch
protection. Require at least one maintainer review on the default branch so a
`cla-signed` label cannot merge a change by itself.

### 5. Continuous integration

`.github/workflows/ci.yml` runs `python -m unittest discover tests` on Python 3.10
through 3.13 and on Windows (3.12), builds a wheel, asserts that the legal documents are
bundled, installs the wheel, and smoke-tests `verify` and the frozen ACL-1.0 digest from a
directory outside the checkout.

---

## 📦 What's Inside

```text
aegean-licensing/
├── .gitignore                <- transient AIKit state and issued certificates excluded
├── .github/
│   ├── workflows/
│   │   ├── ci.yml            <- Tests on 3.10-3.13 and wheel-content verification
│   │   └── cla-check.yml     <- Automated pull-request CLA verification
│   └── cla-signatures.json   <- Durable record of accepted and revoked contributors
├── MANIFEST.in               <- Ships legal documents in source distributions
├── CHANGELOG.md              <- version and draft change history
├── LICENSE                   <- Aegean License 1.0 (copy of licenses/AL-1.0.md)
├── COMMERCIAL.md             <- Commercial licensing terms & Exhibit A
├── README.md                 <- Architecture, quickstart, and commands
├── pyproject.toml            <- Packaging metadata and console entrypoints
├── setup.py                  <- Build hook that bundles legal documents into the wheel
├── .aikit/                   <- AIKit memory: record, ledger, decisions
│   ├── project.json
│   ├── task_ledger.json
│   ├── decisions.md
│   ├── guidelines.md
│   └── codebase_map.md
├── policies/                 <- Licensing and governance policies
│   ├── BACKWARD-COMPATIBILITY-DRAFT.md <- Older versions and non-retroactivity policy
│   └── PORTFOLIO-MIGRATION-PLAN.md     <- Project-by-project migration roadmap
├── licenses/                 <- Canonical legal agreements & policies
│   ├── ACL-1.0.md            <- Full binding Aegean Commercial License agreement
│   ├── issued.json           <- Public register of issued certificates (no personal data)
│   ├── terms.json            <- License registry: scopes, tiers, allowances, pinned ACL-1.0 digest
│   ├── AL-1.0.md             <- Aegean License 1.0: free personal use
│   ├── AGL-1.0.md            <- Aegean Game License 1.0: DRM-free personal play
│   ├── ASL-1.0.md            <- Aegean Science License 1.0: non-commercial research
│   ├── CATALOG.md            <- Which license to use, what each grants, remaining gaps
│   ├── RESTRICTED-NOTICE.md  <- All Rights Reserved notice for the restricted tier
│   ├── PRIVACY.md            <- KVKK Article 10 privacy notice (Turkish controls)
│   ├── ASSET_POLICY.md       <- Delineation between source code and creative/domain assets
│   ├── COMMERCIAL_FAQ.md     <- Plain-English customer FAQ
│   ├── CONTRIBUTING_CLA.md   <- Contributor License Agreement: relicensing and patent rights
│   ├── DUAL_LICENSE_NOTICE.txt <- Standard repo and file header notice
│   └── commercial/
│       └── COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md <- Commercial agreement draft placeholder
├── aegean_licensing/         <- Verification package (pure standard library; issuing is private)
│   ├── __init__.py
│   ├── __main__.py
│   ├── cert.py               <- Frozen certificate DTO & canonical JSON hashing
│   ├── verifier.py           <- Tamper detection, signature check & scope validation
│   ├── bundler.py            <- Copies legal documents into built wheels
│   ├── license_terms.py      <- License registry and frozen agreement digests
│   ├── register.py           <- Reads the public register of issued and revoked certificates
│   └── cli.py                <- `verify` command (<250ms cold response)
└── tests/                    <- Unit test suite (100% pass, ~2ms/test)
    ├── __init__.py
    ├── fixtures.py           <- Test-only certificate builder
    ├── test_cert.py
    ├── test_verifier.py
    ├── test_bundler.py
    ├── test_register.py
    ├── test_license_terms.py
    ├── test_workflow_assets.py
    └── test_cli.py
```

---

## 📜 License

Free for personal use under the Aegean License 1.0; see [LICENSE](LICENSE). Any commercial use needs the Aegean Commercial License 1.0; see [COMMERCIAL.md](COMMERCIAL.md). Any version of this repository already released under GNU AGPL-3.0 keeps that license.
