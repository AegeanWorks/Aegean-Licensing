"""Canonical Licensing Templates and Boilerplate Generators."""

from __future__ import annotations

STANDARD_DUAL_LICENSE_RIDER = """---

### Dual-Licensing Notice

This software is dual-licensed by AegeanWorks:

1. **Open Source Track (AGPL-3.0-or-later)**:
   Free for personal, academic, research, and commercial use under the terms of
   the GNU Affero General Public License v3.0. Note that any distribution or
   remote network interaction (AGPL Section 13) requires complete source code
   disclosure under this license.

2. **Commercial License Track (Aegean-E Commercial License - AECL-1.0)**:
   Organizations wishing to integrate, modify, host closed-source SaaS, or
   redistribute this software without copyleft or source-disclosure obligations
   may obtain an Aegean-E Commercial License.

For commercial licensing inquiries, terms, and certificates:
- Inquiries: `aegean-licensing@proton.me`
- Full Details: [COMMERCIAL.md](COMMERCIAL.md)
"""

STANDARD_COMMERCIAL_MD = """# AegeanWorks Commercial Licensing

This repository is dual-licensed:

1. **Open-Source Track (AGPL-3.0)**: Free for all developers, teams, and commercial organizations who comply with copyleft obligations and provide source code for network-hosted modifications (AGPL Section 13).
2. **Commercial License Track (Aegean-E Commercial License - AECL-1.0)**: A paid, proprietary copyright grant for companies that require closed-source operations, proprietary SaaS deployments, or embedding without source-disclosure obligations.

---

## 1. Comparing the Tracks

| Dimension | AGPL-3.0 Open-Source | AECL-1.0 Commercial License |
|---|---|---|
| **Commercial Use** | Permitted under AGPL conditions | Full proprietary freedom |
| **Source Disclosure** | Mandatory for modified network services (Sec. 13) | Never required |
| **Proprietary SaaS Hosting** | Source must be offered to network users | Permitted closed-source |
| **Code Modification Rights** | Must be open-sourced under AGPL | Proprietary and confidential |
| **Warranty & Support** | As-is, no warranty, no support | As-is, pure IP grant, no support |

---

## 2. Creative & Non-Code Assets

Non-code assets (including 3D models, audio, proprietary datasets, and medical clinic workflow templates) are licensed separately for evaluation and personal use only. Commercial exploitation requires explicit licensing.

---

## 3. Contact & Licensing

To obtain an AECL-1.0 commercial license and verifiable digital certificate:
- **Email**: `aegean-licensing@proton.me`
- **Inquiry Details**: Include your company name, project(s) of interest, and deployment scale.

---

## Exhibit A: Standard AECL Terms

1. **Grant of Rights**: Licensor (AegeanWorks) grants Licensee a worldwide, non-exclusive, non-transferable right to use, modify, embed, host as a closed-source SaaS, and distribute the Licensed Software in proprietary applications without copyleft or source disclosure obligations under AGPL-3.0.
2. **Perpetual Production Rights**: All versions released during an active license term may be deployed in production perpetually.
3. **Pure Copyright Grant**: This license is strictly an intellectual property permissions grant and copyleft waiver.
4. **No Technical Support**: Licensor undertakes no obligation to provide maintenance, technical support, engineering, or SLAs.
5. **AS-IS Disclaimer**: THE SOFTWARE IS PROVIDED AS-IS WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
6. **Limitation of Liability**: IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY CLAIM, DAMAGES, OR LIABILITY ARISING FROM USE OF THE SOFTWARE.
"""

PYPROJECT_SNIPPET = """[project]
authors = [
    { name = "AegeanWorks", email = "aegean-licensing@proton.me" }
]
license = { text = "AGPL-3.0-or-later" }
"""


def get_dual_license_rider() -> str:
    """Return canonical dual-licensing rider for LICENSE files."""
    return STANDARD_DUAL_LICENSE_RIDER.strip() + "\n"


def get_commercial_md() -> str:
    """Return standard COMMERCIAL.md content."""
    return STANDARD_COMMERCIAL_MD.strip() + "\n"


def get_pyproject_snippet() -> str:
    """Return pyproject.toml licensing snippet."""
    return PYPROJECT_SNIPPET.strip() + "\n"
