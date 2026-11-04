"""Unit tests for the public verification command line."""

import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from aegean_licensing.cert import cert_to_dict
from aegean_licensing.cli import main
from tests.fixtures import day, issue_certificate, write_register


class TestCLI(unittest.TestCase):
    """The public CLI verifies; issuing and revoking are private (ADR-017)."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_cli_"))
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def write_cert(self, cert):
        path = self.temp_dir / f"license_certificate_{cert.cert_id}.json"
        path.write_text(json.dumps(cert_to_dict(cert)), encoding="utf-8")
        return path

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_version_output(self):
        with self.assertRaises(SystemExit) as caught, contextlib.redirect_stdout(io.StringIO()) as out:
            main(["--version"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn("aegean-license", out.getvalue())

    def test_only_verify_is_public(self):
        for command in ("issue", "revoke", "audit", "template"):
            with self.subTest(command=command), self.assertRaises(SystemExit), \
                    contextlib.redirect_stderr(io.StringIO()):
                main([command])

    def test_verify_against_the_register(self):
        cert = issue_certificate(licensee_name="Cli Corp", licensee_contact="c@example.com",
                                 allowances=["ai-training"])
        register = self.temp_dir / "issued.json"
        write_register(register, cert)
        code, out, _ = self.run_cli("verify", str(self.write_cert(cert)), "--register", str(register))
        self.assertEqual(code, 0)
        self.assertIn("Status : VALID", out)
        self.assertIn("Allow  : ai-training", out)

        write_register(register, cert, revoked={cert.cert_id})
        code, out, _ = self.run_cli("verify", str(self.write_cert(cert)), "--register", str(register))
        self.assertEqual(code, 1)
        self.assertIn("REVOKED", out)

    def test_as_of_reports_a_historical_key_compromise_as_valid(self):
        cert = issue_certificate(licensee_name="Historical Corp", licensee_contact="h@example.com",
                                 issued_at="2026-10-25")
        register = self.temp_dir / "issued.json"
        before = day(-5)
        write_register(register, cert, revoked={cert.cert_id},
                       reason_code="key-compromise", invalidity_date=day(0))
        path = self.write_cert(cert)
        code, out, _ = self.run_cli("verify", str(path), "--register", str(register))
        self.assertEqual(code, 1)
        self.assertIn("REVOKED", out)

        code, out, _ = self.run_cli("verify", str(path), "--register", str(register),
                                    "--as-of", before)
        self.assertEqual(code, 0)
        self.assertIn("Status : VALID_AS_OF", out)
        self.assertIn("historical, not a current authorization", out)
        self.assertIn(f"was valid as of {before}", out)

    def test_a_malformed_as_of_date_is_a_clean_error(self):
        cert = issue_certificate(licensee_name="As Of Corp", licensee_contact="a@example.com")
        register = self.temp_dir / "issued.json"
        write_register(register, cert)
        code, out, err = self.run_cli("verify", str(self.write_cert(cert)),
                                      "--register", str(register), "--as-of", "not-a-date")
        self.assertEqual(code, 1)
        self.assertIn("INVALID_FORMAT", out)
        self.assertIn("YYYY-MM-DD", out)
        self.assertEqual(err, "")

    def test_unregistered_certificate_fails_with_the_register(self):
        cert = issue_certificate(licensee_name="Forger", licensee_contact="f@example.com")
        register = self.temp_dir / "issued.json"
        write_register(register)
        code, out, _ = self.run_cli("verify", str(self.write_cert(cert)), "--register", str(register))
        self.assertEqual(code, 1)
        self.assertIn("UNREGISTERED", out)
        self.assertIn("not in the supplied register", out)

    def test_verify_without_register_reports_not_checked(self):
        cert = issue_certificate(licensee_name="NoReg", licensee_contact="n@example.com")
        code, out, _ = self.run_cli("verify", str(self.write_cert(cert)))
        self.assertEqual(code, 0)
        self.assertIn("not checked", out)

    def test_empty_register_path_is_a_usage_error(self):
        cert = issue_certificate(licensee_name="EmptyReg", licensee_contact="e@example.com")
        for empty in ("", "   "):
            with self.subTest(register=repr(empty)):
                code, out, err = self.run_cli("verify", str(self.write_cert(cert)),
                                              "--register", empty)
                self.assertEqual(code, 2)
                self.assertIn("--register requires a file path", err)

    def test_an_explicitly_missing_register_is_an_error(self):
        cert = issue_certificate(licensee_name="Missing", licensee_contact="m@example.com")
        missing = self.temp_dir / "absent.json"
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["verify", str(self.write_cert(cert)), "--register", str(missing)])
        self.assertEqual(code, 1)
        self.assertIn("register file not found", err.getvalue())
        self.assertNotIn("UNREGISTERED", out.getvalue())

    def test_the_public_cli_has_no_signing_key_option(self):
        # The HMAC check needs AegeanWorks' secret, so it lives in `aegean-ops verify` (ADR-018).
        for option in ("--key", "--key-file"):
            with self.subTest(option=option), self.assertRaises(SystemExit), \
                    contextlib.redirect_stderr(io.StringIO()):
                main(["verify", "cert.json", option, "x"])


if __name__ == "__main__":
    unittest.main()
