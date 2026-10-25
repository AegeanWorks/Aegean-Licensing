"""Aegean License texts and public certificate verification (issuing is private, ADR-017)."""

__version__ = "0.1.0"
__author__ = "AegeanWorks"
__email__ = "aegean-licensing@proton.me"

from aegean_licensing.cert import LicenseCertificate
from aegean_licensing.verifier import verify_certificate, VerificationResult

__all__ = [
    "LicenseCertificate",
    "verify_certificate",
    "VerificationResult",
    "__version__",
]
