"""Unit tests for commercial license certificate verifier."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from aegean_licensing.cert import cert_to_dict, compute_digest
from tests.fixtures import issue_certificate
from aegean_licensing.verifier import verify_certificate


class TestVerifier(unittest.TestCase):
    """Test certificate verification, tamper detection, terms, and scope checking."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_verifier_")
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def test_verify_valid_certificate_without_key_is_tamper_evident_only(self):
        cert = issue_certificate(
            licensee_name="Valid Enterprise",
            licensee_contact="legal@enterprise.com",
            projects=["AIKit", "chronos"],
        )
        res = verify_certificate(cert_to_dict(cert))
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, "VALID_UNVERIFIED")
        self.assertFalse(res.signature_verified)
        self.assertTrue(res.terms_verified)

    def test_verify_signed_certificate_with_key_is_authentic(self):
        cert = issue_certificate(
            licensee_name="Signed Enterprise",
            licensee_contact="legal@signed.example",
            secret_key="verify-key",
        )
        res = verify_certificate(cert_to_dict(cert), secret_key="verify-key")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, "VALID")
        self.assertTrue(res.signature_verified)
        self.assertTrue(res.terms_verified)

    def test_self_issued_forgery_passes_digest_but_is_not_authentic(self):
        forged = {
            "cert_id": "forged-1",
            "licensee_name": "Forged Corp",
            "licensee_contact": "forged@example.com",
            "issuer": "AegeanWorks",
            "issuer_contact": "aegean-licensing@proton.me",
            "license_type": "ACL-1.0",
            "projects": ["chronos"],
            "scope": "proprietary-saas-and-redistribution",
            "issued_at": "2026-10-25",
            "expires_at": None,
            "is_perpetual": True,
            "notes": "",
            "tier": "",
            "terms_digest": "",
            "licensee_address": "",
            "licensee_registration": "",
            "licensee_country": "",
            "format": 2,
            "serial": "f" * 64,
            "signature": "",
        }
        forged["digest"] = compute_digest(forged)
        res = verify_certificate(forged)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, "VALID_UNVERIFIED")
        self.assertFalse(res.signature_verified)

    def test_verify_from_json_file(self):
        cert = issue_certificate(
            licensee_name="File Corp",
            licensee_contact="dev@filecorp.com",
            cert_id="file-cert-001",
        )
        cert_file = Path(self.temp_dir) / "license_certificate_file-cert-001.json"
        cert_file.write_text(json.dumps(cert_to_dict(cert)), encoding="utf-8")
        res = verify_certificate(cert_file)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, "VALID_UNVERIFIED")

    def test_a_json_file_that_is_not_an_object_is_invalid_not_a_crash(self):
        # A JSON array used to reach data.get("format") and raise AttributeError, so a malformed
        # file crashed the verifier instead of reporting INVALID_FORMAT.
        for body in ("[]", '"a string"', "42", "null"):
            with self.subTest(body=body):
                path = Path(self.temp_dir) / "not-an-object.json"
                path.write_text(body, encoding="utf-8")
                result = verify_certificate(path)
                self.assertFalse(result.is_valid)
                self.assertEqual(result.status, "INVALID_FORMAT")
                self.assertIn("object", result.reasons[0])

    def test_verify_detects_tampered_digest(self):
        cert = issue_certificate(licensee_name="Tamper Corp", licensee_contact="bad@tamper.com")
        data = cert_to_dict(cert)
        data["digest"] = "fake-tampered-digest-00000000000000000000000000000000000000000000000"
        res = verify_certificate(data)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "TAMPERED")

    def test_verify_detects_tampered_payload_field(self):
        cert = issue_certificate(licensee_name="Legit Corp", licensee_contact="good@legit.com")
        data = cert_to_dict(cert)
        data["licensee_name"] = "Hacker Corp"
        res = verify_certificate(data)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "TAMPERED")

    def test_verify_hmac_signature(self):
        cert = issue_certificate(
            licensee_name="Hmac Corp",
            licensee_contact="hmac@corp.com",
            secret_key="top-secret",
        )
        data = cert_to_dict(cert)
        res_ok = verify_certificate(data, secret_key="top-secret")
        self.assertTrue(res_ok.is_valid)
        self.assertEqual(res_ok.status, "VALID")

        res_fail = verify_certificate(data, secret_key="wrong-secret")
        self.assertFalse(res_fail.is_valid)
        self.assertEqual(res_fail.status, "TAMPERED")

    def test_verify_expired_certificate(self):
        cert = issue_certificate(
            licensee_name="Past Corp",
            licensee_contact="past@corp.com",
            is_perpetual=False,
            expires_at="2025-01-01",
        )
        res = verify_certificate(cert_to_dict(cert), reference_date="2026-10-25")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "EXPIRED")

    def test_verify_scope_filtering(self):
        cert = issue_certificate(
            licensee_name="Scoped Corp",
            licensee_contact="scoped@corp.com",
            projects=["chronos"],
        )
        data = cert_to_dict(cert)
        res_covered = verify_certificate(data, check_project="chronos")
        self.assertTrue(res_covered.is_valid)

        res_uncovered = verify_certificate(data, check_project="cyberpulse")
        self.assertFalse(res_uncovered.is_valid)
        self.assertEqual(res_uncovered.status, "SCOPE_MISMATCH")

    def test_unknown_license_type_is_rejected(self):
        cert = issue_certificate(licensee_name="Type Corp", licensee_contact="type@corp.com")
        data = cert_to_dict(cert)
        data["license_type"] = "ACLA-1.0-Tier1"
        data["digest"] = compute_digest(data)
        res = verify_certificate(data)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "INVALID_FORMAT")

    def test_terms_digest_mismatch_is_rejected(self):
        cert = issue_certificate(licensee_name="Terms Corp", licensee_contact="terms@corp.com")
        data = cert_to_dict(cert)
        data["terms_digest"] = "0" * 64
        data["digest"] = compute_digest(data)
        res = verify_certificate(data)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "INVALID_FORMAT")

    def test_unknown_tier_is_rejected(self):
        cert = issue_certificate(
            licensee_name="Tier Corp",
            licensee_contact="tier@corp.com",
            tier="Tier1",
        )
        data = cert_to_dict(cert)
        data["tier"] = "Gold"
        data["digest"] = compute_digest(data)
        res = verify_certificate(data)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "INVALID_FORMAT")

    def _payload(self, **overrides):
        data = {
            "cert_id": "inconsistent-cert",
            "licensee_name": "Inconsistent Corp",
            "licensee_contact": "legal@inconsistent.example",
            "issuer": "AegeanWorks",
            "issuer_contact": "aegean-licensing@proton.me",
            "license_type": "ACL-1.0",
            "projects": ["chronos"],
            "scope": "proprietary-saas-and-redistribution",
            "issued_at": "2026-10-25",
            "expires_at": None,
            "is_perpetual": True,
            "notes": "",
            "format": 2,
            "serial": "e" * 64,
        }
        data.update(overrides)
        data["digest"] = compute_digest(data)
        data["signature"] = ""
        return data

    def test_perpetual_certificate_with_expiry_is_rejected(self):
        data = self._payload(is_perpetual=True, expires_at="2030-01-01")
        res = verify_certificate(data)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "INVALID_FORMAT")

    def test_term_limited_certificate_without_expiry_is_rejected(self):
        data = self._payload(is_perpetual=False, expires_at=None)
        res = verify_certificate(data)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "INVALID_FORMAT")

    def test_malformed_field_types_are_invalid_not_a_crash(self):
        cases = {
            "projects": [1, 2],
            "allowances": 5,
            "expires_at": ["2027-01-01"],
            "is_perpetual": "false",
            "license_type": "",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                data = self._payload()
                data[field] = value
                data["digest"] = "0" * 64
                data["signature"] = ""
                result = verify_certificate(data)
                self.assertFalse(result.is_valid)
                self.assertEqual(result.status, "INVALID_FORMAT")
                self.assertTrue(result.reasons)

    def test_project_scope_check_with_mixed_project_types_does_not_crash(self):
        data = self._payload()
        data["projects"] = ["*", 7]
        data["digest"] = "0" * 64
        data["signature"] = ""
        result = verify_certificate(data, check_project="NeuroCore")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "INVALID_FORMAT")

    def test_missing_projects_defaults_to_every_project(self):
        data = self._payload()
        data.pop("projects", None)
        data["digest"] = compute_digest(data)
        data["signature"] = ""
        result = verify_certificate(data, check_project="NeuroCore")
        self.assertTrue(result.is_valid, result.reasons)

    def test_a_non_hyphenated_expiry_is_invalid(self):
        data = self._payload(is_perpetual=False, expires_at="20260101")
        data["digest"] = compute_digest(data)
        data["signature"] = ""
        result = verify_certificate(data)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "INVALID_FORMAT")


