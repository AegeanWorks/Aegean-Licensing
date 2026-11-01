"""Unit tests for reading the public certificate register (ADR-013, ADR-017)."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from aegean_licensing.cert import cert_from_dict, cert_to_dict, compute_digest
from aegean_licensing.register import load_register, load_register_document
from aegean_licensing.verifier import verify_certificate
from tests.fixtures import day, issue_certificate, moment, write_register

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
        self.assertEqual(data["version"], 2)
        self.assertRegex(data["generated_at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertRegex(data["next_update"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
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

    def test_verifying_against_a_missing_register_is_an_error(self):
        # load_register() returns {} so a writer can create a register; a verifier that was given
        # a path must not treat a mistyped path as an empty register and call every id unregistered.
        result = verify_certificate(
            cert_to_dict(self.issue()), register_path=self.temp_dir / "absent.json"
        )
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "INVALID_FORMAT")
        self.assertIn("does not exist", result.reasons[0])


class TestRegisterVersionTwo(unittest.TestCase):
    """Freshness, typed revocation and as-of behavior (IDEA-935, IDEA-948)."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_register_v2_"))
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)
        self.register = self.temp_dir / "issued.json"

    def issue(self, name="Register V2 Corp"):
        return issue_certificate(licensee_name=name, licensee_contact="legal@register.example",
                                 issued_at="2026-10-25")

    def test_a_stale_register_is_refused(self):
        cert = self.issue()
        write_register(self.register, cert, generated_at="2026-01-01T00:00:00Z",
                       next_update="2026-01-02T00:00:00Z")
        result = verify_certificate(cert_to_dict(cert), register_path=self.register)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "STALE_REGISTER")
        self.assertIn("freshness window", result.reasons[0])

    def test_a_version_one_register_is_undated(self):
        cert = self.issue()
        self.register.write_text(json.dumps({
            "version": 1,
            "certificates": {cert.cert_id: {
                "digest": cert.digest, "license_type": cert.license_type,
                "issued_at": cert.issued_at, "status": "valid"}}}), encoding="utf-8")
        result = verify_certificate(cert_to_dict(cert), register_path=self.register)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "UNDATED_REGISTER")

    def test_a_future_generated_at_is_refused(self):
        cert = self.issue()
        write_register(self.register, cert, generated_at=moment(1),
                       next_update=moment(30))
        result = verify_certificate(cert_to_dict(cert), register_path=self.register)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "STALE_REGISTER")

    def test_version_two_requires_freshness_metadata(self):
        cert = self.issue()
        self.register.write_text(json.dumps({
            "version": 2,
            "certificates": {cert.cert_id: {
                "digest": cert.digest, "license_type": cert.license_type,
                "issued_at": cert.issued_at, "status": "valid"}}}), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            load_register_document(self.register)
        self.assertIn("generated_at/next_update", str(caught.exception))

    def test_freshness_window_is_bounded(self):
        cert = self.issue()
        write_register(self.register, cert, generated_at="2020-01-01T00:00:00Z",
                       next_update="2026-01-01T00:00:00Z")
        with self.assertRaises(ValueError) as caught:
            load_register_document(self.register)
        self.assertIn("longer than", str(caught.exception))

    def test_version_one_rejects_version_two_entry_fields(self):
        cert = self.issue()
        self.register.write_text(json.dumps({
            "version": 1,
            "certificates": {cert.cert_id: {
                "digest": cert.digest, "license_type": cert.license_type,
                "issued_at": cert.issued_at, "status": "revoked",
                "revoked_at": "2026-11-01", "reason_code": "other"}}}), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            load_register_document(self.register)
        self.assertIn("version-2 fields", str(caught.exception))

    def test_an_unknown_reason_code_is_refused(self):
        cert = self.issue()
        write_register(self.register, cert, revoked={cert.cert_id}, reason_code="because")
        with self.assertRaises(ValueError) as caught:
            load_register_document(self.register)
        self.assertIn("unknown reason_code", str(caught.exception))

    def test_invalidity_date_requires_a_retroactive_code(self):
        cert = self.issue()
        write_register(self.register, cert, revoked={cert.cert_id},
                       reason_code="non-payment", invalidity_date="2026-10-01")
        with self.assertRaises(ValueError) as caught:
            load_register_document(self.register)
        self.assertIn("non-retroactive", str(caught.exception))

    def test_invalidity_date_cannot_be_after_revocation(self):
        cert = self.issue()
        write_register(self.register, cert, revoked={cert.cert_id},
                       reason_code="key-compromise", invalidity_date=day(1))
        with self.assertRaises(ValueError) as caught:
            load_register_document(self.register)
        self.assertIn("after revoked_at", str(caught.exception))

    def test_key_compromise_is_valid_as_of_before_the_effective_date(self):
        cert = self.issue()
        before, after = day(-5), day(1)
        write_register(self.register, cert, revoked={cert.cert_id},
                       reason_code="key-compromise", invalidity_date=day(0))
        current = verify_certificate(cert_to_dict(cert), register_path=self.register)
        self.assertEqual(current.status, "REVOKED")
        historical = verify_certificate(cert_to_dict(cert), register_path=self.register,
                                        as_of=before)
        self.assertTrue(historical.is_valid)
        self.assertEqual(historical.status, "VALID_AS_OF")
        self.assertTrue(historical.historical)
        self.assertIn(f"was valid on {before}", historical.reasons[0])
        after_result = verify_certificate(cert_to_dict(cert), register_path=self.register,
                                          as_of=after)
        self.assertEqual(after_result.status, "REVOKED")

    def test_a_non_retroactive_revocation_is_revoked_as_of_any_date(self):
        cert = self.issue()
        write_register(self.register, cert, revoked={cert.cert_id},
                       reason_code="non-payment")
        result = verify_certificate(cert_to_dict(cert), register_path=self.register,
                                    as_of="2026-10-26")
        self.assertEqual(result.status, "REVOKED")

    def test_as_of_before_issuance_is_not_yet_issued(self):
        cert = self.issue()
        write_register(self.register, cert)
        result = verify_certificate(cert_to_dict(cert), register_path=self.register,
                                    as_of="2026-10-01")
        self.assertEqual(result.status, "NOT_YET_ISSUED")
        self.assertFalse(result.is_valid)

    def test_as_of_and_reference_date_are_exclusive(self):
        with self.assertRaises(ValueError):
            verify_certificate(cert_to_dict(self.issue()), as_of="2026-10-26",
                               reference_date="2026-10-26")

    def test_a_historical_question_is_judged_against_todays_register_not_the_asked_date(self):
        # Freshness asks whether the register file is current, not whether it existed on the
        # queried date. Judging it at `as_of` rejected every question about a date before the
        # register was generated as STALE_REGISTER, even though a newer register is better
        # evidence for an older date.
        cert = self.issue()
        write_register(self.register, cert, revoked={cert.cert_id},
                       reason_code="key-compromise", invalidity_date=day(0))
        result = verify_certificate(cert_to_dict(cert), register_path=self.register,
                                    as_of=day(-5))
        self.assertEqual(result.status, "VALID_AS_OF")
        self.assertTrue(result.is_valid)

    def test_a_stale_register_still_refuses_a_historical_question(self):
        # The fix above must not turn the freshness gate off for historical checks.
        cert = self.issue()
        write_register(self.register, cert, generated_at=moment(-90),
                       next_update=moment(-60))
        result = verify_certificate(cert_to_dict(cert), register_path=self.register,
                                    as_of=day(-5))
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "STALE_REGISTER")


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
