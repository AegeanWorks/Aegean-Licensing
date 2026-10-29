"""Canonical license registry: the types, scopes, tiers, and term digests a certificate may cite."""

from __future__ import annotations

import dataclasses
import hashlib
from pathlib import Path
from typing import Dict, Optional

from aegean_licensing.bounded_json import load_bounded

REGISTRY_VERSION = 1
REGISTRY_RELATIVE_PATH = Path("licenses") / "terms.json"


@dataclasses.dataclass(frozen=True)
class LicenseTerms:
    """One operative license agreement and the vocabulary its certificates may use."""

    key: str
    name: str
    document: str
    status: str
    sha256: str
    scopes: tuple
    tiers: tuple
    # Exceptions the agreement grants only when a certificate lists them (ACL-1.0 3.9, 3.10).
    allowances: tuple = ()

    @property
    def is_operative(self) -> bool:
        return self.status == "operative"


def _registry_paths() -> tuple:
    package_dir = Path(__file__).resolve().parent
    return (package_dir.parent / REGISTRY_RELATIVE_PATH,
            package_dir / "resources" / REGISTRY_RELATIVE_PATH)


def _load_registry_document() -> Dict[str, object]:
    for candidate in _registry_paths():
        if candidate.is_file():
            data = load_bounded(candidate)
            if not isinstance(data, dict):
                raise ValueError(f"{candidate} must contain a JSON object.")
            return data
    raise ValueError(
        "License registry (licenses/terms.json) is missing; run from the repository or install a "
        "wheel that bundles it."
    )


def load_registry() -> Dict[str, LicenseTerms]:
    """Return every registered license keyed by its canonical name."""
    data = _load_registry_document()
    version = data.get("version")
    if version != REGISTRY_VERSION:
        raise ValueError(
            f"Unsupported license registry version {version!r}; this tool reads version "
            f"{REGISTRY_VERSION}."
        )
    raw_licenses = data.get("licenses")
    if not isinstance(raw_licenses, dict) or not raw_licenses:
        raise ValueError("License registry 'licenses' must be a non-empty JSON object.")
    registry: Dict[str, LicenseTerms] = {}
    for raw_key, raw in raw_licenses.items():
        if not isinstance(raw, dict):
            raise ValueError(f"License '{raw_key}' must be a JSON object.")
        key = str(raw_key).strip()
        scopes = raw.get("scopes")
        tiers = raw.get("tiers", [])
        if not isinstance(scopes, list) or not scopes or not all(isinstance(s, str) for s in scopes):
            raise ValueError(f"License '{key}' requires a non-empty 'scopes' list.")
        if not isinstance(tiers, list) or not all(isinstance(t, str) for t in tiers):
            raise ValueError(f"License '{key}' has an invalid 'tiers' list.")
        allowances = raw.get("allowances", [])
        if not isinstance(allowances, list) or not all(isinstance(a, str) for a in allowances):
            raise ValueError(f"License '{key}' has an invalid 'allowances' list.")
        registry[key] = LicenseTerms(
            key=key,
            name=str(raw.get("name", key)),
            document=str(raw.get("document", "")),
            status=str(raw.get("status", "draft")),
            sha256=str(raw.get("sha256", "")).lower(),
            scopes=tuple(scopes),
            tiers=tuple(tiers),
            allowances=tuple(allowances),
        )
    return registry


def resolve_license(key: str, require_operative: bool = True) -> LicenseTerms:
    """Look up a license key, refusing unknown or non-operative agreements."""
    registry = load_registry()
    normalized = str(key).strip()
    for candidate_key, terms in registry.items():
        if candidate_key.lower() == normalized.lower():
            if require_operative and not terms.is_operative:
                raise ValueError(
                    f"License '{terms.key}' is not operative; certificates may cite only an "
                    f"operative agreement."
                )
            return terms
    raise ValueError(
        f"Unknown license type '{key}'. Known types: {', '.join(sorted(registry))}."
    )


def normalize_document_text(text: str) -> str:
    """Normalize line endings before hashing so a checkout's EOL style cannot change the digest."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def compute_terms_digest(document_text: str) -> str:
    """Return the SHA-256 of a license document's normalized UTF-8 text."""
    normalized = normalize_document_text(document_text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _document_paths(document: str) -> tuple:
    package_dir = Path(__file__).resolve().parent
    return (package_dir.parent / document, package_dir / "resources" / document)


def read_license_document(terms: LicenseTerms) -> str:
    """Read the operative agreement text from the checkout or the packaged resources."""
    if not terms.document:
        raise ValueError(f"License {terms.key} does not name a document.")
    for candidate in _document_paths(terms.document):
        if candidate.is_file():
            with open(candidate, "r", encoding="utf-8") as handle:
                return handle.read()
    raise ValueError(
        f"License document '{terms.document}' for {terms.key} is missing; run from the "
        f"repository or install a wheel that bundles it."
    )


def terms_digest(terms: LicenseTerms) -> str:
    """
    Return the digest of the agreement text a certificate must cite. An agreement whose text no
    longer matches the sha256 pinned in terms.json was edited after release: certificates already
    cite the old text, so it is refused (ADR-013).
    """
    digest = compute_terms_digest(read_license_document(terms))
    if terms.sha256 and digest != terms.sha256:
        raise ValueError(
            f"{terms.document} no longer matches the sha256 pinned for {terms.key} in terms.json; "
            f"an issued agreement is frozen, so publish changed terms as a new version."
        )
    return digest
