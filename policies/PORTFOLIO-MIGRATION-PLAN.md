# AegeanWorks Portfolio Licensing Migration Plan

**Status:** Roadmap — each project migrates at its milestone; not operative for a project until
that project's release is tagged under AL-1.0
**Version:** 1.2 — October 2026
**Governing Policy:** [BACKWARD-COMPATIBILITY-DRAFT.md](BACKWARD-COMPATIBILITY-DRAFT.md)

> AegeanWorks makes no new release under AGPL-3.0. The licenses are `licenses/AL-1.0.md`
> (personal use) and `licenses/ACL-1.0.md` (commercial); legal review is recommended before
> either is relied on in a dispute. A project keeps its AGPL-3.0 baseline only until its
> migration milestone, and every version already released under AGPL-3.0 stays AGPL-3.0.

---

## 1. Executive Summary

This document establishes the official project-by-project roadmap for transitioning AegeanWorks repositories from the initial baseline (**GNU AGPL-3.0 + ACL-1.0 Dual Licensing**) to the finalized custom source-available model (**Aegean License 1.0 AL-1.0 + Aegean Commercial License Agreement ACL-1.0**).

In strict adherence to the [Backward Compatibility Policy](BACKWARD-COMPATIBILITY-DRAFT.md):
- **No Retroactive Revocation**: Every release, commit, or package historically distributed under AGPL-3.0 remains irrevocably available under AGPL-3.0 to all recipients.
- **Forward Version Gating**: All new releases published past a project's designated migration milestone adopt AL-1.0 (free for personal and individual student use) and ACL-1.0 (paid commercial tiers).

---

## 2. Portfolio Categorization & Migration Matrix

AegeanWorks projects are grouped into four operational tiers with customized migration milestones:

| Category | Representative Projects | Current Baseline | Migration Milestone | Forward Model |
|---|---|---|---|---|
| **AI & Neural Engines** | `N1-Engine`, `NeuralBeat`, `NeuroOptic`, `neurocore` | AGPL-3.0 + ACL | Next tagged release | **AL-1.0 + ACL-1.0** (High Commercial Value) |
| **CLI & Applications** | `chronos`, `cyberpulse`, `lattice` | AGPL-3.0 + ACL | v2.0.0 (or v0.2.0) | **AL-1.0 + ACL-1.0** |
| **Games & Media** | `voidfarer`, `aldervale`, `crypt-crawler` | AGPL-3.0 + ACL | Alpha / Next Release | **Code: AL-1.0; Media: ASSET_POLICY.md** |
| **Domain Assets** | `NeurologyClinicTemplates-TR` | Proprietary Domain | Immediate | **ASSET_POLICY.md (Proprietary Clinic License)** |
| **Developer Infrastructure**| `portable_agent_kit` (AIKit), `aegean-licensing` | AGPL-3.0 + ACL | Next release (October 2026) | **AL-1.0 + ACL-1.0** |

A project whose value outgrows free distribution may later move from AL-1.0 to the **Restricted
tier**: later versions carry `licenses/RESTRICTED-NOTICE.md` (All Rights Reserved) from a
recorded cutoff commit and are not published, while every earlier version keeps its license.
AIKit performs the switch with `python aikit.py license <name> --restrict`.

---

## 3. The 6-Step Pre-Migration Release Checklist

Before any repository migrates its active license from AGPL-3.0 to AL-1.0, the release maintainer must execute the following protocol:

### Step 0: Legal Review and Rights-Holder Approval
- Obtain written legal review of the final AL-1.0 text and the ACL-1.0 commercial agreement.
- Record the approval and its effective date in `.aikit/decisions.md` before changing any `LICENSE` file.
- Confirm the rights holder for the specific repository; a portfolio-wide plan does not grant that authority by itself.

### Step 1: Contributor IP & Inbound Rights Review
- Confirm that 100% of the repository's copyrightable source code is owned by AegeanWorks, or that all external pull requests have an executed [Contributor License Agreement (CLA)](../licenses/CONTRIBUTING_CLA.md).
- Third-party open-source dependencies (e.g. PyPI packages) must be documented in `pyproject.toml` with their respective permissive licenses.

### Step 2: Final AGPL-3.0 Legacy Milestone Tag
- Create a permanent, immutable Git tag marking the final AGPL-3.0 release:
  ```bash
  git tag -a v1.0.0-agpl -m "Final legacy release under GNU AGPL-3.0"
  git push origin v1.0.0-agpl
  ```
- This guarantees full transparency and provides community users with permanent access to the last copyleft version.

### Step 3: License & Commercial File Swap
- Replace root `LICENSE` with the approved text, copied from `licenses/AL-1.0.md` once that draft is finalized. Rename the approved file to `licenses/AL-1.0.md` in this repository at the same time.
- Replace `COMMERCIAL.md` with the approved ACL-1.0 terms, promoted from `licenses/commercial/COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md`, listing the tiers and stating that fees and payment are arranged privately by email.
- Ensure `licenses/ASSET_POLICY.md` and `policies/BACKWARD-COMPATIBILITY-DRAFT.md` are committed.

### Step 4: Metadata and Package Specification Update
- Update `pyproject.toml` (or the package configuration). Under PEP 639 the license is a string expression:
  ```toml
  [project]
  license = "LicenseRef-AL-1.0"
  license-files = ["LICENSE"]
  ```
  For tooling that still needs the deprecated table form, use
  `license = { text = "Aegean License 1.0 (AL-1.0) / Commercial (ACL-1.0)" }`
  and record why in the release notes.

### Step 5: Release Notes & Changelog Disclosure
- Add an explicit announcement in `CHANGELOG.md` and GitHub Release notes:
  > *"Notice: Beginning with release v2.0.0, this software is published under the Aegean License 1.0 (AL-1.0) for free personal, academic, and non-commercial use, and the Aegean Commercial License Agreement (ACL-1.0) for commercial deployments. Releases up to v1.0.0-agpl remain governed by GNU AGPL-3.0."*
  Substitute this project's actual release number; tag names differ per repository.

### Step 6: Post-Migration Verification
- Have AegeanWorks run its private licensing audit (`aegean-ops audit . --strict --check-policies`) and confirm the new `LICENSE` is recognized.
- Confirm the `vX.Y.Z-agpl` tag is pushed and immutable before the first AL-1.0 release.

---

## 4. Resolving External Inquiries (FAQ for Users)

- **Q: Can I continue using older versions under AGPL-3.0?**  
  **Yes.** AegeanWorks respects all prior grants. You may run, modify, and distribute versions tagged prior to the migration milestone under AGPL-3.0.
- **Q: Why was the license updated for new versions?**  
  To protect ongoing commercial investment, support full-time R&D on neural engines and tools, and prevent proprietary cloud operators from hosting AegeanWorks software without source disclosure or compensation.
- **Q: How do commercial organizations transition?**  
  Organizations can instantly obtain a digital commercial license certificate by contacting `aegean-licensing@proton.me` or using our automated licensing tooling.

