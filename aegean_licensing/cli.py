"""AegeanWorks Licensing Command-Line Interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from aegean_licensing import __version__
from aegean_licensing.auditor import audit_repository
from aegean_licensing.cert import cert_to_dict, cert_to_markdown
from aegean_licensing.issuer import issue_certificate
from aegean_licensing.templates import (
    get_asset_policy,
    get_backward_compatibility_policy,
    get_commercial_agreement_template,
    get_commercial_md,
    get_contributor_cla,
    get_dual_license_rider,
    get_personal_use_license,
    get_pyproject_snippet,
)
from aegean_licensing.verifier import verify_certificate


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aegean-license",
        description="AegeanWorks Commercial Licensing, Certificate Generation & Verification Tool.",
    )
    parser.add_argument("--version", action="version", version=f"aegean-license {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available subcommands")

    # 1. Issue
    p_issue = subparsers.add_parser("issue", help="Generate a commercial license certificate.")
    p_issue.add_argument("--licensee", required=True, help="Legal name of licensee individual or organization.")
    p_issue.add_argument("--contact", required=True, help="Contact email of licensee.")
    p_issue.add_argument(
        "--type",
        dest="license_type",
        default="AECL-1.0",
        help="License agreement type (default: 'AECL-1.0', or e.g. 'ACLA-1.0-Tier1', 'ACLA-1.0-Enterprise').",
    )
    p_issue.add_argument(
        "--projects",
        default="*",
        help="Comma-separated project names (e.g. 'chronos,AIKit') or '*' for portfolio-wide.",
    )
    p_issue.add_argument(
        "--scope",
        default="proprietary-saas-and-redistribution",
        help="Commercial scope (default: 'proprietary-saas-and-redistribution').",
    )
    p_issue.add_argument("--expires", default=None, help="Optional expiration date (YYYY-MM-DD).")
    p_issue.add_argument("--term-limited", action="store_true", help="Mark license as non-perpetual.")
    p_issue.add_argument("--key", default=None, help="Optional secret key to generate HMAC signature.")
    p_issue.add_argument("--notes", default="", help="Optional notes or reference transaction ID.")
    p_issue.add_argument("--output-dir", default=None, help="Directory to save certificate .json and .md files.")

    # 2. Verify
    p_verify = subparsers.add_parser("verify", help="Verify authenticity and validity of a certificate.")
    p_verify.add_argument("path", help="Path to certificate JSON file.")
    p_verify.add_argument("--key", default=None, help="Optional secret key to verify HMAC signature.")
    p_verify.add_argument("--project", default=None, help="Check if specific project is covered by certificate.")
    p_verify.add_argument("--date", default=None, help="Reference date (YYYY-MM-DD) for expiration check.")

    # 3. Audit
    p_audit = subparsers.add_parser("audit", help="Audit repository for dual-licensing compliance.")
    p_audit.add_argument("path", nargs="?", default=".", help="Repository root directory (default: current directory).")
    p_audit.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    p_audit.add_argument(
        "--check-policies",
        action="store_true",
        help="Also verify presence of CLA, asset policy, and backward-compat policy.",
    )

    # 4. Template
    p_template = subparsers.add_parser("template", help="Output or write standard licensing templates.")
    p_template.add_argument(
        "kind",
        choices=[
            "rider",
            "commercial",
            "pyproject",
            "al-pu",
            "acla",
            "cla",
            "asset-policy",
            "backward-compat",
            "all",
        ],
        help="Template to generate: 'rider', 'commercial', 'pyproject', 'al-pu', 'acla', 'cla', 'asset-policy', 'backward-compat', or 'all'.",
    )
    p_template.add_argument(
        "--output-dir",
        default=None,
        help="Optional directory to write generated template files.",
    )

    return parser


def _handle_issue(args: argparse.Namespace) -> int:
    projects_list = [p.strip() for p in args.projects.split(",") if p.strip()]
    is_perpetual = not args.term_limited and args.expires is None

    try:
        cert = issue_certificate(
            licensee_name=args.licensee,
            licensee_contact=args.contact,
            license_type=args.license_type,
            projects=projects_list,
            scope=args.scope,
            is_perpetual=is_perpetual,
            expires_at=args.expires,
            notes=args.notes,
            secret_key=args.key,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        print(f"Error: Failed to issue certificate: {exc}", file=sys.stderr)
        return 1

    print("==========================================================")
    print("AEGEANWORKS COMMERCIAL LICENSE CERTIFICATE")
    print("==========================================================")
    print(f"Certificate ID : {cert.cert_id}")
    print(f"Licensee       : {cert.licensee_name} <{cert.licensee_contact}>")
    print(f"Projects       : {', '.join(cert.projects)}")
    print(f"Scope          : {cert.scope}")
    print(f"Issued At      : {cert.issued_at}")
    print(f"Expires        : {cert.expires_at or 'Perpetual'}")
    print(f"Digest (SHA256): {cert.digest}")
    if cert.signature:
        print(f"Signature (HMAC): {cert.signature}")
    if args.output_dir:
        print(f"Saved to       : {Path(args.output_dir).resolve()}")
    print("==========================================================")
    return 0


def _handle_verify(args: argparse.Namespace) -> int:
    result = verify_certificate(
        target=args.path,
        secret_key=args.key,
        check_project=args.project,
        reference_date=args.date,
    )

    print("==========================================================")
    print("AEGEANWORKS CERTIFICATE VERIFICATION")
    print("==========================================================")
    print(f"Target : {args.path}")
    print(f"Status : {result.status}")

    if result.cert:
        print(f"ID     : {result.cert.cert_id}")
        print(f"Holder : {result.cert.licensee_name}")
        print(f"Scope  : {result.cert.scope}")
        print(f"Covered: {', '.join(result.cert.projects)}")

    if result.is_valid:
        print("[PASS] Certificate is authentic, untampered, and currently valid.")
        print("==========================================================")
        return 0

    print(f"[FAIL] Certificate validation failed: {result.status}")
    for reason in result.reasons:
        print(f"  - {reason}")
    print("==========================================================")
    return 1


def _handle_audit(args: argparse.Namespace) -> int:
    report = audit_repository(args.path, check_policies=args.check_policies)

    print("==========================================================")
    print(f"AEGEANWORKS DUAL-LICENSING AUDIT: {report.repo_path}")
    print("==========================================================")

    for check in report.passed_checks:
        print(f"[PASS] {check}")

    for warn in report.warnings:
        print(f"[WARN] {warn}")

    for fail in report.failed_checks:
        print(f"[FAIL] {fail}")

    print("----------------------------------------------------------")
    if report.is_compliant and (not args.strict or len(report.warnings) == 0):
        print("[OK] Repository complies with AegeanWorks dual-licensing standards.")
        print("==========================================================")
        return 0

    print("[FAIL] Compliance audit detected issues.")
    if report.fixes:
        print("\nActionable Fixes:")
        for fix in report.fixes:
            print(f"  * {fix}")
    print("==========================================================")
    return 1


def _handle_template(args: argparse.Namespace) -> int:
    out_dir = Path(args.output_dir) if args.output_dir else None

    templates_map = {
        "rider": ("DUAL_LICENSE_NOTICE.txt", get_dual_license_rider()),
        "commercial": ("COMMERCIAL.md", get_commercial_md()),
        "pyproject": ("pyproject_snippet.toml", get_pyproject_snippet()),
        "al-pu": ("AL-PU-1.0-DRAFT.md", get_personal_use_license()),
        "acla": ("COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md", get_commercial_agreement_template()),
        "cla": ("CONTRIBUTING_CLA.md", get_contributor_cla()),
        "asset-policy": ("ASSET_POLICY.md", get_asset_policy()),
        "backward-compat": ("BACKWARD-COMPATIBILITY-DRAFT.md", get_backward_compatibility_policy()),
    }

    if args.kind in templates_map:
        filename, content = templates_map[args.kind]
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)
            target_path = out_dir / filename
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Wrote {target_path}")
        else:
            print(content)
    elif args.kind == "all":
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)
            for fname, content in templates_map.values():
                target_path = out_dir / fname
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Wrote {target_path}")
        else:
            for fname, content in templates_map.values():
                print(f"=== {fname} ===")
                print(content)

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "issue":
        return _handle_issue(args)
    elif args.command == "verify":
        return _handle_verify(args)
    elif args.command == "audit":
        return _handle_audit(args)
    elif args.command == "template":
        return _handle_template(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
