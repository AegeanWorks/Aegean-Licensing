# aegean-licensing

[![Built with AIKit](https://img.shields.io/badge/built%20with-AIKit-6f42c1)](https://github.com/AegeanWorks/AIKit)

**Status: Draft repository proposal. The custom license text in this repository is not yet final or operative.**

A central home for the licensing terms, license-version history, commercial licensing process, certificate tooling, and backward-compatibility policy for projects published under the Aegean brand.

---

## ⚡ 30-Second Cold-Start Quick Reference

- **Runtime Prerequisites**: Python >= 3.10 (Standard Library only; zero external runtime dependencies)
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

- **Personal Use**: Personal, non-commercial use is intended to be free under the eventual Aegean Licensing Personal Use License (`AL-PU-1.0-DRAFT.md`).
- **Commercial & Organizational Use**: Commercial and organizational use requires separate prior written authorization from the rights holder (`aegean-licensing@proton.me`).
- **Explicit Versioning**: Each release must identify its governing license and version.
- **Older Versions & Reissuance**: Older versions may be reissued under the current Aegean license only where the rights holder controls the necessary rights and the release is clearly marked as such.
- **Backward Compatibility & Non-Retroactivity**: Existing permissions granted under prior licenses—including AGPL-3.0—are not retroactively revoked. The new license cannot force existing recipients to give up a valid earlier grant. See [BACKWARD-COMPATIBILITY-DRAFT.md](policies/BACKWARD-COMPATIBILITY-DRAFT.md).

> **Operational Notice**: Do not place a draft custom license in the root as if it were the final operative `LICENSE`. When the terms are approved, publish the final text with a clear effective date and add the exact license text to every repository/release it governs. Add a `LICENSE` file only when the applicable terms have been finalized for that project.

### Pre-Release Checklist

1. Replace all placeholders with the actual rights holder and contact details.
2. Confirm copyright ownership and contributor rights for every project.
3. Decide the migration plan for each repository, including Chronos's prior AGPL-licensed releases.
4. Obtain legal review for the final custom license and commercial agreement.

---

## 💻 CLI & Verification Tooling

The repository includes pure standard-library tooling (`aegean-license` or `python -m aegean_licensing`):

### 1. Issue a Commercial License Certificate
```bash
python -m aegean_licensing issue \
  --licensee "Acme Corp" \
  --contact "legal@acme.com" \
  --projects "chronos,AIKit" \
  --scope "proprietary-saas-and-redistribution" \
  --output-dir ./certs
```

### 2. Verify an Authentic Certificate
```bash
python -m aegean_licensing verify ./certs/license_certificate_*.json --project chronos
```

### 3. Audit a Repository for Compliance
```bash
python -m aegean_licensing audit /path/to/project --strict
```

### 4. Output Boilerplate Licensing Templates
```bash
python -m aegean_licensing template all --output-dir ./licensing_boilerplate
```

---

## 📦 What's Inside

```text
aegean-licensing/
├── .gitignore                <- transient AIKit state excluded
├── CHANGELOG.md              <- version and draft change history
├── LICENSE                   <- GNU AGPL-3.0 with AegeanWorks dual-licensing rider
├── COMMERCIAL.md             <- Commercial licensing terms & Exhibit A
├── README.md                 <- Architecture, quickstart, and commands
├── pyproject.toml            <- Packaging metadata and console entrypoints
├── .aikit/                   <- AIKit memory: record, ledger, decisions
│   ├── project.json
│   ├── task_ledger.json
│   ├── decisions.md
│   ├── guidelines.md
│   └── codebase_map.md
├── policies/                 <- Licensing and governance policies
│   └── BACKWARD-COMPATIBILITY-DRAFT.md <- Older versions and non-retroactivity policy
├── licenses/                 <- Canonical legal agreements & policies
│   ├── AECL-1.0.md           <- Full binding Aegean-E Commercial License agreement
│   ├── AL-PU-1.0-DRAFT.md    <- Draft Aegean Licensing Personal Use License
│   ├── ASSET_POLICY.md       <- Delineation between source code and creative/domain assets
│   ├── COMMERCIAL_FAQ.md     <- Plain-English customer FAQ
│   ├── CONTRIBUTING_CLA.md   <- Contributor License Agreement for dual-licensing rights
│   ├── DUAL_LICENSE_NOTICE.txt <- Standard repo and file header notice
│   └── commercial/
│       └── COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md <- Commercial agreement draft placeholder
├── aegean_licensing/         <- Core Python package (Pure Standard Library)
│   ├── __init__.py
│   ├── __main__.py
│   ├── cert.py               <- Frozen certificate DTO & canonical JSON hashing
│   ├── issuer.py             <- Atomic certificate generator & exporter
│   ├── verifier.py           <- Tamper detection, signature check & scope validation
│   ├── auditor.py            <- Repository compliance linter & fixer
│   ├── templates.py          <- Canonical legal boilerplates
│   └── cli.py                <- Subcommand dispatcher (<250ms cold response)
└── tests/                    <- Unit test suite (100% pass, ~2ms/test)
    ├── __init__.py
    ├── test_cert.py
    ├── test_issuer.py
    ├── test_verifier.py
    ├── test_auditor.py
    ├── test_templates.py
    └── test_cli.py
```

---

## 📜 License

GNU Affero General Public License v3.0; see [LICENSE](LICENSE). For commercial licensing and proprietary rights, see [COMMERCIAL.md](COMMERCIAL.md). Draft custom terms are located in [licenses/](licenses/).
