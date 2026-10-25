"""Public certificate register: which certificates AegeanWorks issued, and which it revoked (ADR-013).

HMAC signatures can be checked only with the signing key, so publishing that key would let anyone
forge a certificate. The register is the public proof instead: `licenses/issued.json` lists each
issued certificate's id, digest, license type, issue date and status, and nothing that identifies
the licensee. A certificate whose digest is in the register, and not revoked, was issued by
AegeanWorks. This package only reads the register; AegeanWorks writes it with its private
operations tooling (ADR-017).
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Dict, Union

REGISTER_VERSION = 1
DEFAULT_REGISTER_PATH = Path("licenses") / "issued.json"
STATUS_VALID = "valid"
STATUS_REVOKED = "revoked"


@dataclasses.dataclass(frozen=True)
class RegisterEntry:
    """One issued certificate, as the public may see it."""

    cert_id: str
    digest: str
    license_type: str
    issued_at: str
    status: str = STATUS_VALID
    revoked_at: str = ""
    reason: str = ""


def load_register(path: Union[str, Path]) -> Dict[str, RegisterEntry]:
    """Every entry keyed by certificate id; a missing register is empty."""
    target = Path(path)
    if not target.is_file():
        return {}
    with open(target, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or data.get("version") != REGISTER_VERSION:
        version = data.get("version") if isinstance(data, dict) else None
        raise ValueError(f"Unsupported register version {version!r} in {path}.")
    raw = data.get("certificates")
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must hold a 'certificates' object.")
    try:
        return {cert_id: RegisterEntry(cert_id=cert_id, **fields) for cert_id, fields in raw.items()}
    except TypeError as exc:
        raise ValueError(f"{path} has a malformed certificate entry: {exc}") from exc
