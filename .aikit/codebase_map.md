# Codebase Map & Symbol Catalog 🗺️

> **AUTO-GENERATED & VERIFIED BY `scripts/update_knowledge_base.py`**
> This document provides an automated, up-to-date registry of all modules, classes, and exported functions across this repository.

---

## 📊 Codebase Metrics
- **Total Python Modules**: `15`
- **Total Classes**: `9`
- **Total Top-Level Functions**: `25`
- **Total Class Methods**: `41`
- **Total Source Lines**: `1624`

---

## 📦 Modules & Exported Symbols

### [`aegean_licensing/__init__.py`](aegean_licensing/__init__.py)
> *AegeanWorks Licensing Framework & Verification Tooling.*

**Size**: `17` lines (`475` bytes)

---

### [`aegean_licensing/__main__.py`](aegean_licensing/__main__.py)
> *Main execution entrypoint for python -m aegean_licensing.*

**Size**: `7` lines (`163` bytes)

---

### [`aegean_licensing/auditor.py`](aegean_licensing/auditor.py)
> *Repository Dual-Licensing Compliance Auditor.*

**Size**: `168` lines (`8254` bytes)

**Classes:**
- `class AuditReport` - *Detailed compliance report for an audited repository.*

**Functions:**
- `def audit_repository(repo_dir, check_policies)` - *Inspect repository files for compliance with AegeanWorks dual-licensing standards.*

---

### [`aegean_licensing/cert.py`](aegean_licensing/cert.py)
> *License Certificate Data Model and Cryptographic Hashing.*

**Size**: `130` lines (`4999` bytes)

**Classes:**
- `class LicenseCertificate` - *Immutable data transfer object representing a granted commercial license.*
  - Method `.__post_init__()`

**Functions:**
- `def compute_canonical_payload(data)` - *Serialize dictionary excluding digest and signature into deterministic UTF-8 bytes.*
- `def compute_digest(data)` - *Compute SHA-256 digest of canonical license payload.*
- `def compute_signature(data, secret_key)` - *Compute HMAC-SHA256 signature of canonical license payload using secret key.*
- `def cert_to_dict(cert)` - *Convert LicenseCertificate to dictionary representation.*
- `def cert_from_dict(data)` - *Construct LicenseCertificate from raw dictionary data.*
- `def cert_to_markdown(cert)` - *Render LicenseCertificate as a printable Markdown document.*

---

### [`aegean_licensing/cli.py`](aegean_licensing/cli.py)
> *AegeanWorks Licensing Command-Line Interface.*

**Size**: `264` lines (`10329` bytes)

**Functions:**
- `def _build_parser()`
- `def _handle_issue(args)`
- `def _handle_verify(args)`
- `def _handle_audit(args)`
- `def _handle_template(args)`
- `def main(argv)`

---

### [`aegean_licensing/issuer.py`](aegean_licensing/issuer.py)
> *Commercial License Certificate Issuance Module.*

**Size**: `103` lines (`3308` bytes)

**Functions:**
- `def _write_atomic(path, content)` - *Write text to destination atomically using temp file, fsync, and replace.*
- `def issue_certificate(licensee_name, licensee_contact, license_type, projects, scope, is_perpetual, expires_at, notes, secret_key, cert_id, issued_at, output_dir)` - *Generate and return an authentic LicenseCertificate, optionally saving to disk.*

---

### [`aegean_licensing/templates.py`](aegean_licensing/templates.py)
> *Canonical Licensing Templates and Boilerplate Generators.*

**Size**: `137` lines (`5826` bytes)

**Functions:**
- `def _read_file_or_fallback(rel_path, fallback)` - *Read template file relative to repository root, falling back to static string.*
- `def get_dual_license_rider()` - *Return canonical dual-licensing rider for LICENSE files.*
- `def get_commercial_md()` - *Return standard COMMERCIAL.md content.*
- `def get_pyproject_snippet()` - *Return pyproject.toml licensing snippet.*
- `def get_personal_use_license()` - *Return draft Aegean Licensing Personal Use License (AL-PU 1.0).*
- `def get_commercial_agreement_template()` - *Return draft Aegean Commercial License Agreement (ACLA 1.0).*
- `def get_backward_compatibility_policy()` - *Return draft Backward Compatibility Policy.*
- `def get_contributor_cla()` - *Return AegeanWorks Contributor License Agreement.*
- `def get_asset_policy()` - *Return AegeanWorks Asset Separation & Licensing Policy.*

