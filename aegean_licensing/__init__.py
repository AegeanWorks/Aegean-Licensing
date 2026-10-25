"""AegeanWorks Licensing Framework & Verification Tooling."""

__version__ = "0.1.0"
__author__ = "AegeanWorks"
__email__ = "aegean-licensing@proton.me"

from aegean_licensing.cert import LicenseCertificate
from aegean_licensing.issuer import issue_certificate
from aegean_licensing.verifier import verify_certificate, VerificationResult

__all__ = [
    "LicenseCertificate",
    "issue_certificate",
    "verify_certificate",
    "VerificationResult",
    "__version__",
]
