"""Commercial License Certificate Verification Module."""

from __future__ import annotations

import dataclasses
import datetime
import hmac
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from aegean_licensing.bounded_json import load_bounded
from aegean_licensing.fingerprint import DEFAULT_FINGERPRINT
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
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


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
    ruleset_fingerprint: str = DEFAULT_FINGERPRINT


def _type_error(data: Dict[str, Any]) -> Optional[str]:
    """A field whose JSON type cannot be read safely, or None.

    The public verifier reads untrusted files: a list of numbers in `projects`, a number in
    `allowances` or a list in `expires_at` used to raise `TypeError` deep in the dataclass instead
    of reporting INVALID_FORMAT. Only the types the format defines are accepted here.
    """
    projects = data.get("projects", ["*"])
    if isinstance(projects, str):
        pass
    elif isinstance(projects, (list, tuple)):
        if not all(isinstance(project, str) for project in projects):
            return "'projects' must contain only strings."
    else:
        return "'projects' must be a string or a list of strings."
    allowances = data.get("allowances", [])
    if isinstance(allowances, str):
        pass
    elif isinstance(allowances, (list, tuple)):
        if not all(isinstance(allowance, str) for allowance in allowances):
            return "'allowances' must contain only strings."
    else:
        return "'allowances' must be a string or a list of strings."
    expires_at = data.get("expires_at")
    if expires_at is not None and not isinstance(expires_at, str):
        return "'expires_at' must be a string or null."
    if "is_perpetual" in data and not isinstance(data["is_perpetual"], bool):
        return "'is_perpetual' must be a boolean."
    if "license_type" in data and (
        not isinstance(data["license_type"], str) or not data["license_type"].strip()
    ):
        return "'license_type' must be a non-empty string."
    return None


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
            data = load_bounded(file_path)
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

    if not isinstance(data, dict):
        return VerificationResult(
            is_valid=False,
            status="INVALID_FORMAT",
            reasons=("Certificate JSON must be an object, not a list, string or number.",),
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

    # 2. Structural type checks before canonicalization: mixed or wrong-typed lists cannot be
    # sorted or compared safely, and must be INVALID_FORMAT rather than an uncaught TypeError.
    type_error = _type_error(data)
    if type_error:
        reasons.append(type_error)
        return VerificationResult(is_valid=False, status="INVALID_FORMAT",
                                  reasons=tuple(reasons))

    # 3. Tamper check (Digest verification)
    try:
        expected_digest = compute_digest(data)
    except (TypeError, ValueError) as exc:
        reasons.append(f"Certificate payload cannot be canonicalized: {exc}")
        return VerificationResult(is_valid=False, status="INVALID_FORMAT",
                                  reasons=tuple(reasons))
    if not hmac.compare_digest(recorded_digest.encode("utf-8", "surrogatepass"),
                               expected_digest.encode("utf-8")):
        reasons.append(
            f"Digest mismatch! Recorded digest '{recorded_digest}' does not match computed '{expected_digest}'."
        )
        return VerificationResult(
            is_valid=False,
            status="TAMPERED",
            reasons=tuple(reasons),
        )

    # Construct typed certificate
    try:
        cert = cert_from_dict(data)
    except (TypeError, ValueError) as exc:
        reasons.append(f"Certificate fields cannot be read: {exc}")
        return VerificationResult(is_valid=False, status="INVALID_FORMAT",
                                  reasons=tuple(reasons))
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
        if cert.scope and cert.scope not in terms.scopes:
            reasons.append(
                f"Scope '{cert.scope}' is not defined by {terms.key}; "
                f"allowed: {', '.join(terms.scopes)}."
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
        register_file = Path(register_path)
        if not register_file.is_file():
            reasons.append(
                f"Cannot read the certificate register: {register_file} does not exist."
            )
            return VerificationResult(is_valid=False, status="INVALID_FORMAT",
                                      reasons=tuple(reasons), cert=cert)
        try:
            entry = load_register(register_file).get(cert.cert_id)
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
            if not _ISO_DATE.fullmatch(cert.expires_at) or not _ISO_DATE.fullmatch(ref_str):
                raise ValueError("dates must use YYYY-MM-DD")
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
