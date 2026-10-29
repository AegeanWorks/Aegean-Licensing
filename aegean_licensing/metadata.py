"""Validation and normalization for certificate fields that reach a renderer."""

from __future__ import annotations

import unicodedata

MAX_METADATA_BYTES = 200
FORBIDDEN_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Zl", "Zp"})


class MetadataError(ValueError):
    """A rendered certificate field carries markup or a control character."""

    def __init__(self, field: str, category: str, message: str) -> None:
        self.field = field
        self.category = category
        super().__init__(f"'{field}' {message}")


def normalize_metadata_text(field: str, value: object, max_bytes: int = MAX_METADATA_BYTES) -> str:
    """Collapse whitespace, reject markup/control characters, and cap UTF-8 length."""
    if not isinstance(value, str):
        raise MetadataError(field, "type", "must be a string.")
    if "\u2028" in value or "\u2029" in value:
        raise MetadataError(field, "line_separator", "contains a Unicode line separator.")
    text = " ".join(value.split())
    if "<" in text or ">" in text:
        raise MetadataError(field, "angle_bracket", "must not contain '<' or '>'.")
    for char in text:
        if unicodedata.category(char) in FORBIDDEN_CATEGORIES:
            raise MetadataError(field, "control", "contains a disallowed control or separator character.")
    if len(text.encode("utf-8")) > max_bytes:
        raise MetadataError(field, "too_long", f"exceeds {max_bytes} UTF-8 bytes.")
    return text
