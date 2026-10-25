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
    p_verify.add_argument("--date", default=None, help="Reference date (YYYY-MM-DD) for expiration check.")
    signer_group = p_verify.add_mutually_exclusive_group()
    signer_group.add_argument("--key", default=None, help="Secret HMAC key, licensor only (prefer --key-file).")
    signer_group.add_argument("--key-file", default=None, metavar="PATH", help="File holding the signing key.")
    return parser


def _signing_key(args: argparse.Namespace) -> Optional[str]:
    """The key from --key-file (preferred, never in shell history) or --key."""
    if not args.key_file:
        return args.key
    try:
        return Path(args.key_file).read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError(f"Cannot read key file {args.key_file}: {exc}") from exc


def _handle_verify(args: argparse.Namespace) -> int:
    try:
        secret_key = _signing_key(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    result = verify_certificate(
        target=args.path,
        secret_key=secret_key,
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
        signed_state = "yes, verified with the supplied key" if result.signature_verified else "no"
        print(f"ID     : {result.cert.cert_id}")
        print(f"Holder : {result.cert.licensee_name}")
        print(f"License: {license_line}")
        print(f"Scope  : {result.cert.scope}")
        print(f"Allow  : {', '.join(result.cert.allowances) or 'none'}")
        print(f"Covered: {', '.join(result.cert.projects)}")
        print(f"Terms  : {terms_state}")
        print(f"Signed : {signed_state}")
        print(f"Listed : {'yes, in the public register' if result.registered else 'not checked'}")

    if result.is_valid:
        if result.signature_verified or result.registered:
            print("[PASS] Certificate is authentic, untampered, and currently valid.")
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
