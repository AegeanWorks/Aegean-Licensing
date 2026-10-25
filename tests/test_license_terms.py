"""Unit tests for the frozen text of operative agreements (ADR-013)."""

import dataclasses
import unittest
from unittest import mock

from aegean_licensing import license_terms
from aegean_licensing.cert import cert_to_dict
from aegean_licensing.license_terms import (
    compute_terms_digest,
    load_registry,
    read_license_document,
    terms_digest,
)
from aegean_licensing.verifier import verify_certificate
from tests.fixtures import issue_certificate


class TestFrozenTerms(unittest.TestCase):
    """A certificate cites an agreement's digest, so an issued agreement's text must never change."""

    def test_every_operative_agreement_pins_its_text(self):
        for key, terms in load_registry().items():
            if not terms.is_operative:
                continue
            with self.subTest(key=key):
                self.assertTrue(terms.sha256, "an operative agreement records its sha256 in terms.json")
                self.assertEqual(compute_terms_digest(read_license_document(terms)), terms.sha256,
                                 "the text changed: publish a new version instead of editing it")

    def test_an_edited_agreement_is_refused_and_fails_verification(self):
        cert = issue_certificate(licensee_name="Frozen Corp", licensee_contact="f@example.com")
        real = license_terms.read_license_document
        with mock.patch("aegean_licensing.license_terms.read_license_document",
                        side_effect=lambda terms: real(terms) + "\nA silent amendment.\n"):
            with self.assertRaises(ValueError) as caught:
                terms_digest(load_registry()["ACL-1.0"])
            result = verify_certificate(cert_to_dict(cert))
        self.assertIn("new version", str(caught.exception))
        self.assertEqual(result.status, "INVALID_FORMAT")

    def test_an_unpinned_agreement_still_yields_its_digest(self):
        terms = dataclasses.replace(load_registry()["ACL-1.0"], sha256="")
        self.assertEqual(terms_digest(terms), compute_terms_digest(read_license_document(terms)))


if __name__ == "__main__":
    unittest.main()
