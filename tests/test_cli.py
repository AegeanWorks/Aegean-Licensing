"""Unit tests for aegean-licensing CLI."""

import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from aegean_licensing.cli import main


class TestCLI(unittest.TestCase):
    """Test CLI commands, argument handling, and exit codes."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_cli_")
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def test_version_output(self):
        buf = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buf
            with self.assertRaises(SystemExit) as cm:
                main(["--version"])
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("aegean-license", buf.getvalue())
        finally:
            sys.stdout = old_stdout

    def test_issue_and_verify_roundtrip_cli(self):
        # 1. Issue certificate to temp_dir
        exit_code = main([
            "issue",
            "--licensee", "Alpha Tech",
            "--contact", "alpha@tech.io",
            "--projects", "chronos,AIKit",
            "--output-dir", self.temp_dir,
        ])
        self.assertEqual(exit_code, 0)

        # Locate generated JSON
        json_files = list(Path(self.temp_dir).glob("*.json"))
        self.assertEqual(len(json_files), 1)
        cert_path = str(json_files[0])

        # 2. Verify certificate
        exit_code = main(["verify", cert_path])
        self.assertEqual(exit_code, 0)

        # 3. Verify scope check (chronos -> OK, other -> fail)
        exit_code_ok = main(["verify", cert_path, "--project", "chronos"])
        self.assertEqual(exit_code_ok, 0)

        exit_code_bad = main(["verify", cert_path, "--project", "unlicensed-project"])
        self.assertEqual(exit_code_bad, 1)

    def test_template_generation_cli(self):
        exit_code = main(["template", "all", "--output-dir", self.temp_dir])
        self.assertEqual(exit_code, 0)
        self.assertTrue((Path(self.temp_dir) / "DUAL_LICENSE_NOTICE.txt").exists())
        self.assertTrue((Path(self.temp_dir) / "COMMERCIAL.md").exists())
        self.assertTrue((Path(self.temp_dir) / "pyproject_snippet.toml").exists())


if __name__ == "__main__":
    unittest.main()
