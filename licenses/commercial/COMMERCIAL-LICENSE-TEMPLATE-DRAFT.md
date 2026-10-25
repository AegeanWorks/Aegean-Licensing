# Aegean Commercial License Agreement (ACLA-1.0-DRAFT)

**Draft version:** 0.3  
**Draft date:** 25 October 2026  
**Status:** DRAFT FOR REVIEW — Operative upon formal release and execution of a License Grant Certificate

---

## 1. Parties & Commercial Purpose

This Commercial License Agreement (the **"Agreement"**) is entered into by and between:
- **Licensor**: AegeanWorks (`aegean-licensing@proton.me`), and
- **Licensee**: The entity or individual designated on an authentic AegeanWorks License Grant Certificate.

This Agreement provides commercial organizations, startups, and developers with binding, proprietary rights to integrate, deploy, host, and redistribute AegeanWorks software without being subject to the source disclosure conditions of the GNU AGPL-3.0 or the non-commercial restrictions of the Aegean Licensing Personal Use License (AL-PU 1.0).

---

## 2. Commercial Licensing Tiers

Licensee may obtain commercial permissions under one of three tiers as specified in their License Grant Certificate:

| Tier | Eligibility & Scope | Key Rights |
|---|---|---|
| **Tier 1: Indie & Startup** | Revenue < \$250,000/yr OR team size $\le$ 5 | Full commercial deployment, internal automation, closed SaaS |
| **Tier 2: Enterprise & SaaS** | Revenue $\ge$ \$250,000/yr OR cloud platforms | Unlimited seats, closed SaaS cloud APIs, confidential client deliverables |
| **Tier 3: OEM & Embedded** | Hardware devices, game engines, retail bundles | Royalty or volume redistribution of embedded binaries |

---

## 3. Grant of Commercial Rights

Subject to the terms herein and possession of a valid License Grant Certificate, Licensor grants Licensee a worldwide, non-exclusive, non-transferable (except to a corporate successor or affiliate) right to:

1. **Closed-Source SaaS & Cloud APIs**: Deploy the Licensed Software on cloud servers, private networks, or multi-tenant architectures without disclosing, publishing, or offering backend modifications or source code to network users.
2. **Proprietary Integration**: Embed, link, and compile the Licensed Software into proprietary, closed-source commercial applications, workflows, or client deliverables.
3. **Redistribution**: Distribute compiled binaries or bundled packages as part of Licensee's commercial products, keeping proprietary adaptations and modifications confidential.
4. **Perpetual Production Rights**: All versions released by Licensor during the active term of the License Grant Certificate may be deployed in production by Licensee perpetually.

---

## 4. Boundaries & Pure License Model

1. **Pure IP Permissions**: This Agreement is strictly a legal grant of intellectual property permissions and copyleft waiver.
2. **No Technical Support or SLAs**: Software is provided as self-service tooling. Licensor undertakes no obligation to provide maintenance, bug-fixing, consulting, custom development, or Service Level Agreements (SLAs).
3. **No Resale as Standalone Code**: Licensee may not resell or broker the unmodified standalone source code in direct competition with Licensor's commercial licensing operations.
4. **AS-IS Disclaimer**: THE SOFTWARE IS LICENSED AS-IS WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
5. **Limitation of Liability**: IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY CONSEQUENTIAL, INDIRECT, INCIDENTAL, OR PUNITIVE DAMAGES ARISING FROM THE USE OF THE SOFTWARE.

---

## 5. Digital Verification & Certificate Issuance

Commercial permissions under this Agreement become effective immediately upon the issuance of an authentic **AegeanWorks License Grant Certificate** containing a unique Certificate ID, licensee details, and a SHA-256 cryptographic integrity digest.

Authenticity can be verified at any time using the local verification tooling:
```bash
aegean-license verify license_certificate_<id>.json
```

For custom quotes, multi-project bundles, or enterprise procurement:  
**Contact:** `aegean-licensing@proton.me`
