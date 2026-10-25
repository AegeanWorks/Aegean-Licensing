"""Unit tests for commercial license certificate issuer."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from aegean_licensing.issuer import issue_certificate


class TestIssuer(unittest.TestCase):
    """Test certificate creation and disk serialization."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_issuer_")
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def test_issue_valid_perpetual_certificate(self):
        cert = issue_certificate(
            licensee_name="Nexus Technologies",
            licensee_contact="ops@nexustech.io",
            projects=["chronos", "cyberpulse"],
            scope="closed-source-saas",
        )
        self.assertEqual(cert.licensee_name, "Nexus Technologies")
        self.assertEqual(cert.licensee_contact, "ops@nexustech.io")
        self.assertIn("chronos", cert.projects)
        self.assertIn("cyberpulse", cert.projects)
        self.assertTrue(cert.is_perpetual)
        self.assertIsNotNone(cert.digest)
        self.assertEqual(len(cert.digest), 64)
        self.assertEqual(cert.signature, "")

    def test_issue_with_hmac_signature(self):
        cert = issue_certificate(
            licensee_name="Secure Co",
            licensee_contact="admin@secure.co",
            secret_key="my-master-signing-key",
        )
        self.assertNotEqual(cert.signature, "")
        self.assertEqual(len(cert.signature), 64)

    def test_validation_errors(self):
        with self.assertRaises(ValueError):
            issue_certificate(licensee_name="", licensee_contact="test@example.com")
        with self.assertRaises(ValueError):
            issue_certificate(licensee_name="Valid", licensee_contact="   ")

    def test_issue_writes_atomic_files(self):
        cert = issue_certificate(
            licensee_name="Disk Corp",
            licensee_contact="disk@corp.com",
            cert_id="custom-uuid-1",
            output_dir=self.temp_dir,
        )
        json_path = Path(self.temp_dir) / "license_certificate_custom-uuid-1.json"
        md_path = Path(self.temp_dir) / "license_certificate_custom-uuid-1.md"

        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["cert_id"], "custom-uuid-1")
        self.assertEqual(data["licensee_name"], "Disk Corp")
        self.assertEqual(data["digest"], cert.digest)


if __name__ == "__main__":
    unittest.main()
