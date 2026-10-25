"""Unit tests for bundling licensing documents into the built package."""

import shutil
import tempfile
import unittest
from pathlib import Path

from aegean_licensing.bundler import bundle_documents


class TestBundler(unittest.TestCase):
    """Test document discovery and copy layout."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_bundler_"))
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)
        self.repo = self.temp_dir / "repo"
        self.build = self.temp_dir / "build"
        (self.repo / "licenses" / "commercial").mkdir(parents=True)
        (self.repo / "policies").mkdir()
        (self.repo / "licenses" / "ACL-1.0.md").write_text("# ACL\n", encoding="utf-8")
        (self.repo / "licenses" / "commercial" / "TEMPLATE.md").write_text("# Template\n", encoding="utf-8")
        (self.repo / "policies" / "PLAN.md").write_text("# Plan\n", encoding="utf-8")
        workflow = self.repo / ".github" / "workflows"
        workflow.mkdir(parents=True)
        (workflow / "cla-check.yml").write_text("name: CLA\n", encoding="utf-8")

    def test_documents_are_copied_into_package_resources(self):
        copied = bundle_documents(self.repo, self.build)
        self.assertEqual(copied, 4)
        resources = self.build / "aegean_licensing" / "resources"
        self.assertTrue((resources / "licenses" / "ACL-1.0.md").is_file())
        self.assertTrue((resources / "licenses" / "commercial" / "TEMPLATE.md").is_file())
        self.assertTrue((resources / "policies" / "PLAN.md").is_file())
        self.assertTrue((resources / ".github" / "workflows" / "cla-check.yml").is_file())

    def test_empty_repository_is_rejected(self):
        empty = self.temp_dir / "empty"
        empty.mkdir()
        with self.assertRaises(RuntimeError):
            bundle_documents(empty, self.build)


if __name__ == "__main__":
    unittest.main()
