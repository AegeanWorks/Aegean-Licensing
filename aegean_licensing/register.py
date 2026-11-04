"""Public certificate register: which certificates AegeanWorks issued, and which it revoked (ADR-013).

HMAC signatures can be checked only with the signing key, so publishing that key would let anyone
forge a certificate. The register is the public proof instead: `licenses/issued.json` lists each
issued certificate's id, digest, license type, issue date and status, and nothing that identifies
the licensee. A certificate whose digest is in the register, and not revoked, was issued by
AegeanWorks. This package only reads the register; AegeanWorks writes it with its private
operations tooling (ADR-017).

Register version 2 adds a `generated_at`/`next_update` freshness window and typed revocation
details. Version 1 is still readable, but it has no freshness evidence and is reported as
`UNDATED_REGISTER` by the verifier. Old readers reject version 2 before reading an entry, which
fails closed instead of silently ignoring a new field.
"""

from __future__ import annotations

import dataclasses
import datetime
import re
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from aegean_licensing.bounded_json import load_bounded

REGISTER_VERSION = 2
SUPPORTED_REGISTER_VERSIONS = (1, 2)
DEFAULT_REGISTER_PATH = Path("licenses") / "issued.json"
MAX_FRESHNESS_WINDOW = datetime.timedelta(days=366)
CLOCK_SKEW = datetime.timedelta(minutes=5)
STATUS_VALID = "valid"
STATUS_REVOKED = "revoked"
# Any other status is not a state this package understands; treating it as valid would let a
# malformed or tampered register hide a revocation.
_STATUSES = (STATUS_VALID, STATUS_REVOKED)
# A certificate digest is a SHA-256 hex digest; any other JSON value would make compare_digest
# raise TypeError instead of reporting the register as malformed.
_DIGEST = re.compile(r"[0-9a-f]{64}")
_ISO_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_TEXT_FIELDS = ("license_type", "issued_at", "revoked_at", "reason", "reason_code",
                "invalidity_date")
# A closed vocabulary keeps the public reason machine-readable. Only a key compromise may carry
# an invalidity date before the publication of the revocation; the other codes are prospective.
REVOCATION_REASON_CODES = (
    "key-compromise",
    "non-payment",
    "breach",
    "superseded",
    "voluntary",
    "other",
)
RETROACTIVE_REASON_CODES = ("key-compromise",)


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
    reason_code: str = ""
    invalidity_date: str = ""


@dataclasses.dataclass(frozen=True)
class RegisterDocument:
    """The register file, including the freshness window that bounds its revocation view."""

    version: int
    generated_at: str
    next_update: str
    entries: Dict[str, RegisterEntry]

    def freshness(self, moment: datetime.datetime) -> Tuple[bool, str]:
        """Whether the register is fresh at `moment`; a missing window is not fresh."""
        if getattr(moment, "tzinfo", None) is None:
            raise ValueError("freshness moment must be a timezone-aware datetime")
        if not self.generated_at or not self.next_update:
            return False, "the register has no generated_at/next_update freshness metadata"
        generated = _parse_timestamp(self.generated_at, "generated_at")
        next_update = _parse_timestamp(self.next_update, "next_update")
        if moment < generated - CLOCK_SKEW:
            return False, f"the register was generated at {self.generated_at}, after the check time"
        if moment > next_update:
            return False, f"the register freshness window ended at {self.next_update}"
        return True, ""


def _parse_timestamp(value: str, field: str) -> datetime.datetime:
    if not isinstance(value, str) or not _ISO_TIMESTAMP.fullmatch(value):
        raise ValueError(f"Register {field} must be a UTC timestamp like 2026-10-30T12:00:00Z.")
    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=datetime.timezone.utc)


def _parse_date(value: str, field: str) -> datetime.date:
    if not isinstance(value, str) or not _ISO_DATE.fullmatch(value):
        raise ValueError(f"Register {field} must be a date like 2026-10-30.")
    return datetime.date.fromisoformat(value)


