"""Unit tests for the verification-ruleset fingerprint (IDEA-076)."""

import unittest
from types import SimpleNamespace

from aegean_licensing.fingerprint import (
    DEFAULT_FINGERPRINT,
    DEFAULT_PROFILE,
    DEFAULT_RULE_DIGESTS,
    FingerprintMismatch,
    VerificationProfile,
    compare_results,
    ruleset_fingerprint,
)
from aegean_licensing.verifier import verify_certificate


class TestFingerprint(unittest.TestCase):
    def test_default_fingerprint_is_stable_and_order_independent(self):
        self.assertEqual(ruleset_fingerprint(DEFAULT_PROFILE, DEFAULT_RULE_DIGESTS),
                         DEFAULT_FINGERPRINT)
        self.assertEqual(ruleset_fingerprint(DEFAULT_PROFILE,
                                             list(reversed(DEFAULT_RULE_DIGESTS))),
                         DEFAULT_FINGERPRINT)

    def test_a_profile_change_changes_the_fingerprint(self):
        changed = VerificationProfile(normalization_version="3")
        self.assertNotEqual(ruleset_fingerprint(changed, DEFAULT_RULE_DIGESTS),
                            DEFAULT_FINGERPRINT)

    def test_compare_accepts_equal_fingerprints_and_rejects_mismatch(self):
        same = (SimpleNamespace(ruleset_fingerprint=DEFAULT_FINGERPRINT),
                SimpleNamespace(ruleset_fingerprint=DEFAULT_FINGERPRINT))
        compare_results(*same)
        with self.assertRaises(FingerprintMismatch):
            compare_results(SimpleNamespace(ruleset_fingerprint=DEFAULT_FINGERPRINT),
                            SimpleNamespace(ruleset_fingerprint="f" * 64))

    def test_unfingerprinted_results_never_compare_equal(self):
        with self.assertRaises(FingerprintMismatch):
            compare_results(SimpleNamespace(ruleset_fingerprint=""),
                            SimpleNamespace(ruleset_fingerprint=""))
        with self.assertRaises(FingerprintMismatch):
            compare_results(SimpleNamespace(ruleset_fingerprint=""),
                            SimpleNamespace(ruleset_fingerprint=DEFAULT_FINGERPRINT))

    def test_verifier_results_carry_the_default_fingerprint(self):
        result = verify_certificate({})
        self.assertEqual(result.ruleset_fingerprint, DEFAULT_FINGERPRINT)


if __name__ == "__main__":
    unittest.main()
