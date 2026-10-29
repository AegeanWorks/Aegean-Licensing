"""Asset tests for the CLA workflow, CI workflow, and packaging manifest."""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestWorkflowAssets(unittest.TestCase):
    """Test the durable CLA register, workflow wiring, and manifest coverage."""

    def test_cla_register_is_valid_json(self):
        register = json.loads((REPO_ROOT / ".github" / "cla-signatures.json").read_text(encoding="utf-8"))
        self.assertEqual(register["version"], 2)
        self.assertIsInstance(register["signatures"], list)
        self.assertIsInstance(register["revoked"], list)

    def test_workflow_records_evidence_and_honours_revocation(self):
        workflow = (REPO_ROOT / ".github" / "workflows" / "cla-check.yml").read_text(encoding="utf-8")
        self.assertIn(".github/cla-signatures.json", workflow)
        self.assertIn("createOrUpdateFileContents", workflow)
        self.assertIn("pull_request_target", workflow)
        self.assertIn("labeled", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("/agree-cla", workflow)
        self.assertIn("revoked", workflow)
        self.assertIn("evidence", workflow)
        self.assertIn("version: 2", workflow)

    def test_cla_result_is_a_commit_status_the_comment_run_can_turn_green(self):
        # ADR-016: a run started by a /agree-cla comment is not attached to the pull request's
        # head, and labels added by GITHUB_TOKEN start no new run, so the verdict is a commit
        # status on the head sha that every run updates.
        workflow = (REPO_ROOT / ".github" / "workflows" / "cla-check.yml").read_text(encoding="utf-8")
        self.assertIn("statuses: write", workflow)
        self.assertIn("createCommitStatus", workflow)
        self.assertIn("pulls.get", workflow)
        self.assertIn("author_association", workflow)
        self.assertNotIn("author === repoOwner", workflow, "an org login never authors a PR")
        self.assertNotIn("dual-license", workflow)

    def test_ci_workflow_runs_tests_and_checks_the_wheel(self):
        workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("python -m unittest discover tests", workflow)
        self.assertIn("python -m pip wheel", workflow)
        self.assertIn("aegean_licensing/resources/licenses/ACL-1.0.md", workflow)
        self.assertIn("windows-latest", workflow)
        for version in ('"3.10"', '"3.11"', '"3.12"', '"3.13"'):
            self.assertIn(version, workflow)

    def test_manifest_covers_legal_documents(self):
        manifest = (REPO_ROOT / "MANIFEST.in").read_text(encoding="utf-8")
        for entry in (
            "recursive-include licenses",
            "recursive-include policies",
            ".github/workflows/cla-check.yml",
            "include setup.py",
            "include REUSE.toml",
            "*.json",
        ):
            self.assertIn(entry, manifest)
        for directory in ("licenses", "policies"):
            self.assertTrue((REPO_ROOT / directory).is_dir())
        self.assertTrue((REPO_ROOT / "REUSE.toml").is_file())
        self.assertIn("LicenseRef-AL-1.1", (REPO_ROOT / "REUSE.toml").read_text(encoding="utf-8"))
        self.assertTrue((REPO_ROOT / "licenses" / "LicenseRef-AL-1.1.txt").is_file())


if __name__ == "__main__":
    unittest.main()
