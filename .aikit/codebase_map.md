# Codebase Map & Symbol Catalog 🗺️

> **AUTO-GENERATED & VERIFIED BY `scripts/update_knowledge_base.py`**
> This document provides an automated, up-to-date registry of all modules, classes, and exported functions across this repository.

---

## 📊 Codebase Metrics
- **Total Python Modules**: `25`
- **Total Classes**: `27`
- **Total Top-Level Functions**: `35`
- **Total Class Methods**: `105`
- **Total Source Lines**: `2327`

---

## 📦 Modules & Exported Symbols

### [`aegean_licensing/__init__.py`](aegean_licensing/__init__.py)
> *Aegean License texts and public certificate verification (issuing is private, ADR-017).*

**Size**: `15` lines (`428` bytes)

---

### [`aegean_licensing/__main__.py`](aegean_licensing/__main__.py)
> *Main execution entrypoint for python -m aegean_licensing.*

**Size**: `7` lines (`163` bytes)

---

### [`aegean_licensing/bounded_json.py`](aegean_licensing/bounded_json.py)
> *Bounded JSON loading for files that cross an untrusted boundary.*

**Size**: `137` lines (`5062` bytes)

**Classes:**
- `class ParseLimits`
- `class TooLarge` - *The input exceeded the byte cap before or during the bounded read.*
  - Method `.__init__(observed, limit, variable)`
- `class TooDeep` - *The input nested deeper than the parser is willing to recurse.*
  - Method `.__init__(depth, limit)`
- `class TooManyNodes` - *The input carries more structural nodes than the parser accepts.*
  - Method `.__init__(count, limit)`
- `class ConfigError` - *A configured parse limit is not a positive byte count with an optional MB/GB suffix.*

**Functions:**
- `def parse_limit(raw, *, default, variable)` - *Resolve one limit, accepting plain bytes or the binary suffixes MB and GB.*
- `def limits_from_env(environ)` - *Read the three limits from the environment, validating each value at startup.*
- `def _guard_structure(text, limits)` - *Reject depth and node bombs before json.loads can recurse or allocate freely.*
- `def load_bounded(path, limits)` - *Read and parse one JSON file under byte, depth and node limits.*

---

### [`aegean_licensing/bundler.py`](aegean_licensing/bundler.py)
> *Bundle the repository's licensing documents into the built Python package.*

**Size**: `38` lines (`1391` bytes)

**Functions:**
- `def bundle_documents(repo_root, destination_root)` - *Copy legal documents under destination_root, returning the number of files copied.*
- `def _iter_sources(repo_root)`

---

### [`aegean_licensing/cert.py`](aegean_licensing/cert.py)
> *License Certificate Data Model and Cryptographic Hashing.*

**Size**: `182` lines (`7409` bytes)

**Classes:**
- `class LicenseCertificate` - *Immutable data transfer object representing a granted commercial license.*
  - Method `.__post_init__()`

**Functions:**
- `def _canonical_value(value)` - *Normalize a JSON value to the intersection of Python and JavaScript exact values.*
- `def compute_canonical_payload(data)` - *Serialize dictionary excluding digest and signature into deterministic UTF-8 bytes.*
- `def compute_digest(data)` - *SHA-256 of the format-2 digest domain and the canonical license payload.*
- `def compute_signature(data, secret_key)` - *HMAC-SHA256 of the format-2 signature domain and the canonical payload, keyed by the licensor.*
- `def cert_to_dict(cert)` - *Convert LicenseCertificate to dictionary representation.*
- `def _allowance_tuple(raw)` - *Allowances as a tuple; a lone string is one allowance, not a sequence of characters.*
- `def _format_number(raw)` - *The certificate format as an int; anything unreadable is format 0, which never verifies.*
- `def cert_from_dict(data)` - *Construct LicenseCertificate from raw dictionary data.*

---

### [`aegean_licensing/cli.py`](aegean_licensing/cli.py)
> *Aegean License Certificate verification command line (`aegean-license verify`).*

**Size**: `95` lines (`3937` bytes)

**Functions:**
- `def _build_parser()`
- `def _handle_verify(args)`
- `def main(argv)`

---

### [`aegean_licensing/fingerprint.py`](aegean_licensing/fingerprint.py)
> *A stable identity for the rules a verification result was produced under.*

**Size**: `61` lines (`2337` bytes)

**Classes:**
- `class VerificationProfile`
- `class FingerprintMismatch` - *Two results were produced under different verification rules.*

