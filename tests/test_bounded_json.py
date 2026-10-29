"""Unit tests for bounded JSON loading (IDEA-118)."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aegean_licensing.bounded_json import (
    ConfigError,
    ParseLimits,
    TooDeep,
    TooLarge,
    TooManyNodes,
    limits_from_env,
    load_bounded,
    parse_limit,
)
from aegean_licensing.register import load_register
from aegean_licensing.verifier import verify_certificate


class TestParseLimits(unittest.TestCase):
    def test_plain_bytes_and_binary_suffixes(self):
        self.assertEqual(parse_limit("1024", default=1, variable="X"), 1024)
        self.assertEqual(parse_limit("640MB", default=1, variable="X"), 640 * 1024 ** 2)
        self.assertEqual(parse_limit("2GB", default=1, variable="X"), 2 * 1024 ** 3)
        self.assertEqual(parse_limit(None, default=9, variable="X"), 9)
        self.assertEqual(parse_limit("", default=9, variable="X"), 9)

    def test_invalid_values_are_config_errors_not_silent_defaults(self):
        for raw in ("MB", "-1", "2TB", "0", "1.5MB", "many"):
            with self.subTest(raw=raw):
                with self.assertRaises(ConfigError) as caught:
                    parse_limit(raw, default=1, variable="AEGEAN_JSON_MAX_BYTES")
                self.assertIn("AEGEAN_JSON_MAX_BYTES", str(caught.exception))

    def test_environment_limits_are_read_and_validated(self):
        limits = limits_from_env({"AEGEAN_JSON_MAX_BYTES": "1MB",
                                 "AEGEAN_JSON_MAX_DEPTH": "8",
                                 "AEGEAN_JSON_MAX_NODES": "20"})
        self.assertEqual((limits.max_bytes, limits.max_depth, limits.max_nodes),
                         (1024 ** 2, 8, 20))


class TestLoadBounded(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_bounded_json_"))
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def write(self, name: str, content: bytes) -> Path:
        path = self.temp_dir / name
        path.write_bytes(content)
        return path

    def test_file_exactly_at_the_byte_cap_parses(self):
        content = b"{}" + b" " * 18
        path = self.write("exact.json", content)
        self.assertEqual(load_bounded(path, ParseLimits(max_bytes=len(content))), {})

    def test_one_byte_over_the_cap_is_too_large(self):
        content = b"{}" + b" " * 19
        path = self.write("large.json", content)
        with self.assertRaises(TooLarge) as caught:
            load_bounded(path, ParseLimits(max_bytes=len(content) - 1))
        self.assertEqual(caught.exception.observed, len(content))
        self.assertEqual(caught.exception.limit, len(content) - 1)

    def test_depth_is_bounded_below_the_byte_cap(self):
        path = self.write("deep.json", ("[" * 100 + "0" + "]" * 100).encode("utf-8"))
        with self.assertRaises(TooDeep) as caught:
            load_bounded(path, ParseLimits(max_bytes=4096, max_depth=64))
        self.assertEqual(caught.exception.limit, 64)

    def test_node_count_is_bounded(self):
        path = self.write("nodes.json", ("[" + ",".join(["0"] * 50) + "]").encode("utf-8"))
        with self.assertRaises(TooManyNodes) as caught:
            load_bounded(path, ParseLimits(max_bytes=4096, max_nodes=10))
        self.assertEqual(caught.exception.limit, 10)

    def test_utf8_bom_is_accepted(self):
        path = self.write("bom.json", b"\xef\xbb\xbf{}")
        self.assertEqual(load_bounded(path), {})

    def test_corrupt_json_under_the_cap_raises_a_value_error(self):
        path = self.write("corrupt.json", b"{")
        with self.assertRaises(ValueError):
            load_bounded(path)

    def test_register_loader_uses_the_bounded_path(self):
        path = self.write("register.json", b"{}")
        with mock.patch("aegean_licensing.register.load_bounded",
                        side_effect=TooLarge(10, 5)):
            with self.assertRaises(TooLarge):
                load_register(path)

    def test_verifier_file_loader_uses_the_bounded_path(self):
        path = self.write("certificate.json", b"{}")
        with mock.patch("aegean_licensing.verifier.load_bounded",
                        side_effect=TooLarge(10, 5)):
            result = verify_certificate(path)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "INVALID_FORMAT")
        self.assertIn("above the 5-byte limit", result.reasons[0])


if __name__ == "__main__":
    unittest.main()
