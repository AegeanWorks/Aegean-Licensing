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
from tests.fixtures import issue_certificate, write_register


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

    def test_unregistered_certificate_fails_with_the_register(self):
        cert = issue_certificate(licensee_name="Forger", licensee_contact="f@example.com")
        register = self.temp_dir / "issued.json"
        write_register(register)
        code, out, _ = self.run_cli("verify", str(self.write_cert(cert)), "--register", str(register))
        self.assertEqual(code, 1)
        self.assertIn("UNREGISTERED", out)

    def test_the_public_cli_has_no_signing_key_option(self):
        # The HMAC check needs AegeanWorks' secret, so it lives in `aegean-ops verify` (ADR-018).
        for option in ("--key", "--key-file"):
            with self.subTest(option=option), self.assertRaises(SystemExit), \
                    contextlib.redirect_stderr(io.StringIO()):
                main(["verify", "cert.json", option, "x"])


if __name__ == "__main__":
    unittest.main()
