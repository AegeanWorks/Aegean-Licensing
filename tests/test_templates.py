"""Unit tests for licensing template generation."""

import unittest

from aegean_licensing.templates import (
    get_commercial_md,
    get_dual_license_rider,
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


if __name__ == "__main__":
    unittest.main()
