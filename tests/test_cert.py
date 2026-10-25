"""Unit tests for LicenseCertificate and cryptographic utilities."""

import dataclasses
import unittest

from aegean_licensing.cert import (
    CERT_FORMAT,
    LicenseCertificate,
    cert_from_dict,
    cert_to_dict,
    compute_canonical_payload,
    compute_digest,
    compute_signature,
)


class TestLicenseCertificate(unittest.TestCase):
    """Test certificate data transfer object and canonical hashing."""

    def test_cert_is_frozen(self):
        cert = LicenseCertificate(
            cert_id="test-123",
            licensee_name="Acme Corp",
            licensee_contact="legal@acme.com",
        )
        with self.assertRaises(dataclasses.FrozenInstanceError):
            setattr(cert, "cert_id", "new-id")

    def test_canonical_payload_is_deterministic(self):
        d1 = {
            "licensee_name": "Acme",
            "cert_id": "1",
            "projects": ["zeta", "alpha"],
            "digest": "ignore-me",
            "signature": "ignore-me-too",
        }
        d2 = {
            "projects": ["alpha", "zeta"],
            "cert_id": "1",
            "licensee_name": "Acme",
        }
        self.assertEqual(compute_canonical_payload(d1), compute_canonical_payload(d2))

    def test_digest_computation(self):
        d = {"cert_id": "test", "licensee_name": "Acme"}
        digest1 = compute_digest(d)
        digest2 = compute_digest(d)
        self.assertEqual(digest1, digest2)
        self.assertEqual(len(digest1), 64)

    def test_format_2_binds_digest_and_signature_to_their_own_domains(self):
        # ADR-018: a format-1 digest (plain SHA-256 of the payload) never equals a format-2 one,
        # and the digest and the signature never hash the same bytes.
        import hashlib
        import hmac
        d = {"cert_id": "test", "licensee_name": "Acme", "format": 2}
        payload = compute_canonical_payload(d)
        self.assertNotEqual(compute_digest(d), hashlib.sha256(payload).hexdigest())
        self.assertNotEqual(compute_signature(d, "k"),
                            hmac.new(b"k", payload, hashlib.sha256).hexdigest())
        self.assertEqual(CERT_FORMAT, 2)

    def test_signature_computation(self):
        d = {"cert_id": "test", "licensee_name": "Acme"}
        sig1 = compute_signature(d, "secret-1")
        sig2 = compute_signature(d, "secret-1")
        sig3 = compute_signature(d, "secret-2")
        self.assertEqual(sig1, sig2)
        self.assertNotEqual(sig1, sig3)

    def test_to_and_from_dict_roundtrip(self):
        cert = LicenseCertificate(
            cert_id="id-99",
            licensee_name="Beta Org",
            licensee_contact="dev@beta.org",
            projects=("chronos", "AIKit"),
            scope="proprietary-saas",
            is_perpetual=True,
            digest="abc123",
            signature="def456",
        )
        d = cert_to_dict(cert)
        reconstructed = cert_from_dict(d)
        self.assertEqual(cert, reconstructed)



if __name__ == "__main__":
    unittest.main()