**Functions:**
- `def ruleset_fingerprint(profile, rule_digests)` - *SHA-256 over the declarative profile and the ordered rule identities.*
- `def compare_results(left, right)` - *Refuse to compare results whose ruleset fingerprints differ or are missing.*

---

### [`aegean_licensing/license_terms.py`](aegean_licensing/license_terms.py)
> *Canonical license registry: the types, scopes, tiers, and term digests a certificate may cite.*

**Size**: `152` lines (`6018` bytes)

**Classes:**
- `class LicenseTerms` - *One operative license agreement and the vocabulary its certificates may use.*
  - Property `.is_operative`

**Functions:**
- `def _registry_paths()`
- `def _load_registry_document()`
- `def load_registry()` - *Return every registered license keyed by its canonical name.*
- `def resolve_license(key, require_operative)` - *Look up a license key, refusing unknown or non-operative agreements.*
- `def normalize_document_text(text)` - *Normalize line endings before hashing so a checkout's EOL style cannot change the digest.*
- `def compute_terms_digest(document_text)` - *Return the SHA-256 of a license document's normalized UTF-8 text.*
- `def _document_paths(document)`
- `def read_license_document(terms)` - *Read the operative agreement text from the checkout or the packaged resources.*
- `def terms_digest(terms)` - *Return the digest of the agreement text a certificate must cite. An agreement whose text no*

---

### [`aegean_licensing/metadata.py`](aegean_licensing/metadata.py)
> *Validation and normalization for certificate fields that reach a renderer.*

**Size**: `34` lines (`1448` bytes)

**Classes:**
- `class MetadataError` - *A rendered certificate field carries markup or a control character.*
  - Method `.__init__(field, category, message)`

**Functions:**
- `def normalize_metadata_text(field, value, max_bytes)` - *Collapse whitespace, reject markup/control characters, and cap UTF-8 length.*

---

### [`aegean_licensing/register.py`](aegean_licensing/register.py)
> *Public certificate register: which certificates AegeanWorks issued, and which it revoked (ADR-013).*

**Size**: `75` lines (`3233` bytes)

**Classes:**
- `class RegisterEntry` - *One issued certificate, as the public may see it.*

**Functions:**
- `def load_register(path)` - *Every entry keyed by certificate id; a missing register is empty.*

---

### [`aegean_licensing/verifier.py`](aegean_licensing/verifier.py)
> *Commercial License Certificate Verification Module.*

**Size**: `360` lines (`14921` bytes)

**Classes:**
- `class VerificationResult` - *Outcome of validating a License Grant Certificate.*

**Functions:**
- `def _type_error(data)` - *A field whose JSON type cannot be read safely, or None.*
- `def verify_certificate(target, secret_key, check_project, reference_date, register_path)` - *Verify authenticity, tamper-resistance, expiration, and scope of a license certificate. With*

---

### [`setup.py`](setup.py)
> *Build hook that bundles the repository's legal documents into the wheel.*

**Size**: `29` lines (`887` bytes)

**Classes:**
- `class BundleDocuments` - *Copy licenses, policies, and the CLA workflow into the built package.*
  - Method `.run()`

**Functions:**
- `def _load_bundler()`

---

### [`tests/__init__.py`](tests/__init__.py)
> *Test suite for aegean-licensing.*

**Size**: `1` lines (`39` bytes)

---

### [`tests/fixtures.py`](tests/fixtures.py)
> *Test-only certificate builder (ADR-017).*

**Size**: `58` lines (`2434` bytes)

**Functions:**
- `def issue_certificate(licensee_name, licensee_contact, license_type, projects, scope, is_perpetual, expires_at, notes, secret_key, cert_id, issued_at, tier, allowances)`
- `def write_register(path, *certs, revoked)` - *A register file listing `certs`, with the ids in `revoked` marked revoked.*

---

### [`tests/test_bounded_json.py`](tests/test_bounded_json.py)
> *Unit tests for bounded JSON loading (IDEA-118).*

**Size**: `109` lines (`4503` bytes)

**Classes:**
- `class TestParseLimits`
  - Method `.test_plain_bytes_and_binary_suffixes()`
  - Method `.test_invalid_values_are_config_errors_not_silent_defaults()`
  - Method `.test_environment_limits_are_read_and_validated()`
