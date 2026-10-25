"""Aegean License Certificate verification command line (`aegean-license verify`)."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from aegean_licensing import __version__
from aegean_licensing.register import DEFAULT_REGISTER_PATH
from aegean_licensing.verifier import verify_certificate


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aegean-license",
        description="Verify an Aegean Commercial License certificate against the public register.",
    )
    parser.add_argument("--version", action="version", version=f"aegean-license {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available subcommands")

    p_verify = subparsers.add_parser("verify", help="Verify authenticity and validity of a certificate.")
    p_verify.add_argument("path", help="Path to certificate JSON file.")
    p_verify.add_argument(
        "--register",
        default=None,
        metavar="PATH",
        help=f"The public register of issued and revoked certificates ({DEFAULT_REGISTER_PATH.as_posix()} "
             "in the aegean-licensing repository).",
    )
    p_verify.add_argument("--project", default=None, help="Check if specific project is covered by certificate.")
    p_verify.add_argument("--date", default=None, help="Reference date (YYYY-MM-DD) for expiration check.")
    return parser


def _handle_verify(args: argparse.Namespace) -> int:
    # The signature is checked only by AegeanWorks' private `aegean-ops verify` (ADR-018).
    result = verify_certificate(
        target=args.path,
        check_project=args.project,
        reference_date=args.date,
        register_path=args.register,
    )

    print("==========================================================")
    print("AEGEAN CERTIFICATE VERIFICATION")
    print("==========================================================")
    print(f"Target : {args.path}")
    print(f"Status : {result.status}")

    if result.cert:
        license_line = result.cert.license_type
        if result.cert.tier:
            license_line += f" ({result.cert.tier})"
        terms_state = "text matches the bundled agreement" if result.terms_verified else "not verified"
        print(f"ID     : {result.cert.cert_id}")
        print(f"Holder : {result.cert.licensee_name}")
        print(f"License: {license_line}")
        print(f"Scope  : {result.cert.scope}")
        print(f"Allow  : {', '.join(result.cert.allowances) or 'none'}")
        print(f"Covered: {', '.join(result.cert.projects)}")
        print(f"Terms  : {terms_state}")
        print(f"Listed : {'yes, in the public register' if result.registered else 'not checked'}")

    if result.is_valid:
        if result.registered:
            print("[PASS] Certificate is listed in the public register, untampered, and currently valid.")
        else:
            print("[WARN] Certificate is structurally valid and tamper-evident, but its")
            print("       authenticity was NOT verified. The SHA-256 digest alone can be")
            print("       reproduced by anyone; re-run with --register licenses/issued.json.")
        print("==========================================================")
        return 0

    print(f"[FAIL] Certificate validation failed: {result.status}")
    for reason in result.reasons:
        print(f"  - {reason}")
    print("==========================================================")
    return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "verify":
        return _handle_verify(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
