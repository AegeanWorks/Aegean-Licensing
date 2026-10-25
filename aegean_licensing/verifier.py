"""Commercial License Certificate Verification Module."""

from __future__ import annotations

import dataclasses
import datetime
import hmac
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from aegean_licensing.cert import (
    LicenseCertificate,
    cert_from_dict,
    compute_digest,
    compute_signature,
)


@dataclasses.dataclass(frozen=True)
class VerificationResult:
    """Outcome of validating a License Grant Certificate."""

    is_valid: bool
    status: str  # "VALID", "TAMPERED", "EXPIRED", "SCOPE_MISMATCH", "INVALID_FORMAT"
    reasons: tuple[str, ...]
    cert: Optional[LicenseCertificate] = None


def verify_certificate(
    target: Union[Dict[str, Any], str, Path],
    secret_key: Optional[str] = None,
    check_project: Optional[str] = None,
    reference_date: Optional[str] = None,
) -> VerificationResult:
    """Verify authenticity, tamper-resistance, expiration, and scope of a license certificate."""
    reasons: List[str] = []

    if isinstance(target, (str, Path)):
        file_path = Path(target)
        if not file_path.exists():
            return VerificationResult(
                is_valid=False,
                status="INVALID_FORMAT",
                reasons=(f"Certificate file does not exist: {file_path}",),
            )
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            return VerificationResult(
                is_valid=False,
                status="INVALID_FORMAT",
                reasons=(f"Failed to parse certificate JSON: {exc}",),
            )
    elif isinstance(target, dict):
        data = target
    else:
        return VerificationResult(
            is_valid=False,
            status="INVALID_FORMAT",
            reasons=("Target must be a dictionary or path to a JSON file.",),
        )

    # 1. Structural checks
    recorded_digest = str(data.get("digest", "")).strip()
    if not recorded_digest:
        reasons.append("Certificate is missing required 'digest' field.")
        return VerificationResult(
            is_valid=False,
            status="TAMPERED",
            reasons=tuple(reasons),
        )

    # 2. Tamper check (Digest verification)
    expected_digest = compute_digest(data)
    if not hmac.compare_digest(recorded_digest, expected_digest):
        reasons.append(
            f"Digest mismatch! Recorded digest '{recorded_digest}' does not match computed '{expected_digest}'."
        )
        return VerificationResult(
            is_valid=False,
            status="TAMPERED",
            reasons=tuple(reasons),
        )

    # 3. Signature verification (if secret_key is provided or expected)
    recorded_signature = str(data.get("signature", "")).strip()
    if secret_key:
        if not recorded_signature:
            reasons.append("Certificate lacks signature, but verification key was provided.")
            return VerificationResult(
                is_valid=False,
                status="TAMPERED",
                reasons=tuple(reasons),
            )
        expected_sig = compute_signature(data, secret_key)
        if not hmac.compare_digest(recorded_signature, expected_sig):
            reasons.append("Cryptographic HMAC signature is invalid.")
            return VerificationResult(
                is_valid=False,
                status="TAMPERED",
                reasons=tuple(reasons),
            )

    # Construct typed certificate
    cert = cert_from_dict(data)

    # 4. Expiration check
    if not cert.is_perpetual and cert.expires_at:
        ref_str = reference_date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        try:
            exp_date = datetime.date.fromisoformat(cert.expires_at)
            ref_date = datetime.date.fromisoformat(ref_str)
            if ref_date > exp_date:
                reasons.append(f"Certificate expired on {cert.expires_at} (reference date: {ref_str}).")
                return VerificationResult(
                    is_valid=False,
                    status="EXPIRED",
                    reasons=tuple(reasons),
                    cert=cert,
                )
        except ValueError as exc:
            reasons.append(f"Invalid date format in certificate: {exc}")
            return VerificationResult(
                is_valid=False,
                status="INVALID_FORMAT",
                reasons=tuple(reasons),
                cert=cert,
            )

    # 5. Project scope check
    if check_project:
        norm_project = check_project.strip().lower()
        allowed = [p.lower() for p in cert.projects]
        if "*" not in allowed and norm_project not in allowed:
            reasons.append(
                f"Project '{check_project}' is not covered by authorized projects: {list(cert.projects)}."
            )
            return VerificationResult(
                is_valid=False,
                status="SCOPE_MISMATCH",
                reasons=tuple(reasons),
                cert=cert,
            )

    return VerificationResult(
        is_valid=True,
        status="VALID",
        reasons=tuple(reasons),
        cert=cert,
    )