def load_register_document(path: Union[str, Path]) -> RegisterDocument:
    """Read the register and its freshness window; a missing file is an empty v2 document."""
    target = Path(path)
    if not target.is_file():
        return RegisterDocument(REGISTER_VERSION, "", "", {})
    data = load_bounded(target)
    # bool is an int subclass, so True/False must be rejected explicitly: True == 1 would
    # otherwise load as register version 1.
    if type(data.get("version")) is not int or data.get("version") not in SUPPORTED_REGISTER_VERSIONS:
        version = data.get("version") if isinstance(data, dict) else None
        raise ValueError(f"Unsupported register version {version!r} in {path}.")
    version = data["version"]
    generated_at = data.get("generated_at", "")
    next_update = data.get("next_update", "")
    if version == REGISTER_VERSION:
        if not generated_at or not next_update:
            raise ValueError(
                f"{path} is a version-2 register but lacks generated_at/next_update.")
        generated = _parse_timestamp(generated_at, "generated_at")
        update = _parse_timestamp(next_update, "next_update")
        if update <= generated:
            raise ValueError(f"{path} has next_update at or before generated_at.")
        if update - generated > MAX_FRESHNESS_WINDOW:
            raise ValueError(
                f"{path} has a freshness window longer than {MAX_FRESHNESS_WINDOW.days} days.")
    elif generated_at or next_update:
        raise ValueError(f"{path} is a version-1 register but carries freshness metadata.")
    raw = data.get("certificates")
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must hold a 'certificates' object.")
    entries: Dict[str, RegisterEntry] = {}
    for cert_id, fields in raw.items():
        if not isinstance(cert_id, str) or not cert_id.strip():
            raise ValueError(f"{path} has a malformed certificate entry id {cert_id!r}.")
        if not isinstance(fields, dict):
            raise ValueError(f"{path} has a malformed certificate entry for {cert_id}.")
        try:
            entry = RegisterEntry(cert_id=cert_id, **fields)
        except TypeError as exc:
            raise ValueError(f"{path} has a malformed certificate entry: {exc}") from exc
        non_text = [name for name in _TEXT_FIELDS if not isinstance(getattr(entry, name), str)]
        if non_text:
            raise ValueError(f"{path} gives certificate {cert_id} non-text {', '.join(non_text)}.")
        if not isinstance(entry.digest, str) or not _DIGEST.fullmatch(entry.digest):
            raise ValueError(f"{path} gives certificate {cert_id} an invalid digest.")
        if not entry.license_type.strip():
            raise ValueError(f"{path} gives certificate {cert_id} an empty license_type.")
        _parse_date(entry.issued_at, f"issued_at for {cert_id}")
        if entry.status not in _STATUSES:
            raise ValueError(
                f"{path} gives certificate {cert_id} an unknown status {entry.status!r}; "
                f"only {', '.join(_STATUSES)} are understood."
            )
        if version == 1 and (entry.reason_code or entry.invalidity_date):
            raise ValueError(
                f"{path} gives a version-1 certificate {cert_id} version-2 fields.")
        if entry.revoked_at:
            _parse_date(entry.revoked_at, f"revoked_at for {cert_id}")
        if version == REGISTER_VERSION and entry.status == STATUS_REVOKED and not entry.revoked_at:
            raise ValueError(f"{path} gives revoked certificate {cert_id} no revoked_at date.")
        if entry.status == STATUS_VALID and (
                entry.revoked_at or entry.reason or entry.reason_code or entry.invalidity_date):
            raise ValueError(
                f"{path} gives valid certificate {cert_id} revocation-only fields.")
        if entry.reason_code and entry.reason_code not in REVOCATION_REASON_CODES:
            raise ValueError(
                f"{path} gives certificate {cert_id} an unknown reason_code "
                f"{entry.reason_code!r}; allowed: {', '.join(REVOCATION_REASON_CODES)}.")
        if entry.invalidity_date:
            if entry.reason_code not in RETROACTIVE_REASON_CODES:
                raise ValueError(
                    f"{path} gives certificate {cert_id} an invalidity_date for a non-retroactive "
                    f"reason_code {entry.reason_code!r}.")
            invalidity = _parse_date(entry.invalidity_date, f"invalidity_date for {cert_id}")
            revoked = _parse_date(entry.revoked_at, f"revoked_at for {cert_id}")
            if invalidity > revoked:
                raise ValueError(
                    f"{path} gives certificate {cert_id} an invalidity_date after revoked_at.")
        entries[cert_id] = entry
    return RegisterDocument(version, generated_at, next_update, entries)


def load_register(path: Union[str, Path]) -> Dict[str, RegisterEntry]:
    """Every entry keyed by certificate id; a missing register is empty."""
    return load_register_document(path).entries


def entry_effective_date(entry: RegisterEntry) -> Optional[str]:
    """The date a revocation takes effect: its recorded invalidity date, else the publication date."""
    if entry.status != STATUS_REVOKED:
        return None
    return entry.invalidity_date or entry.revoked_at or None
