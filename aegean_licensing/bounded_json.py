"""Bounded JSON loading for files that cross an untrusted boundary.

A certificate, register or license registry can be large, deeply nested or malformed. The
schema checks are too late if reading or parsing the file already exhausts memory. This module
applies a byte cap before parsing, a nesting-depth guard and a node budget, and it reads at most
one byte beyond the byte cap so a growing file cannot slip through the size check.
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping, Optional, Union

DEFAULT_MAX_BYTES = 16 * 1024 * 1024
DEFAULT_MAX_DEPTH = 64
DEFAULT_MAX_NODES = 200_000
_SUFFIXES = {"MB": 1024 ** 2, "GB": 1024 ** 3}
_LIMIT_RE = re.compile(r"(\d+)\s*(MB|GB)?")


@dataclasses.dataclass(frozen=True)
class ParseLimits:
    max_bytes: int = DEFAULT_MAX_BYTES
    max_depth: int = DEFAULT_MAX_DEPTH
    max_nodes: int = DEFAULT_MAX_NODES


class TooLarge(ValueError):
    """The input exceeded the byte cap before or during the bounded read."""

    def __init__(self, observed: int, limit: int, variable: str = "max_bytes") -> None:
        self.observed = observed
        self.limit = limit
        self.variable = variable
        super().__init__(
            f"JSON input is {observed} bytes, above the {limit}-byte limit ({variable}); "
            f"raise {variable} or provide a smaller document."
        )


class TooDeep(ValueError):
    """The input nested deeper than the parser is willing to recurse."""

    def __init__(self, depth: int, limit: int) -> None:
        self.depth = depth
        self.limit = limit
        super().__init__(f"JSON nesting depth {depth} exceeds the limit {limit}.")


class TooManyNodes(ValueError):
    """The input carries more structural nodes than the parser accepts."""

    def __init__(self, count: int, limit: int) -> None:
        self.count = count
        self.limit = limit
        super().__init__(f"JSON node count {count} exceeds the limit {limit}.")


class ConfigError(ValueError):
    """A configured parse limit is not a positive byte count with an optional MB/GB suffix."""


def parse_limit(raw: Optional[Union[str, int]], *, default: int, variable: str) -> int:
    """Resolve one limit, accepting plain bytes or the binary suffixes MB and GB."""
    if raw is None or str(raw).strip() == "":
        return default
    match = _LIMIT_RE.fullmatch(str(raw).strip().upper())
    if not match:
        raise ConfigError(f"Invalid {variable}={raw!r}; use bytes, MB or GB (for example 640MB).")
    number = int(match.group(1))
    if number <= 0:
        raise ConfigError(f"Invalid {variable}={raw!r}; the value must be positive.")
    return number * _SUFFIXES.get(match.group(2) or "", 1)


def limits_from_env(environ: Optional[Mapping[str, str]] = None) -> ParseLimits:
    """Read the three limits from the environment, validating each value at startup."""
    env = os.environ if environ is None else environ
    return ParseLimits(
        max_bytes=parse_limit(env.get("AEGEAN_JSON_MAX_BYTES"), default=DEFAULT_MAX_BYTES,
                              variable="AEGEAN_JSON_MAX_BYTES"),
        max_depth=parse_limit(env.get("AEGEAN_JSON_MAX_DEPTH"), default=DEFAULT_MAX_DEPTH,
                              variable="AEGEAN_JSON_MAX_DEPTH"),
        max_nodes=parse_limit(env.get("AEGEAN_JSON_MAX_NODES"), default=DEFAULT_MAX_NODES,
                              variable="AEGEAN_JSON_MAX_NODES"),
    )


def _guard_structure(text: str, limits: ParseLimits) -> None:
    """Reject depth and node bombs before json.loads can recurse or allocate freely."""
    depth = 0
    nodes = 0
    in_string = False
    escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            nodes += 1
            if depth > limits.max_depth:
                raise TooDeep(depth, limits.max_depth)
        elif char in "}]":
            depth = max(0, depth - 1)
            nodes += 1
        elif char in ",:":
            nodes += 1
        if nodes > limits.max_nodes:
            raise TooManyNodes(nodes, limits.max_nodes)


def load_bounded(path: Union[str, Path], limits: Optional[ParseLimits] = None) -> Any:
    """Read and parse one JSON file under byte, depth and node limits."""
    target = Path(path)
    limits = limits or ParseLimits()
    with open(target, "rb") as handle:
        observed = os.fstat(handle.fileno()).st_size
        if observed > limits.max_bytes:
            raise TooLarge(observed, limits.max_bytes)
        raw = handle.read(limits.max_bytes + 1)
    if len(raw) > limits.max_bytes:
        raise TooLarge(len(raw), limits.max_bytes)
    text = raw.decode("utf-8-sig")
    _guard_structure(text, limits)
    return json.loads(text)
