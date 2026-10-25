"""Test-only certificate builder (ADR-017).

The issuing tool is private to AegeanWorks; these tests build certificates straight from the
public data model, so the verifier is tested against exactly the format it reads. A certificate
built here is not in the public register, which is the whole point of the register.
"""

import json
import secrets
import uuid
from pathlib import Path

from aegean_licensing.cert import cert_from_dict, compute_digest, compute_signature
from aegean_licensing.license_terms import resolve_license, terms_digest


def issue_certificate(licensee_name, licensee_contact, license_type="ACL-1.0", projects=("*",),
                      scope="proprietary-saas-and-redistribution", is_perpetual=True,
                      expires_at=None, notes="", secret_key=None, cert_id=None,
                      issued_at="2026-10-25", tier="", allowances=()):
    terms = resolve_license(license_type)
    data = {
        "cert_id": cert_id or str(uuid.uuid4()),
        "licensee_name": licensee_name,
        "licensee_contact": licensee_contact,
        "issuer": "AegeanWorks",
        "issuer_contact": "aegean-licensing@proton.me",
        "license_type": terms.key,
        "projects": sorted(projects),
        "scope": scope,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "is_perpetual": is_perpetual,
        "notes": notes,
        "tier": tier,
        "terms_digest": terms_digest(terms),
        "licensee_address": "",
        "licensee_registration": "",
        "licensee_country": "",
        "allowances": sorted(allowances),
        "format": 2,
        "serial": secrets.token_hex(32),
    }
    data["digest"] = compute_digest(data)
    data["signature"] = compute_signature(data, secret_key) if secret_key else ""
    return cert_from_dict(data)


def write_register(path, *certs, revoked=()):
    """A register file listing `certs`, with the ids in `revoked` marked revoked."""
    entries = {}
    for cert in certs:
        entry = {"digest": cert.digest, "license_type": cert.license_type,
                 "issued_at": cert.issued_at, "status": "valid", "revoked_at": "", "reason": ""}
        if cert.cert_id in revoked:
            entry.update(status="revoked", revoked_at="2026-11-01", reason="terminated for breach")
        entries[cert.cert_id] = entry
    Path(path).write_text(json.dumps({"version": 1, "certificates": entries}), encoding="utf-8")
