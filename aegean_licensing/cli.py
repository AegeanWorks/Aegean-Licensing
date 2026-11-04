"""Aegean License Certificate verification command line (`aegean-license verify`)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
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
    date_group = p_verify.add_mutually_exclusive_group()
    date_group.add_argument("--date", default=None,
                            help="Reference date (YYYY-MM-DD) for the expiration check.")
    date_group.add_argument("--as-of", default=None, metavar="DATE",
                            help="Historical check: was the certificate valid on DATE? "
                                 "This is not a current authorization.")
    return parser


def _handle_verify(args: argparse.Namespace) -> int:
    # The signature is checked only by AegeanWorks' private `aegean-ops verify` (ADR-018).
    if args.register and not Path(args.register).is_file():
        print(f"Error: register file not found: {args.register}", file=sys.stderr)
        return 1
    try:
        result = verify_certificate(
            target=args.path,
            check_project=args.project,
            reference_date=args.date,
            register_path=args.register,
            as_of=args.as_of,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("==========================================================")
    print("AEGEAN CERTIFICATE VERIFICATION")
    print("==========================================================")
    print(f"Target : {args.path}")
    if args.as_of:
        print(f"Check  : as of {args.as_of} (historical, not a current authorization)")
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
        if result.registered:
            print("Listed : yes, in the public register")
        elif not args.register:
            print("Listed : not checked (no --register supplied)")
        else:
            print("Listed : no, not in the supplied register")
        if result.register_generated_at:
            print(f"Register: generated {result.register_generated_at}, "
                  f"next update {result.register_next_update}")

    if result.is_valid:
        if result.status == "VALID_AS_OF":
            print(f"[PASS] Certificate was valid as of {args.as_of}; it is NOT a current authorization.")
        elif result.registered:
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
