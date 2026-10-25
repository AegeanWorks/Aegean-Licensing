"""Commercial License Certificate Verification Module."""

from __future__ import annotations

import dataclasses
import datetime
import hmac
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from aegean_licensing.cert import (
    CERT_FORMAT,
    SERIAL_HEX_LENGTH,
    LicenseCertificate,
    cert_from_dict,
    compute_digest,
    compute_signature,
)
from aegean_licensing.license_terms import resolve_license, terms_digest
from aegean_licensing.register import STATUS_REVOKED, load_register

_SERIAL = re.compile(rf"[0-9a-f]{{{SERIAL_HEX_LENGTH}}}")


@dataclasses.dataclass(frozen=True)
class VerificationResult:
    """Outcome of validating a License Grant Certificate."""

    is_valid: bool
    # "VALID", "VALID_UNVERIFIED", "TAMPERED", "EXPIRED", "SCOPE_MISMATCH", "INVALID_FORMAT",
    # "UNREGISTERED", "REVOKED", "UNSUPPORTED_FORMAT"
    status: str
    reasons: tuple[str, ...]
    cert: Optional[LicenseCertificate] = None
    signature_verified: bool = False
    terms_verified: bool = False
    registered: bool = False


def verify_certificate(
    target: Union[Dict[str, Any], str, Path],
    secret_key: Optional[str] = None,
    check_project: Optional[str] = None,
    reference_date: Optional[str] = None,
    register_path: Optional[Union[str, Path]] = None,
) -> VerificationResult:
    """
    Verify authenticity, tamper-resistance, expiration, and scope of a license certificate. With
    `register_path`, the public register (ADR-013) proves authenticity without the signing key: a
    certificate absent from it, or listed with another digest, is UNREGISTERED; a revoked one is
    REVOKED.
    """
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

    # 0. Format: only format 2 verifies; format 1, from the issuer published before ADR-018, never does
    certificate_format = data.get("format", 1)
    if certificate_format != CERT_FORMAT:
        return VerificationResult(
            is_valid=False,
            status="UNSUPPORTED_FORMAT",
            reasons=(f"Certificate format {certificate_format!r} is not accepted; only format "
                     f"{CERT_FORMAT} certificates are valid (ADR-018).",),
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

    # Construct typed certificate
    cert = cert_from_dict(data)
    if not _SERIAL.fullmatch(cert.serial):
        reasons.append(f"Certificate serial must be {SERIAL_HEX_LENGTH} lowercase hex characters.")
        return VerificationResult(is_valid=False, status="INVALID_FORMAT",
                                  reasons=tuple(reasons), cert=cert)

    # 3. Terms check: the certificate must cite an operative agreement whose bundled text matches
    terms_verified = False
    if cert.license_type:
        try:
            terms = resolve_license(cert.license_type, require_operative=False)
        except ValueError as exc:
            reasons.append(str(exc))
            return VerificationResult(
                is_valid=False,
                status="INVALID_FORMAT",
                reasons=tuple(reasons),
                cert=cert,
            )
        if cert.tier and terms.tiers and cert.tier not in terms.tiers:
            reasons.append(
                f"Tier '{cert.tier}' is not defined by {terms.key}; allowed: {', '.join(terms.tiers)}."
            )
            return VerificationResult(
                is_valid=False,
                status="INVALID_FORMAT",
                reasons=tuple(reasons),
                cert=cert,
            )
        unknown = [a for a in cert.allowances if a not in terms.allowances]
        if unknown:
            reasons.append(f"Allowances {unknown} are not defined by {terms.key}.")
            return VerificationResult(is_valid=False, status="INVALID_FORMAT",
                                      reasons=tuple(reasons), cert=cert)
        if cert.terms_digest:
            try:
                expected_terms = terms_digest(terms)
            except ValueError as exc:
                reasons.append(str(exc))
                return VerificationResult(is_valid=False, status="INVALID_FORMAT",
                                          reasons=tuple(reasons), cert=cert)
            if not hmac.compare_digest(cert.terms_digest, expected_terms):
                reasons.append(
                    "Certificate cites terms that do not match the current agreement text; "
                    "the license document may have changed after issuance."
                )
                return VerificationResult(
                    is_valid=False,
                    status="INVALID_FORMAT",
                    reasons=tuple(reasons),
                    cert=cert,
                )
            terms_verified = True

    # 4. Signature verification (if a verification key was provided)
    recorded_signature = str(data.get("signature", "")).strip()
    signature_verified = False
    if secret_key:
        if not recorded_signature:
            reasons.append("Certificate lacks signature, but verification key was provided.")
            return VerificationResult(
                is_valid=False,
                status="TAMPERED",
                reasons=tuple(reasons),
                cert=cert,
            )
        expected_sig = compute_signature(data, secret_key)
        if not hmac.compare_digest(recorded_signature, expected_sig):
            reasons.append("Cryptographic HMAC signature is invalid.")
            return VerificationResult(
                is_valid=False,
                status="TAMPERED",
                reasons=tuple(reasons),
                cert=cert,
            )
        signature_verified = True

    # 4b. Public register: issued by AegeanWorks, and not revoked (ADR-013)
    registered = False
    if register_path is not None:
        try:
            entry = load_register(register_path).get(cert.cert_id)
        except (OSError, ValueError) as exc:
            reasons.append(f"Cannot read the certificate register: {exc}")
            return VerificationResult(is_valid=False, status="INVALID_FORMAT",
                                      reasons=tuple(reasons), cert=cert)
        if entry is None or not hmac.compare_digest(entry.digest, recorded_digest):
            reasons.append(f"Certificate {cert.cert_id} is not in the register of issued certificates.")
            return VerificationResult(is_valid=False, status="UNREGISTERED",
                                      reasons=tuple(reasons), cert=cert)
        if entry.status == STATUS_REVOKED:
            reasons.append(f"Certificate {cert.cert_id} was revoked on {entry.revoked_at}: {entry.reason}")
            return VerificationResult(is_valid=False, status="REVOKED",
                                      reasons=tuple(reasons), cert=cert)
        registered = True

    # 5. Term consistency: perpetual certificates cannot expire, term-limited ones must
    if cert.is_perpetual and cert.expires_at:
        reasons.append("Certificate is perpetual but also declares 'expires_at'.")
        return VerificationResult(
            is_valid=False,
            status="INVALID_FORMAT",
            reasons=tuple(reasons),
            cert=cert,
        )
    if not cert.is_perpetual and not cert.expires_at:
        reasons.append("Certificate is not perpetual but declares no 'expires_at'.")
        return VerificationResult(
            is_valid=False,
            status="INVALID_FORMAT",
            reasons=tuple(reasons),
            cert=cert,
        )

    # 6. Expiration check
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

    # 7. Project scope check
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
        status="VALID" if signature_verified or registered else "VALID_UNVERIFIED",
        reasons=tuple(reasons),
        cert=cert,
        signature_verified=signature_verified,
        terms_verified=terms_verified,
        registered=registered,
    )
