import json
import unittest
from pathlib import Path

from aegean_licensing.cert import compute_canonical_payload, compute_digest

ROOT = Path(__file__).resolve().parent.parent
VECTOR = ROOT / "licenses" / "verification-vector.json"
SPEC = ROOT / "licenses" / "VERIFICATION.md"
REGISTER = ROOT / "licenses" / "issued.json"


class VerificationSpecTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(VECTOR.read_text(encoding="utf-8"))
        self.certificate = self.document["certificate"]

    def test_vector_digest_matches_the_python_canonicalization(self):
        self.assertEqual(
            compute_digest(self.certificate), self.document["expected_digest"]
        )
        self.assertEqual(self.certificate["digest"], self.document["expected_digest"])

    def test_vector_pins_non_ascii_and_projects_sorting(self):
        payload = compute_canonical_payload(self.certificate)
        self.assertIn(b"\\u0131", payload)
        self.assertIn(b"\\u2014", payload)
        self.assertIn(b"\\u007f", payload)
        self.assertIn(b'"numeric_probe":1', payload)
        self.assertIn(b'"nested_probe":{"a":{"z":true},"b":[3,"\\u00e9"]}', payload)
        self.assertIn(b'"projects":["Aegean-Licensing","Chronos"]', payload)
        self.assertNotIn("—".encode("utf-8"), payload)

    def test_ascii_escaping_matches_the_javascript_quote_function(self):
        payload = compute_canonical_payload(
            {"cert_id": "x", "format": 2, "note": "\x00\x1f\x7f\u0080"}
        )
        self.assertIn(b"\\u0000", payload)
        self.assertIn(b"\\u001f", payload)
        self.assertIn(b"\\u007f", payload)
        self.assertIn(b"\\u0080", payload)

    def test_numbers_are_safe_integers_in_both_runtimes(self):
        self.assertEqual(
            compute_canonical_payload({"cert_id": "x", "format": 2, "n": 1.0}),
            b'{"cert_id":"x","format":2,"n":1}',
        )
        for value in (1.5, 2 ** 53, -(2 ** 53), float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    compute_canonical_payload({"cert_id": "x", "format": 2, "n": value})

    def test_vector_is_not_an_issued_certificate(self):
        self.assertIn("not an issued certificate", self.document["note"])
        register = json.loads(REGISTER.read_text(encoding="utf-8"))
        self.assertNotIn(self.certificate["cert_id"], register["certificates"])

    def test_vector_uses_the_format_two_contract(self):
        self.assertEqual(self.certificate["format"], 2)
        self.assertRegex(self.certificate["serial"], r"^[0-9a-f]{64}$")
        self.assertEqual(self.certificate["signature"], "")

    def test_spec_names_the_digest_and_the_vector(self):
        text = SPEC.read_text(encoding="utf-8")
        self.assertIn(self.document["expected_digest"], text)
        self.assertIn("verification-vector.json", text)
        self.assertIn("never published", text)
        self.assertIn("UNREGISTERED", text)
        self.assertIn("REVOKED", text)


if __name__ == "__main__":
    unittest.main()
