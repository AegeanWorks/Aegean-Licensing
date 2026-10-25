"""Unit tests for commercial license certificate verifier."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from aegean_licensing.issuer import issue_certificate
from aegean_licensing.verifier import verify_certificate


class TestVerifier(unittest.TestCase):
    """Test certificate verification, tamper detection, and scope checking."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_verifier_")
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def test_verify_valid_certificate(self):
        cert = issue_certificate(
            licensee_name="Valid Enterprise",
            licensee_contact="legal@enterprise.com",
            projects=["AIKit", "chronos"],
        )
        res = verify_certificate(
            target={
                "cert_id": cert.cert_id,
                "licensee_name": cert.licensee_name,
                "licensee_contact": cert.licensee_contact,
                "issuer": cert.issuer,
                "issuer_contact": cert.issuer_contact,
                "license_type": cert.license_type,
                "projects": list(cert.projects),
                "scope": cert.scope,
                "issued_at": cert.issued_at,
                "expires_at": cert.expires_at,
                "is_perpetual": cert.is_perpetual,
                "notes": cert.notes,
                "digest": cert.digest,
                "signature": cert.signature,
            }
        )
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, "VALID")

    def test_verify_from_json_file(self):
        cert = issue_certificate(
            licensee_name="File Corp",
            licensee_contact="dev@filecorp.com",
            cert_id="file-cert-001",
            output_dir=self.temp_dir,
        )
        cert_file = Path(self.temp_dir) / "license_certificate_file-cert-001.json"
        res = verify_certificate(cert_file)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, "VALID")

    def test_verify_detects_tampered_digest(self):
        cert = issue_certificate(
            licensee_name="Tamper Corp",
            licensee_contact="bad@tamper.com",
        )
        data = {
            "cert_id": cert.cert_id,
            "licensee_name": cert.licensee_name,
            "licensee_contact": cert.licensee_contact,
            "issuer": cert.issuer,
            "issuer_contact": cert.issuer_contact,
            "license_type": cert.license_type,
            "projects": list(cert.projects),
            "scope": cert.scope,
            "issued_at": cert.issued_at,
            "expires_at": cert.expires_at,
            "is_perpetual": cert.is_perpetual,
            "notes": cert.notes,
            "digest": "fake-tampered-digest-00000000000000000000000000000000000000000000000",
            "signature": cert.signature,
        }
        res = verify_certificate(data)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "TAMPERED")

    def test_verify_detects_tampered_payload_field(self):
        cert = issue_certificate(
            licensee_name="Legit Corp",
            licensee_contact="good@legit.com",
        )
        # Change the licensee name but keep the original digest
        data = {
            "cert_id": cert.cert_id,
            "licensee_name": "Hacker Corp",
            "licensee_contact": cert.licensee_contact,
            "issuer": cert.issuer,
            "issuer_contact": cert.issuer_contact,
            "license_type": cert.license_type,
            "projects": list(cert.projects),
            "scope": cert.scope,
            "issued_at": cert.issued_at,
            "expires_at": cert.expires_at,
            "is_perpetual": cert.is_perpetual,
            "notes": cert.notes,
            "digest": cert.digest,
            "signature": cert.signature,
        }
        res = verify_certificate(data)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "TAMPERED")

    def test_verify_hmac_signature(self):
        cert = issue_certificate(
            licensee_name="Hmac Corp",
            licensee_contact="hmac@corp.com",
            secret_key="top-secret",
        )
        data = {
            "cert_id": cert.cert_id,
            "licensee_name": cert.licensee_name,
            "licensee_contact": cert.licensee_contact,
            "issuer": cert.issuer,
            "issuer_contact": cert.issuer_contact,
            "license_type": cert.license_type,
            "projects": list(cert.projects),
            "scope": cert.scope,
            "issued_at": cert.issued_at,
            "expires_at": cert.expires_at,
            "is_perpetual": cert.is_perpetual,
            "notes": cert.notes,
            "digest": cert.digest,
            "signature": cert.signature,
        }
        # Correct key
        res_ok = verify_certificate(data, secret_key="top-secret")
        self.assertTrue(res_ok.is_valid)

        # Wrong key
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
        data = {
            "cert_id": cert.cert_id,
            "licensee_name": cert.licensee_name,
            "licensee_contact": cert.licensee_contact,
            "issuer": cert.issuer,
            "issuer_contact": cert.issuer_contact,
            "license_type": cert.license_type,
            "projects": list(cert.projects),
            "scope": cert.scope,
            "issued_at": cert.issued_at,
            "expires_at": cert.expires_at,
            "is_perpetual": cert.is_perpetual,
            "notes": cert.notes,
            "digest": cert.digest,
            "signature": cert.signature,
        }
        res = verify_certificate(data, reference_date="2026-10-25")
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, "EXPIRED")

    def test_verify_scope_filtering(self):
        cert = issue_certificate(
            licensee_name="Scoped Corp",
            licensee_contact="scoped@corp.com",
            projects=["chronos"],
        )
        data = {
            "cert_id": cert.cert_id,
            "licensee_name": cert.licensee_name,
            "licensee_contact": cert.licensee_contact,
            "issuer": cert.issuer,
            "issuer_contact": cert.issuer_contact,
            "license_type": cert.license_type,
            "projects": list(cert.projects),
            "scope": cert.scope,
            "issued_at": cert.issued_at,
            "expires_at": cert.expires_at,
            "is_perpetual": cert.is_perpetual,
            "notes": cert.notes,
            "digest": cert.digest,
            "signature": cert.signature,
        }
        res_covered = verify_certificate(data, check_project="chronos")
        self.assertTrue(res_covered.is_valid)

        res_uncovered = verify_certificate(data, check_project="cyberpulse")
        self.assertFalse(res_uncovered.is_valid)
        self.assertEqual(res_uncovered.status, "SCOPE_MISMATCH")


if __name__ == "__main__":
    unittest.main()
