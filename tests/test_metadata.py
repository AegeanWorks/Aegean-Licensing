"""Unit tests for rendered certificate metadata validation (IDEA-090)."""

import unittest

from aegean_licensing.cert import cert_from_dict
from aegean_licensing.metadata import MetadataError, normalize_metadata_text


class TestMetadata(unittest.TestCase):
    def test_normal_text_survives_and_whitespace_is_collapsed(self):
        self.assertEqual(normalize_metadata_text("licensee_name", " O'Brien   & Sons "),
                         "O'Brien & Sons")

    def test_angle_brackets_are_rejected(self):
        with self.assertRaises(MetadataError) as caught:
            normalize_metadata_text("licensee_name", "<script>alert(1)</script>")
        self.assertEqual(caught.exception.category, "angle_bracket")

    def test_control_and_line_separator_characters_are_rejected(self):
        for value in ("Ada\x00Lovelace", "Ada\u2028Lovelace", "Ada\u2029Lovelace"):
            with self.subTest(value=repr(value)):
                with self.assertRaises(MetadataError) as caught:
                    normalize_metadata_text("licensee_name", value)
                self.assertEqual(caught.exception.category,
                                 "line_separator" if "\u2028" in value or "\u2029" in value
                                 else "control")

    def test_utf8_length_is_capped(self):
        with self.assertRaises(MetadataError) as caught:
            normalize_metadata_text("licensee_name", "ş" * 101)
        self.assertEqual(caught.exception.category, "too_long")
        self.assertEqual(normalize_metadata_text("licensee_name", "ş" * 100), "ş" * 100)

    def test_cert_from_dict_rejects_unsafe_metadata(self):
        with self.assertRaises(MetadataError):
            cert_from_dict({"cert_id": "x", "licensee_name": "<b>Acme</b>",
                            "licensee_contact": "a@example.com"})
        with self.assertRaises(MetadataError):
            cert_from_dict({"cert_id": "x", "licensee_name": "Acme",
                            "licensee_contact": "a@example.com", "projects": ["ok", "<bad>"]})

    def test_cert_from_dict_normalizes_project_and_allowance_spaces(self):
        cert = cert_from_dict({"cert_id": "x", "licensee_name": "  Acme  ",
                               "licensee_contact": "a@example.com",
                               "projects": ["  chronos ", "AIKit"],
                               "allowances": [" hosted-service "]})
        self.assertEqual(cert.licensee_name, "Acme")
        self.assertEqual(cert.projects, ("AIKit", "chronos"))
        self.assertEqual(cert.allowances, ("hosted-service",))


if __name__ == "__main__":
    unittest.main()