---

### [`aegean_licensing/verifier.py`](aegean_licensing/verifier.py)
> *Commercial License Certificate Verification Module.*

**Size**: `152` lines (`5225` bytes)

**Classes:**
- `class VerificationResult` - *Outcome of validating a License Grant Certificate.*

**Functions:**
- `def verify_certificate(target, secret_key, check_project, reference_date)` - *Verify authenticity, tamper-resistance, expiration, and scope of a license certificate.*

---

### [`tests/__init__.py`](tests/__init__.py)
> *Test suite for aegean-licensing.*

**Size**: `1` lines (`39` bytes)

---

### [`tests/test_auditor.py`](tests/test_auditor.py)
> *Unit tests for repository compliance auditor.*

**Size**: `120` lines (`4929` bytes)

**Classes:**
- `class TestAuditor` - *Test repository licensing audit checks and warnings.*
  - Method `.setUp()`
  - Method `.test_compliant_repository()`
  - Method `.test_missing_license_fails()`
  - Method `.test_missing_commercial_md_fails()`
  - Method `.test_detects_obsolete_enterprise_bureaucracy()`
  - Method `.test_alpu_compliant_repository()`
  - Method `.test_audit_with_policies_check()`

---

### [`tests/test_cert.py`](tests/test_cert.py)
> *Unit tests for LicenseCertificate and cryptographic utilities.*

**Size**: `90` lines (`2843` bytes)

**Classes:**
- `class TestLicenseCertificate` - *Test certificate data transfer object and canonical hashing.*
  - Method `.test_cert_is_frozen()`
  - Method `.test_canonical_payload_is_deterministic()`
  - Method `.test_digest_computation()`
  - Method `.test_signature_computation()`
  - Method `.test_to_and_from_dict_roundtrip()`
  - Method `.test_markdown_rendering()`

---

### [`tests/test_cli.py`](tests/test_cli.py)
> *Unit tests for aegean-licensing CLI.*

**Size**: `85` lines (`2942` bytes)

**Classes:**
- `class TestCLI` - *Test CLI commands, argument handling, and exit codes.*
  - Method `.setUp()`
  - Method `.test_version_output()`
  - Method `.test_issue_and_verify_roundtrip_cli()`
  - Method `.test_template_generation_cli()`
  - Method `.test_issue_with_type_cli()`

---

### [`tests/test_issuer.py`](tests/test_issuer.py)
> *Unit tests for commercial license certificate issuer.*

**Size**: `81` lines (`2972` bytes)

**Classes:**
- `class TestIssuer` - *Test certificate creation and disk serialization.*
  - Method `.setUp()`
  - Method `.test_issue_valid_perpetual_certificate()`
  - Method `.test_issue_with_custom_license_type()`
  - Method `.test_issue_with_hmac_signature()`
  - Method `.test_validation_errors()`
  - Method `.test_issue_writes_atomic_files()`

---

### [`tests/test_templates.py`](tests/test_templates.py)
> *Unit tests for licensing template generation.*

**Size**: `70` lines (`2473` bytes)

**Classes:**
- `class TestTemplates` - *Test standard licensing templates.*
  - Method `.test_dual_license_rider_content()`
  - Method `.test_commercial_md_content()`
  - Method `.test_pyproject_snippet_content()`
  - Method `.test_personal_use_license_content()`
  - Method `.test_commercial_agreement_template_content()`
  - Method `.test_backward_compatibility_policy_content()`
  - Method `.test_contributor_cla_content()`
  - Method `.test_asset_policy_content()`

---

### [`tests/test_verifier.py`](tests/test_verifier.py)
> *Unit tests for commercial license certificate verifier.*

**Size**: `199` lines (`7385` bytes)

**Classes:**
- `class TestVerifier` - *Test certificate verification, tamper detection, and scope checking.*
  - Method `.setUp()`
  - Method `.test_verify_valid_certificate()`
  - Method `.test_verify_from_json_file()`
  - Method `.test_verify_detects_tampered_digest()`
  - Method `.test_verify_detects_tampered_payload_field()`
  - Method `.test_verify_hmac_signature()`
  - Method `.test_verify_expired_certificate()`
  - Method `.test_verify_scope_filtering()`

---
