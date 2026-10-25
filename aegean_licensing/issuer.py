"""Commercial License Certificate Issuance Module."""

from __future__ import annotations

import datetime
import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from aegean_licensing.cert import (
    LicenseCertificate,
    cert_from_dict,
    cert_to_dict,
    cert_to_markdown,
    compute_digest,
    compute_signature,
)


def _write_atomic(path: Path, content: str) -> None:
    """Write text to destination atomically using temp file, fsync, and replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = path.parent
    fd, temp_path_str = tempfile.mkstemp(dir=temp_dir, prefix=".cert_tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path_str, path)
    except Exception:
        if os.path.exists(temp_path_str):
            try:
                os.remove(temp_path_str)
            except OSError:  # hygiene: allow best-effort temporary file cleanup
                pass
        raise


def issue_certificate(
    licensee_name: str,
    licensee_contact: str,
    license_type: str = "AECL-1.0",
    projects: Sequence[str] = ("*",),
    scope: str = "proprietary-saas-and-redistribution",
    is_perpetual: bool = True,
    expires_at: Optional[str] = None,
    notes: str = "",
    secret_key: Optional[str] = None,
    cert_id: Optional[str] = None,
    issued_at: Optional[str] = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> LicenseCertificate:
    """Generate and return an authentic LicenseCertificate, optionally saving to disk."""
    if not licensee_name or not licensee_name.strip():
        raise ValueError("licensee_name must not be empty.")
    if not licensee_contact or not licensee_contact.strip():
        raise ValueError("licensee_contact must not be empty.")

    actual_id = cert_id or str(uuid.uuid4())
    actual_date = issued_at or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    data: Dict[str, Any] = {
        "cert_id": actual_id,
        "licensee_name": licensee_name.strip(),
        "licensee_contact": licensee_contact.strip(),
        "issuer": "AegeanWorks",
        "issuer_contact": "aegean-licensing@proton.me",
        "license_type": license_type.strip() or "AECL-1.0",
        "projects": list(projects) if projects else ["*"],
        "scope": scope.strip(),
        "issued_at": actual_date,
        "expires_at": expires_at,
        "is_perpetual": is_perpetual,
        "notes": notes.strip(),
    }

    digest = compute_digest(data)
    data["digest"] = digest

    if secret_key:
        signature = compute_signature(data, secret_key)
        data["signature"] = signature
    else:
        data["signature"] = ""

    cert = cert_from_dict(data)

    if output_dir:
        out_path = Path(output_dir)
        json_file = out_path / f"license_certificate_{actual_id}.json"
        md_file = out_path / f"license_certificate_{actual_id}.md"

        json_text = json.dumps(cert_to_dict(cert), indent=2, ensure_ascii=True) + "\n"
        md_text = cert_to_markdown(cert)

        _write_atomic(json_file, json_text)
        _write_atomic(md_file, md_text)

    return cert
