"""Unit tests for licensing template generation."""

import unittest

from aegean_licensing.templates import (
    get_asset_policy,
    get_backward_compatibility_policy,
    get_commercial_agreement_template,
    get_commercial_md,
    get_contributor_cla,
    get_dual_license_rider,
    get_personal_use_license,
    get_pyproject_snippet,
)


class TestTemplates(unittest.TestCase):
    """Test standard licensing templates."""

    def test_dual_license_rider_content(self):
        rider = get_dual_license_rider()
        self.assertIn("Dual-Licensing Notice", rider)
        self.assertIn("aegean-licensing@proton.me", rider)
        self.assertIn("AGPL-3.0", rider)
        self.assertIn("AECL-1.0", rider)

    def test_commercial_md_content(self):
        comm = get_commercial_md()
        self.assertIn("AegeanWorks Commercial Licensing", comm)
        self.assertIn("Exhibit A: Standard AECL Terms", comm)
        self.assertIn("aegean-licensing@proton.me", comm)
        # Verify no enterprise bureaucracy
        self.assertNotIn("W-9", comm)
        self.assertNotIn("Net-30", comm)
        self.assertNotIn("Master Services Agreement", comm)

    def test_pyproject_snippet_content(self):
        snippet = get_pyproject_snippet()
        self.assertIn("AegeanWorks", snippet)
        self.assertIn("aegean-licensing@proton.me", snippet)
        self.assertIn("AGPL-3.0-or-later", snippet)

    def test_personal_use_license_content(self):
        al_pu = get_personal_use_license()
        self.assertIn("AL-PU", al_pu)
        self.assertIn("aegean-licensing@proton.me", al_pu)
        self.assertIn("Permission for Personal Use", al_pu)

    def test_commercial_agreement_template_content(self):
        acla = get_commercial_agreement_template()
        self.assertIn("Commercial License Agreement", acla)
        self.assertIn("aegean-licensing@proton.me", acla)

    def test_backward_compatibility_policy_content(self):
        compat = get_backward_compatibility_policy()
        self.assertIn("Backward Compatibility Policy", compat)
        self.assertIn("AGPL-3.0", compat)

    def test_contributor_cla_content(self):
        cla = get_contributor_cla()
        self.assertIn("Contributor License Agreement", cla)
        self.assertIn("dual-license", cla.lower())

    def test_asset_policy_content(self):
        policy = get_asset_policy()
        self.assertIn("Asset Separation", policy)


if __name__ == "__main__":
    unittest.main()
