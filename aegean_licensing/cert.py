"""License Certificate Data Model and Cryptographic Hashing."""

from __future__ import annotations

import dataclasses
import hashlib
import hmac
import json
from typing import Any, Dict, List, Optional


@dataclasses.dataclass(frozen=True)
class LicenseCertificate:
    """Immutable data transfer object representing a granted commercial license."""

    cert_id: str
    licensee_name: str
    licensee_contact: str
    issuer: str = "AegeanWorks"
    issuer_contact: str = "aegean-licensing@proton.me"
    license_type: str = "ACL-1.0"
    projects: tuple[str, ...] = ("*",)
    scope: str = "proprietary-saas-and-redistribution"
    issued_at: str = ""
    expires_at: Optional[str] = None
    is_perpetual: bool = True
    notes: str = ""
    digest: str = ""
    signature: str = ""
    tier: str = ""
    terms_digest: str = ""
    licensee_address: str = ""
    licensee_registration: str = ""
    licensee_country: str = ""
    # Exceptions the agreement grants only by certificate, e.g. ai-training (ADR-014).
    allowances: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.projects, (list, tuple)):
            object.__setattr__(self, "projects", tuple(sorted(self.projects)))
        elif isinstance(self.projects, str):
            object.__setattr__(self, "projects", (self.projects,))
        object.__setattr__(self, "allowances", tuple(sorted(self.allowances)))


def compute_canonical_payload(data: Dict[str, Any]) -> bytes:
    """Serialize dictionary excluding digest and signature into deterministic UTF-8 bytes."""
    filtered = {
        k: v for k, v in data.items()
        if k not in ("digest", "signature")
    }
    # Ensure lists/tuples are sorted if appropriate or consistently ordered
    if "projects" in filtered and isinstance(filtered["projects"], (list, tuple)):
        filtered["projects"] = sorted(list(filtered["projects"]))
    return json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def compute_digest(data: Dict[str, Any]) -> str:
    """Compute SHA-256 digest of canonical license payload."""
    payload = compute_canonical_payload(data)
    return hashlib.sha256(payload).hexdigest()


def compute_signature(data: Dict[str, Any], secret_key: str) -> str:
    """Compute HMAC-SHA256 signature of canonical license payload using secret key."""
    payload = compute_canonical_payload(data)
    key_bytes = secret_key.encode("utf-8")
    return hmac.new(key_bytes, payload, hashlib.sha256).hexdigest()


def cert_to_dict(cert: LicenseCertificate) -> Dict[str, Any]:
    """Convert LicenseCertificate to dictionary representation."""
    d = dataclasses.asdict(cert)
    d["projects"] = list(cert.projects)
    d["allowances"] = list(cert.allowances)
    return d


def _allowance_tuple(raw: Any) -> tuple:
    """Allowances as a tuple; a lone string is one allowance, not a sequence of characters."""
    if not raw:
        return ()
    if isinstance(raw, str):
        return (raw,)
    return tuple(str(a) for a in raw)


def cert_from_dict(data: Dict[str, Any]) -> LicenseCertificate:
    """Construct LicenseCertificate from raw dictionary data."""
    projects_raw = data.get("projects", ["*"])
    if isinstance(projects_raw, list):
        projects = tuple(sorted(projects_raw))
    elif isinstance(projects_raw, tuple):
        projects = tuple(sorted(list(projects_raw)))
    elif isinstance(projects_raw, str):
        projects = (projects_raw,)
    else:
        projects = ("*",)

    return LicenseCertificate(
        cert_id=str(data.get("cert_id", "")),
        licensee_name=str(data.get("licensee_name", "")),
        licensee_contact=str(data.get("licensee_contact", "")),
        issuer=str(data.get("issuer", "AegeanWorks")),
        issuer_contact=str(data.get("issuer_contact", "aegean-licensing@proton.me")),
        license_type=str(data.get("license_type", "ACL-1.0")),
        projects=projects,
        scope=str(data.get("scope", "proprietary-saas-and-redistribution")),
        issued_at=str(data.get("issued_at", "")),
        expires_at=data.get("expires_at") if data.get("expires_at") else None,
        is_perpetual=bool(data.get("is_perpetual", True)),
        notes=str(data.get("notes", "")),
        digest=str(data.get("digest", "")),
        signature=str(data.get("signature", "")),
        tier=str(data.get("tier", "")),
        terms_digest=str(data.get("terms_digest", "")),
        licensee_address=str(data.get("licensee_address", "")),
        licensee_registration=str(data.get("licensee_registration", "")),
        licensee_country=str(data.get("licensee_country", "")),
        allowances=_allowance_tuple(data.get("allowances")),
    )
