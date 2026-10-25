"""Unit tests for repository compliance auditor."""

import shutil
import tempfile
import unittest
from pathlib import Path

from aegean_licensing.auditor import audit_repository
from aegean_licensing.templates import (
    get_commercial_md,
    get_dual_license_rider,
    get_pyproject_snippet,
)


class TestAuditor(unittest.TestCase):
    """Test repository licensing audit checks and warnings."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_auditor_")
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)
        self.root = Path(self.temp_dir)

    def test_compliant_repository(self):
        # Create compliant LICENSE
        license_path = self.root / "LICENSE"
        with open(license_path, "w", encoding="utf-8") as f:
            f.write("GNU AFFERO GENERAL PUBLIC LICENSE\nVersion 3\n\n" + get_dual_license_rider())

        # Create compliant COMMERCIAL.md
        comm_path = self.root / "COMMERCIAL.md"
        with open(comm_path, "w", encoding="utf-8") as f:
            f.write(get_commercial_md())

        # Create compliant pyproject.toml
        pyproj_path = self.root / "pyproject.toml"
        with open(pyproj_path, "w", encoding="utf-8") as f:
            f.write(get_pyproject_snippet())

        report = audit_repository(self.root)
        self.assertTrue(report.is_compliant)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.warnings), 0)

    def test_missing_license_fails(self):
        comm_path = self.root / "COMMERCIAL.md"
        with open(comm_path, "w", encoding="utf-8") as f:
            f.write(get_commercial_md())

        report = audit_repository(self.root)
        self.assertFalse(report.is_compliant)
        self.assertTrue(any("Missing LICENSE" in f for f in report.failed_checks))

    def test_missing_commercial_md_fails(self):
        license_path = self.root / "LICENSE"
        with open(license_path, "w", encoding="utf-8") as f:
            f.write("GNU AFFERO GENERAL PUBLIC LICENSE\n\n" + get_dual_license_rider())

        report = audit_repository(self.root)
        self.assertFalse(report.is_compliant)
        self.assertTrue(any("Missing COMMERCIAL.md" in f for f in report.failed_checks))

    def test_detects_obsolete_enterprise_bureaucracy(self):
        license_path = self.root / "LICENSE"
        with open(license_path, "w", encoding="utf-8") as f:
            f.write("GNU AFFERO GENERAL PUBLIC LICENSE\n\n" + get_dual_license_rider())

        comm_path = self.root / "COMMERCIAL.md"
        with open(comm_path, "w", encoding="utf-8") as f:
            f.write(get_commercial_md() + "\nContact us for W-9 and Net-30 invoicing forms.\n")

        report = audit_repository(self.root)
        self.assertTrue(any("obsolete enterprise bureaucracy" in w for w in report.warnings))

    def test_alpu_compliant_repository(self):
        license_path = self.root / "LICENSE"
        with open(license_path, "w", encoding="utf-8") as f:
            f.write("# Aegean Licensing Personal Use License (AL-PU)\nContact: aegean-licensing@proton.me\n")

        comm_path = self.root / "COMMERCIAL.md"
        with open(comm_path, "w", encoding="utf-8") as f:
            f.write(get_commercial_md())

        report = audit_repository(self.root)
        self.assertTrue(report.is_compliant)
        self.assertTrue(any("AL-PU" in p for p in report.passed_checks))

    def test_audit_with_policies_check(self):
        license_path = self.root / "LICENSE"
        with open(license_path, "w", encoding="utf-8") as f:
            f.write("GNU AFFERO GENERAL PUBLIC LICENSE\n\n" + get_dual_license_rider())

        comm_path = self.root / "COMMERCIAL.md"
        with open(comm_path, "w", encoding="utf-8") as f:
            f.write(get_commercial_md())

        # Without policies files, warnings are generated
        report = audit_repository(self.root, check_policies=True)
        self.assertTrue(report.is_compliant)
        self.assertTrue(any("Missing Contributor License Agreement" in w for w in report.warnings))

        # Create policies
        lic_dir = self.root / "licenses"
        lic_dir.mkdir(parents=True, exist_ok=True)
        with open(lic_dir / "CONTRIBUTING_CLA.md", "w", encoding="utf-8") as f:
            f.write("# CLA\n")
        with open(lic_dir / "ASSET_POLICY.md", "w", encoding="utf-8") as f:
            f.write("# Assets\n")
        pol_dir = self.root / "policies"
        pol_dir.mkdir(parents=True, exist_ok=True)
        with open(pol_dir / "BACKWARD-COMPATIBILITY-DRAFT.md", "w", encoding="utf-8") as f:
            f.write("# Backward\n")

        report_ok = audit_repository(self.root, check_policies=True)
        self.assertTrue(report_ok.is_compliant)
        self.assertTrue(any("Contributor License Agreement (CLA) found" in p for p in report_ok.passed_checks))


if __name__ == "__main__":
    unittest.main()
