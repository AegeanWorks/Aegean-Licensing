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
import re
from pathlib import Path
from typing import Dict, Union

from aegean_licensing.bounded_json import load_bounded

REGISTER_VERSION = 1
DEFAULT_REGISTER_PATH = Path("licenses") / "issued.json"
STATUS_VALID = "valid"
STATUS_REVOKED = "revoked"
# Any other status is not a state this package understands; treating it as valid would let a
# malformed or tampered register hide a revocation.
_STATUSES = (STATUS_VALID, STATUS_REVOKED)
# A certificate digest is a SHA-256 hex digest; any other JSON value would make compare_digest
# raise TypeError instead of reporting the register as malformed.
_DIGEST = re.compile(r"[0-9a-f]{64}")
_TEXT_FIELDS = ("license_type", "issued_at", "revoked_at", "reason")


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
    data = load_bounded(target)
    if not isinstance(data, dict) or data.get("version") != REGISTER_VERSION:
        version = data.get("version") if isinstance(data, dict) else None
        raise ValueError(f"Unsupported register version {version!r} in {path}.")
    raw = data.get("certificates")
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must hold a 'certificates' object.")
    entries: Dict[str, RegisterEntry] = {}
    for cert_id, fields in raw.items():
        try:
            entry = RegisterEntry(cert_id=cert_id, **fields)
        except TypeError as exc:
            raise ValueError(f"{path} has a malformed certificate entry: {exc}") from exc
        non_text = [name for name in _TEXT_FIELDS if not isinstance(getattr(entry, name), str)]
        if non_text:
            raise ValueError(f"{path} gives certificate {cert_id} non-text {', '.join(non_text)}.")
        if not isinstance(entry.digest, str) or not _DIGEST.fullmatch(entry.digest):
            raise ValueError(f"{path} gives certificate {cert_id} an invalid digest.")
        if entry.status not in _STATUSES:
            raise ValueError(
                f"{path} gives certificate {cert_id} an unknown status {entry.status!r}; "
                f"only {', '.join(_STATUSES)} are understood."
            )
        entries[cert_id] = entry
    return entries
