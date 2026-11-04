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
        # The write path carries the loaded schema version forward (defaulting to 2),
        # so a future register v3 survives an /agree-cla write instead of downgrading.
        self.assertIn("fresh.version ?? 2", workflow)

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

    def test_cla_register_preserves_schema_version(self):
        # A future register v3 must survive an /agree-cla write: hardcoding
        # `version: 2` on the write path would silently downgrade it and drop
        # v3 fields. The writer must carry the loaded version forward.
        workflow = (REPO_ROOT / ".github" / "workflows" / "cla-check.yml").read_text(encoding="utf-8")
        self.assertIn("fresh.version ?? 2", workflow)
        self.assertNotIn("version: 2,", workflow)

    def test_cla_signatures_sort_is_deterministic(self):
        # localeCompare follows ICU and can reorder the same logins across runner
        # images, producing spurious register commits and 409 retries. Codepoint
        # order is stable everywhere.
        workflow = (REPO_ROOT / ".github" / "workflows" / "cla-check.yml").read_text(encoding="utf-8")
        self.assertNotIn("localeCompare", workflow)
        self.assertIn("a.login < b.login", workflow)

    def test_ci_windows_job_is_a_pinned_single_version_smoke(self):
        # The full 3.10-3.13 matrix runs on ubuntu; Windows is a platform smoke on one
        # pinned version. If the Windows job gains a matrix, this test must be updated
        # deliberately — the 1-version coverage is a locked cost decision, not an oversight.
        workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        windows_job = workflow.split("test-windows:", 1)[1]
        self.assertIn('python-version: "3.12"', windows_job)
        self.assertNotIn("matrix:", windows_job)

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

    def test_docs_name_the_operative_personal_license(self):
        # ADR-022: new projects and entry docs use AL-1.1. AL-1.0 survives only in the
        # archived 1.0 texts, CHANGELOG history, the CI wheel-content pin for archived
        # files, and ACL-1.0's frozen definitions reference.
        commercial = (REPO_ROOT / "COMMERCIAL.md").read_text(encoding="utf-8")
        self.assertNotIn("AL-1.0", commercial)
        self.assertIn("AL-1.1", commercial)
        cla = (REPO_ROOT / "licenses" / "CONTRIBUTING_CLA.md").read_text(encoding="utf-8")
        self.assertNotIn("AL-1.0", cla)
        self.assertIn("AL-1.1", cla)
        notice = (REPO_ROOT / "licenses" / "DUAL_LICENSE_NOTICE.txt").read_text(encoding="utf-8")
        self.assertIn("AGL-1.1", notice)
        self.assertIn("ASL-1.1", notice)
        self.assertEqual(
            (REPO_ROOT / "LICENSE").read_bytes(),
            (REPO_ROOT / "licenses" / "AL-1.1.md").read_bytes(),
        )


if __name__ == "__main__":
    unittest.main()
