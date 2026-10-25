"""Unit tests for reading the public certificate register (ADR-013, ADR-017)."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from aegean_licensing.cert import cert_from_dict, cert_to_dict, compute_digest
from aegean_licensing.register import load_register
from aegean_licensing.verifier import verify_certificate
from tests.fixtures import issue_certificate, write_register

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestRegister(unittest.TestCase):
    """The register is the public proof of issuance and revocation."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_register_"))
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)
        self.register = self.temp_dir / "issued.json"

    def issue(self, name="Register Corp"):
        return issue_certificate(licensee_name=name, licensee_contact="legal@register.example")

    def test_the_published_register_is_valid_and_holds_no_personal_data(self):
        path = REPO_ROOT / "licenses" / "issued.json"
        load_register(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data["certificates"].values():
            self.assertEqual(sorted(entry), ["digest", "issued_at", "license_type", "reason",
                                             "revoked_at", "status"])

    def test_registered_unregistered_and_revoked(self):
        cert = self.issue()
        write_register(self.register, cert)
        registered = verify_certificate(cert_to_dict(cert), register_path=self.register)
        self.assertTrue(registered.is_valid)
        self.assertEqual(registered.status, "VALID")
        self.assertTrue(registered.registered)

        unknown = verify_certificate(cert_to_dict(self.issue("Forger")), register_path=self.register)
        self.assertEqual(unknown.status, "UNREGISTERED")

        write_register(self.register, cert, revoked={cert.cert_id})
        revoked = verify_certificate(cert_to_dict(cert), register_path=self.register)
        self.assertEqual(revoked.status, "REVOKED")
        self.assertTrue(any("terminated for breach" in r for r in revoked.reasons))

    def test_a_listed_id_with_another_digest_is_unregistered(self):
        cert = self.issue()
        other = issue_certificate(licensee_name="Other", licensee_contact="o@example.com",
                                  cert_id=cert.cert_id)
        write_register(self.register, other)
        self.assertEqual(verify_certificate(cert_to_dict(cert), register_path=self.register).status,
                         "UNREGISTERED")

    def test_a_malformed_register_is_reported_not_raised(self):
        self.register.write_text(json.dumps({"version": 1, "certificates": {"x": {"oops": 1}}}),
                                 encoding="utf-8")
        with self.assertRaises(ValueError):
            load_register(self.register)
        result = verify_certificate(cert_to_dict(self.issue()), register_path=self.register)
        self.assertEqual(result.status, "INVALID_FORMAT")

    def test_an_unknown_status_is_refused_not_treated_as_valid(self):
        # A register status the package does not know used to fall through as valid, so a
        # mistyped revocation ("revoked " or "suspended") would not stop a certificate.
        cert = self.issue()
        write_register(self.register, cert)
        data = json.loads(self.register.read_text(encoding="utf-8"))
        data["certificates"][cert.cert_id]["status"] = "revoked "
        self.register.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            load_register(self.register)
        self.assertIn("unknown status", str(caught.exception))
        result = verify_certificate(cert_to_dict(cert), register_path=self.register)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "INVALID_FORMAT")

    def test_a_non_text_digest_is_refused_instead_of_crashing_compare_digest(self):
        # hmac.compare_digest(7, "...") raises TypeError, which used to escape `verify`.
        cert = self.issue()
        write_register(self.register, cert)
        data = json.loads(self.register.read_text(encoding="utf-8"))
        data["certificates"][cert.cert_id]["digest"] = 7
        self.register.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            load_register(self.register)
        self.assertIn("invalid digest", str(caught.exception))
        result = verify_certificate(cert_to_dict(cert), register_path=self.register)
        self.assertEqual(result.status, "INVALID_FORMAT")

    def test_a_missing_register_is_empty(self):
        self.assertEqual(load_register(self.temp_dir / "absent.json"), {})


class TestAllowances(unittest.TestCase):
    """ACL-1.0 exceptions are checked certificate data (ADR-014)."""

    def test_allowances_verify_and_tampering_is_caught(self):
        cert = issue_certificate(licensee_name="Allow", licensee_contact="a@example.com",
                                 allowances=["hosted-service", "ai-training"])
        self.assertEqual(cert.allowances, ("ai-training", "hosted-service"))
        self.assertTrue(verify_certificate(cert_to_dict(cert)).is_valid)
        data = cert_to_dict(issue_certificate(licensee_name="A", licensee_contact="a@example.com"))
        data["allowances"] = ["ai-training"]
        self.assertEqual(verify_certificate(data).status, "TAMPERED")

    def test_a_self_consistent_unknown_allowance_is_invalid(self):
        data = cert_to_dict(issue_certificate(licensee_name="A", licensee_contact="a@example.com"))
        data["allowances"] = ["resell-everything"]
        data["digest"] = compute_digest(data)
        self.assertEqual(verify_certificate(data).status, "INVALID_FORMAT")

    def test_allowances_given_as_a_string_are_one_allowance(self):
        data = cert_to_dict(issue_certificate(licensee_name="S", licensee_contact="s@example.com"))
        data["allowances"] = "ai-training"
        self.assertEqual(cert_from_dict(data).allowances, ("ai-training",))


if __name__ == "__main__":
    unittest.main()
