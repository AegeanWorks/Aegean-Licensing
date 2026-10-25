"""Repository Dual-Licensing Compliance Auditor."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import List, Optional, Sequence, Union


@dataclasses.dataclass(frozen=True)
class AuditReport:
    """Detailed compliance report for an audited repository."""

    repo_path: str
    is_compliant: bool
    passed_checks: tuple[str, ...]
    failed_checks: tuple[str, ...]
    warnings: tuple[str, ...]
    fixes: tuple[str, ...]


def audit_repository(repo_dir: Union[str, Path], check_policies: bool = False) -> AuditReport:
    """Inspect repository files for compliance with AegeanWorks dual-licensing standards."""
    target = Path(repo_dir).resolve()
    if not target.exists() or not target.is_dir():
        return AuditReport(
            repo_path=str(target),
            is_compliant=False,
            passed_checks=(),
            failed_checks=(f"Repository path does not exist or is not a directory: {target}",),
            warnings=(),
            fixes=("Provide a valid directory path to an AegeanWorks project.",),
        )

    passed: List[str] = []
    failed: List[str] = []
    warnings: List[str] = []
    fixes: List[str] = []

    # 1. Check LICENSE
    license_file = target / "LICENSE"
    if not license_file.exists():
        failed.append("Missing LICENSE file.")
        fixes.append("Add GNU AGPL-3.0 or AL-PU-1.0 LICENSE with AegeanWorks Dual-Licensing rider.")
    else:
        try:
            with open(license_file, "r", encoding="utf-8", errors="replace") as f:
                license_content = f.read()

            is_agpl = "GNU AFFERO GENERAL PUBLIC LICENSE" in license_content
            is_alpu = "PERSONAL USE LICENSE" in license_content.upper() or "AL-PU" in license_content.upper()

            if is_agpl:
                passed.append("LICENSE contains GNU AGPL-3.0 base.")
                if "dual-licensing notice" not in license_content.lower() or "aegean-licensing@proton.me" not in license_content.lower():
                    failed.append("LICENSE is missing AegeanWorks Dual-Licensing notice rider.")
                    fixes.append("Append AegeanWorks Dual-Licensing Notice to bottom of LICENSE.")
                else:
                    passed.append("LICENSE contains valid Dual-Licensing rider.")
            elif is_alpu:
                passed.append("LICENSE contains Aegean Licensing Personal Use (AL-PU) base.")
                if "aegean-licensing@proton.me" not in license_content.lower():
                    warnings.append("AL-PU LICENSE does not list 'aegean-licensing@proton.me' contact.")
                    fixes.append("Ensure commercial licensing contact 'aegean-licensing@proton.me' is listed in LICENSE.")
                else:
                    passed.append("AL-PU LICENSE contains commercial licensing contact.")
            else:
                failed.append("LICENSE file is missing an approved AegeanWorks license base (AGPL-3.0 or AL-PU).")
                fixes.append("Ensure LICENSE begins with full GNU AGPL-3.0 or AL-PU-1.0 license text.")
        except Exception as exc:
            failed.append(f"Failed to read LICENSE file: {exc}")

    # 2. Check COMMERCIAL.md
    comm_file = target / "COMMERCIAL.md"
    if not comm_file.exists():
        failed.append("Missing COMMERCIAL.md file.")
        fixes.append("Add COMMERCIAL.md documenting AGPL vs AECL tracks and Exhibit A terms.")
    else:
        try:
            with open(comm_file, "r", encoding="utf-8", errors="replace") as f:
                comm_content = f.read()

            if "AECL" not in comm_content and "Commercial License" not in comm_content:
                failed.append("COMMERCIAL.md does not describe Aegean-E Commercial License (AECL).")
                fixes.append("Update COMMERCIAL.md with official AECL framework details.")
            else:
                passed.append("COMMERCIAL.md describes AECL track.")

            if "Exhibit A" not in comm_content and "Standard AECL Terms" not in comm_content:
                warnings.append("COMMERCIAL.md does not contain Exhibit A binding standard terms.")
                fixes.append("Include Exhibit A Standard AECL Terms in COMMERCIAL.md.")
            else:
                passed.append("COMMERCIAL.md contains binding standard terms (Exhibit A).")

            # Check for obsolete enterprise bureaucracy terms
            bureaucracy_terms = ["W-9", "Master Services Agreement", "Net-30", "SLA guarantee"]
            detected_bureaucracy = [term for term in bureaucracy_terms if term.lower() in comm_content.lower()]
            if detected_bureaucracy:
                warnings.append(
                    f"COMMERCIAL.md contains obsolete enterprise bureaucracy terms: {', '.join(detected_bureaucracy)}"
                )
                fixes.append("Remove enterprise bureaucracy clauses (MSAs, W-9s, Net-30, SLAs) from COMMERCIAL.md.")
            else:
                passed.append("COMMERCIAL.md is free from enterprise bureaucracy jargon.")
        except Exception as exc:
            failed.append(f"Failed to read COMMERCIAL.md: {exc}")

    # 3. Check pyproject.toml if present
    pyproject_file = target / "pyproject.toml"
    if pyproject_file.exists():
        try:
            with open(pyproject_file, "r", encoding="utf-8", errors="replace") as f:
                pyproj_content = f.read()

            if "aegean-licensing@proton.me" not in pyproj_content:
                failed.append("pyproject.toml does not list 'aegean-licensing@proton.me' in authors.")
                fixes.append("Set author email to 'aegean-licensing@proton.me' in pyproject.toml.")
            else:
                passed.append("pyproject.toml has correct author contact.")

            has_valid_author = "AegeanWorks" in pyproj_content or "Aegean-E" in pyproj_content
            if not has_valid_author:
                failed.append("pyproject.toml does not list 'AegeanWorks' or 'Aegean-E' as author.")
                fixes.append("Set author name to 'AegeanWorks' in pyproject.toml.")
            else:
                passed.append("pyproject.toml names valid AegeanWorks author.")

            if "AGPL-3.0" not in pyproj_content:
                warnings.append("pyproject.toml license field does not reference AGPL-3.0.")
                fixes.append("Set license = { text = 'AGPL-3.0-or-later' } in pyproject.toml.")
            else:
                passed.append("pyproject.toml specifies AGPL-3.0 license.")
        except Exception as exc:
            failed.append(f"Failed to read pyproject.toml: {exc}")

    # 4. Check policies if requested
    if check_policies:
        cla_found = (target / "licenses" / "CONTRIBUTING_CLA.md").exists() or (target / "CONTRIBUTING_CLA.md").exists()
        if cla_found:
            passed.append("Contributor License Agreement (CLA) found.")
        else:
            warnings.append("Missing Contributor License Agreement (CONTRIBUTING_CLA.md).")
            fixes.append("Add CONTRIBUTING_CLA.md to establish clear inbound licensing rights.")

        asset_found = (target / "licenses" / "ASSET_POLICY.md").exists() or (target / "ASSET_POLICY.md").exists()
        if asset_found:
            passed.append("Asset Separation Policy (ASSET_POLICY.md) found.")
        else:
            warnings.append("Missing Asset Separation Policy (ASSET_POLICY.md).")
            fixes.append("Add ASSET_POLICY.md to demarcate code from creative/clinical assets.")

        backward_found = (target / "policies" / "BACKWARD-COMPATIBILITY-DRAFT.md").exists() or (target / "BACKWARD-COMPATIBILITY-DRAFT.md").exists()
        if backward_found:
            passed.append("Backward Compatibility Policy found.")
        else:
            warnings.append("Missing Backward Compatibility Policy (BACKWARD-COMPATIBILITY-DRAFT.md).")
            fixes.append("Add BACKWARD-COMPATIBILITY-DRAFT.md to clarify non-retroactivity of license updates.")

    is_compliant = len(failed) == 0

    return AuditReport(
        repo_path=str(target),
        is_compliant=is_compliant,
        passed_checks=tuple(passed),
        failed_checks=tuple(failed),
        warnings=tuple(warnings),
        fixes=tuple(fixes),
    )
