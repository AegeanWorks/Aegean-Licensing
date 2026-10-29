"""A stable identity for the rules a verification result was produced under."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from typing import Any, Sequence


@dataclasses.dataclass(frozen=True)
class VerificationProfile:
    ruleset_version: str = "2"
    allowed_algorithms: tuple = ("sha256", "hmac-sha256")
    reference_date_policy: str = "caller-supplied-or-utc-today"
    normalization_version: str = "2"


DEFAULT_PROFILE = VerificationProfile()
DEFAULT_RULE_DIGESTS = (
    "format-2", "serial-64-hex", "type-checks-before-canonicalization",
    "digest-domain", "signature-domain", "terms-registry", "scope-vocabulary",
    "allowance-vocabulary", "register-status", "term-consistency", "expiry",
)


def ruleset_fingerprint(profile: VerificationProfile, rule_digests: Sequence[str]) -> str:
    """SHA-256 over the declarative profile and the ordered rule identities."""
    payload: dict[str, Any] = {
        "ruleset_version": profile.ruleset_version,
        "allowed_algorithms": list(profile.allowed_algorithms),
        "reference_date_policy": profile.reference_date_policy,
        "normalization_version": profile.normalization_version,
        "rules": sorted(rule_digests),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


DEFAULT_FINGERPRINT = ruleset_fingerprint(DEFAULT_PROFILE, DEFAULT_RULE_DIGESTS)
UNFINGERPRINTED = ""


class FingerprintMismatch(ValueError):
    """Two results were produced under different verification rules."""


def compare_results(left: Any, right: Any) -> None:
    """Refuse to compare results whose ruleset fingerprints differ or are missing."""
    left_fp = str(getattr(left, "ruleset_fingerprint", "") or "")
    right_fp = str(getattr(right, "ruleset_fingerprint", "") or "")
    if not left_fp or not right_fp:
        raise FingerprintMismatch(
            "Cannot compare an unfingerprinted verification result; re-run it under a known "
            "verification profile."
        )
    if left_fp != right_fp:
        raise FingerprintMismatch(
            f"Verification results use different rulesets ({left_fp[:12]} != {right_fp[:12]}); "
            "do not aggregate them as if they were produced under the same rules."
        )