- `class TestLoadBounded`
  - Method `.setUp()`
  - Method `.write(name, content)`
  - Method `.test_file_exactly_at_the_byte_cap_parses()`
  - Method `.test_one_byte_over_the_cap_is_too_large()`
  - Method `.test_depth_is_bounded_below_the_byte_cap()`
  - Method `.test_node_count_is_bounded()`
  - Method `.test_utf8_bom_is_accepted()`
  - Method `.test_corrupt_json_under_the_cap_raises_a_value_error()`
  - Method `.test_register_loader_uses_the_bounded_path()`
  - Method `.test_verifier_file_loader_uses_the_bounded_path()`

---

### [`tests/test_bundler.py`](tests/test_bundler.py)
> *Unit tests for bundling licensing documents into the built package.*

**Size**: `45` lines (`1920` bytes)

**Classes:**
- `class TestBundler` - *Test document discovery and copy layout.*
  - Method `.setUp()`
  - Method `.test_documents_are_copied_into_package_resources()`
  - Method `.test_empty_repository_is_rejected()`

---

### [`tests/test_cert.py`](tests/test_cert.py)
> *Unit tests for LicenseCertificate and cryptographic utilities.*

**Size**: `89` lines (`3005` bytes)

**Classes:**
- `class TestLicenseCertificate` - *Test certificate data transfer object and canonical hashing.*
  - Method `.test_cert_is_frozen()`
  - Method `.test_canonical_payload_is_deterministic()`
  - Method `.test_digest_computation()`
  - Method `.test_format_2_binds_digest_and_signature_to_their_own_domains()`
  - Method `.test_signature_computation()`
  - Method `.test_to_and_from_dict_roundtrip()`

---

### [`tests/test_cli.py`](tests/test_cli.py)
> *Unit tests for the public verification command line.*

**Size**: `88` lines (`3828` bytes)

**Classes:**
- `class TestCLI` - *The public CLI verifies; issuing and revoking are private (ADR-017).*
  - Method `.setUp()`
  - Method `.write_cert(cert)`
  - Method `.run_cli(*argv)`
  - Method `.test_version_output()`
  - Method `.test_only_verify_is_public()`
  - Method `.test_verify_against_the_register()`
  - Method `.test_unregistered_certificate_fails_with_the_register()`
  - Method `.test_an_explicitly_missing_register_is_an_error()`
  - Method `.test_the_public_cli_has_no_signing_key_option()`

---

### [`tests/test_fingerprint.py`](tests/test_fingerprint.py)
> *Unit tests for the verification-ruleset fingerprint (IDEA-076).*

**Size**: `53` lines (`2252` bytes)

**Classes:**
- `class TestFingerprint`
  - Method `.test_default_fingerprint_is_stable_and_order_independent()`
  - Method `.test_a_profile_change_changes_the_fingerprint()`
  - Method `.test_compare_accepts_equal_fingerprints_and_rejects_mismatch()`
  - Method `.test_unfingerprinted_results_never_compare_equal()`
  - Method `.test_verifier_results_carry_the_default_fingerprint()`

---

### [`tests/test_license_terms.py`](tests/test_license_terms.py)
> *Unit tests for the frozen text of operative agreements (ADR-013).*

**Size**: `48` lines (`2104` bytes)

**Classes:**
- `class TestFrozenTerms` - *A certificate cites an agreement's digest, so an issued agreement's text must never change.*
  - Method `.test_every_operative_agreement_pins_its_text()`
  - Method `.test_an_edited_agreement_is_refused_and_fails_verification()`
  - Method `.test_an_unpinned_agreement_still_yields_its_digest()`

---

### [`tests/test_metadata.py`](tests/test_metadata.py)
> *Unit tests for rendered certificate metadata validation (IDEA-090).*

**Size**: `53` lines (`2620` bytes)

**Classes:**
- `class TestMetadata`
  - Method `.test_normal_text_survives_and_whitespace_is_collapsed()`
  - Method `.test_angle_brackets_are_rejected()`
  - Method `.test_control_and_line_separator_characters_are_rejected()`
  - Method `.test_utf8_length_is_capped()`
  - Method `.test_cert_from_dict_rejects_unsafe_metadata()`
  - Method `.test_cert_from_dict_normalizes_project_and_allowance_spaces()`

---

### [`tests/test_register.py`](tests/test_register.py)
> *Unit tests for reading the public certificate register (ADR-013, ADR-017).*

**Size**: `135` lines (`6752` bytes)

