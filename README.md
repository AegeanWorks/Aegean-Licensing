# aegean-licensing

[![Built with AIKit](https://img.shields.io/badge/built%20with-AIKit-6f42c1)](https://github.com/AegeanWorks/AIKit)

Official dual-licensing framework, commercial agreements, and certificate verification tooling for **AegeanWorks**.

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

## 🎯 Purpose & Dual-Licensing Architecture

AegeanWorks authors high-performance software, developer tools, and machine intelligence runtimes. `aegean-licensing` establishes the canonical legal framework and automated compliance tooling across the entire AegeanWorks portfolio.

### The Two Tracks

1. **Track A — Open-Source Community Track (GNU AGPL-3.0-or-later)**:
   - Free for developers, students, researchers, and commercial organizations.
   - Preserves open source freedom: any distribution or network-hosted modified service triggers complete corresponding source code disclosure under AGPL-3.0 Section 13.
2. **Track B — Commercial License Track (Aegean-E Commercial License - AECL-1.0)**:
   - Designed for enterprises and startups requiring closed-source operations, proprietary cloud SaaS deployments, and closed redistribution.
   - Completely waives AGPL copyleft obligations.
   - Pure copyright grant sold **"AS-IS"** with zero warranty, zero support SLAs, and zero corporate procurement bureaucracy.

---

## 💻 CLI Usage

The package exposes a fast, standalone CLI (`aegean-license` or `python -m aegean_licensing`):

### 1. Issue a License Grant Certificate
```bash
python -m aegean_licensing issue \
  --licensee "Acme Corp" \
  --contact "legal@acme.com" \
  --projects "chronos,AIKit" \
  --scope "proprietary-saas-and-redistribution" \
  --output-dir ./certs
```
Generates a tamper-evident `.json` certificate and human-readable `.md` certificate with a canonical SHA-256 integrity digest and optional HMAC signature.

### 2. Verify an Authentic Certificate
```bash
python -m aegean_licensing verify ./certs/license_certificate_*.json --project chronos
```
Validates SHA-256 payload integrity, checks expiration date, and confirms whether a specific project is authorized.

### 3. Audit a Repository for Compliance
```bash
python -m aegean_licensing audit /path/to/project --strict
```
Inspects `LICENSE`, `COMMERCIAL.md`, and `pyproject.toml` to ensure:
- GNU AGPL-3.0 base license is present.
- Dual-Licensing Notice rider is attached.
- `COMMERCIAL.md` correctly specifies AECL terms and Exhibit A without obsolete corporate bureaucracy.
- Package metadata names `AegeanWorks` and `aegean-licensing@proton.me`.

### 4. Generate Canonical Licensing Templates
```bash
python -m aegean_licensing template all --output-dir ./licensing_boilerplate
```

---

## 📦 What's Inside

```text
aegean-licensing/
├── .gitignore                <- transient AIKit state excluded
├── LICENSE                   <- GNU AGPL-3.0 with AegeanWorks dual-licensing rider
├── COMMERCIAL.md             <- Commercial licensing terms & Exhibit A
├── README.md                 <- Architecture, quickstart, and commands
├── pyproject.toml            <- Packaging metadata and console entrypoints
├── .aikit/                   <- AIKit memory: record, ledger, decisions
│   ├── project.json
│   ├── task_ledger.json
│   ├── decisions.md
│   └── guidelines.md
├── licenses/                 <- Canonical legal agreements & policies
│   ├── AECL-1.0.md           <- Full binding Aegean-E Commercial License agreement
│   ├── DUAL_LICENSE_NOTICE.txt <- Standard repo and file header notice
│   ├── ASSET_POLICY.md       <- Delineation between source code and creative/domain assets
│   ├── CONTRIBUTING_CLA.md   <- Contributor License Agreement for dual-licensing rights
│   └── COMMERCIAL_FAQ.md     <- Plain-English customer FAQ
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

GNU Affero General Public License v3.0; see [LICENSE](LICENSE). For commercial licensing and proprietary rights, see [COMMERCIAL.md](COMMERCIAL.md).