class TestCertificateFormat(unittest.TestCase):
    """Only format-2 certificates, each with a random 256-bit serial, verify (ADR-018)."""

    def test_a_fresh_certificate_is_format_2_with_a_serial(self):
        cert = issue_certificate(licensee_name="Format", licensee_contact="f@example.com")
        self.assertEqual(cert.format, 2)
        self.assertRegex(cert.serial, r"^[0-9a-f]{64}$")
        self.assertTrue(verify_certificate(cert_to_dict(cert)).is_valid)

    def test_a_format_1_certificate_is_rejected_even_when_self_consistent(self):
        # What the issuer published before ADR-018 produced: no format, no serial, plain digest.
        import hashlib
        from aegean_licensing.cert import compute_canonical_payload
        data = cert_to_dict(issue_certificate(licensee_name="Old", licensee_contact="o@example.com"))
        del data["format"], data["serial"]
        data["digest"] = hashlib.sha256(compute_canonical_payload(data)).hexdigest()
        result = verify_certificate(data)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "UNSUPPORTED_FORMAT")

    def test_a_relabelled_format_1_certificate_is_tampered(self):
        data = cert_to_dict(issue_certificate(licensee_name="Old", licensee_contact="o@example.com"))
        data["format"] = 1
        self.assertEqual(verify_certificate(data).status, "UNSUPPORTED_FORMAT")

    def test_a_bad_serial_is_invalid(self):
        for serial in ("", "1234", "Z" * 64):
            with self.subTest(serial=serial):
                data = cert_to_dict(issue_certificate(licensee_name="S", licensee_contact="s@example.com"))
                data["serial"] = serial
                data["digest"] = compute_digest(data)
                self.assertEqual(verify_certificate(data).status, "INVALID_FORMAT")


if __name__ == "__main__":
    unittest.main()