**Classes:**
- `class TestRegister` - *The register is the public proof of issuance and revocation.*
  - Method `.setUp()`
  - Method `.issue(name)`
  - Method `.test_the_published_register_is_valid_and_holds_no_personal_data()`
  - Method `.test_registered_unregistered_and_revoked()`
  - Method `.test_a_listed_id_with_another_digest_is_unregistered()`
  - Method `.test_a_malformed_register_is_reported_not_raised()`
  - Method `.test_an_unknown_status_is_refused_not_treated_as_valid()`
  - Method `.test_a_non_text_digest_is_refused_instead_of_crashing_compare_digest()`
  - Method `.test_a_missing_register_is_empty()`
  - Method `.test_verifying_against_a_missing_register_is_an_error()`
- `class TestAllowances` - *ACL-1.0 exceptions are checked certificate data (ADR-014).*
  - Method `.test_allowances_verify_and_tampering_is_caught()`
  - Method `.test_a_self_consistent_unknown_allowance_is_invalid()`
  - Method `.test_allowances_given_as_a_string_are_one_allowance()`

---

### [`tests/test_verification_spec.py`](tests/test_verification_spec.py)
**Size**: `73` lines (`3098` bytes)

**Classes:**
- `class VerificationSpecTests`
  - Method `.setUp()`
  - Method `.test_vector_digest_matches_the_python_canonicalization()`
  - Method `.test_vector_pins_non_ascii_and_projects_sorting()`
  - Method `.test_ascii_escaping_matches_the_javascript_quote_function()`
  - Method `.test_numbers_are_safe_integers_in_both_runtimes()`
  - Method `.test_vector_is_not_an_issued_certificate()`
  - Method `.test_vector_uses_the_format_two_contract()`
  - Method `.test_spec_names_the_digest_and_the_vector()`

---

### [`tests/test_verifier.py`](tests/test_verifier.py)
> *Unit tests for commercial license certificate verifier.*

**Size**: `319` lines (`13298` bytes)

**Classes:**
- `class TestVerifier` - *Test certificate verification, tamper detection, terms, and scope checking.*
  - Method `.setUp()`
  - Method `.test_verify_valid_certificate_without_key_is_tamper_evident_only()`
  - Method `.test_verify_signed_certificate_with_key_is_authentic()`
  - Method `.test_self_issued_forgery_passes_digest_but_is_not_authentic()`
  - Method `.test_verify_from_json_file()`
  - Method `.test_a_utf8_bom_file_is_read()`
  - Method `.test_a_json_file_that_is_not_an_object_is_invalid_not_a_crash()`
  - Method `.test_verify_detects_tampered_digest()`
  - Method `.test_verify_detects_tampered_payload_field()`
  - Method `.test_verify_hmac_signature()`
  - Method `.test_verify_expired_certificate()`
  - Method `.test_verify_scope_filtering()`
  - Method `.test_unknown_license_type_is_rejected()`
  - Method `.test_terms_digest_mismatch_is_rejected()`
  - Method `.test_unknown_tier_is_rejected()`
  - Method `._payload(**overrides)`
  - Method `.test_perpetual_certificate_with_expiry_is_rejected()`
  - Method `.test_term_limited_certificate_without_expiry_is_rejected()`
  - Method `.test_malformed_field_types_are_invalid_not_a_crash()`
  - Method `.test_project_scope_check_with_mixed_project_types_does_not_crash()`
  - Method `.test_missing_projects_defaults_to_every_project()`
  - Method `.test_a_non_hyphenated_expiry_is_invalid()`
  - Method `.test_an_unknown_scope_is_invalid()`
- `class TestCertificateFormat` - *Only format-2 certificates, each with a random 256-bit serial, verify (ADR-018).*
  - Method `.test_a_fresh_certificate_is_format_2_with_a_serial()`
  - Method `.test_a_format_1_certificate_is_rejected_even_when_self_consistent()`
  - Method `.test_a_relabelled_format_1_certificate_is_tampered()`
  - Method `.test_a_bad_serial_is_invalid()`

---

### [`tests/test_workflow_assets.py`](tests/test_workflow_assets.py)
> *Asset tests for the CLA workflow, CI workflow, and packaging manifest.*

**Size**: `71` lines (`3398` bytes)

**Classes:**
- `class TestWorkflowAssets` - *Test the durable CLA register, workflow wiring, and manifest coverage.*
  - Method `.test_cla_register_is_valid_json()`
  - Method `.test_workflow_records_evidence_and_honours_revocation()`
  - Method `.test_cla_result_is_a_commit_status_the_comment_run_can_turn_green()`
  - Method `.test_ci_workflow_runs_tests_and_checks_the_wheel()`
  - Method `.test_manifest_covers_legal_documents()`

---
