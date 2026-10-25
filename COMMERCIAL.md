# Aegean Commercial Licensing & Licensing Tiers

> **Licensing model.** AegeanWorks software is free for personal use under the **Aegean License
> 1.0 (AL-1.0)**. Every commercial or organizational use needs the paid **Aegean Commercial
> License 1.0 (ACL-1.0)**. A project may later move to the **Restricted** tier and stop being
> distributed. “Aegean-E” is a legacy brand alias for the same licensor.

---

## 1. The Three Tiers

### Personal — AL-1.0, free (default)
- **License:** [Aegean License 1.0](LICENSE), also in `licenses/AL-1.0.md`.
- **You may** download, run, study, and modify the software for your own private,
  non-commercial use as an individual: learning, coursework, hobby projects, personal research.
- **You may not** use it for or on behalf of any company or organization, in paid or client
  work, in a hosted service, or in anything offered to others; redistribute it; train AI
  models on it; or bypass its license checks. The binding definitions are in AL-1.0 Sections
  4 and 5.

### Commercial — ACL-1.0, paid
- **License:** ACL-1.0, in `licenses/ACL-1.0.md`, evidenced by a License Grant Certificate.
- **For** organizations, freelancers, and anyone whose use is commercial: internal business
  use, closed-source products and SaaS, client deliverables, embedded redistribution, OEM.
- **Required before** the commercial use begins.
- **Try first:** each company may evaluate the software free for **28 days**, once per company
  group, non-production only (AL-1.0 Section 4.3). After that it needs ACL-1.0 or must stop.

### Restricted — All Rights Reserved
- **For** projects too valuable to distribute. Versions after the project's cutoff commit carry
  `licenses/RESTRICTED-NOTICE.md`, grant no license, and are not published.
- **Earlier releases are not revoked.** Every version released before the cutoff stays under
  the license it was released with, including GNU AGPL-3.0 for the versions AegeanWorks once
  released under it. AegeanWorks no longer makes new releases under AGPL-3.0.

---

## 2. Scope: Code and Assets

- **Code** is AL-1.0 by default; ACL-1.0 is the commercial license.
- **Creative and domain assets** (3D models, textures, audio, clinical templates, datasets,
  model weights) are not licensed by ACL-1.0. They are proprietary, evaluation-only material
  under `licenses/ASSET_POLICY.md`, and require a separate written asset grant for any
  commercial use.
- **Trademarks** are not licensed. “AegeanWorks”, “Aegean-E”, “AIKit”, and project logos remain
  the exclusive property of the licensor.

---

## 3. Commercial Tiers

The certificate names one tier. Eligibility is declared honestly by the licensee; the licensor
may require evidence for a tier claim.

| Tier | Intended for | Typical scope | Term options |
|---|---|---|---|
| **Tier1 — Indie** | Individuals and small teams, annual revenue under USD 250,000 | Internal use, closed-source SaaS, client deliverables | 12 months or perpetual |
| **Tier2 — Business** | Growing companies and SaaS operators, revenue at or above USD 250,000 | Closed-source SaaS, cloud APIs, confidential client deliverables, redistribution inside a product | 12 months or perpetual |
| **Tier3 — OEM** | Devices, engines, retail bundles, high-volume redistribution | Embedded or bundled redistribution; separate volume terms | 12 months or perpetual |

All tiers share the same legal text (ACL-1.0). A tier changes price and commercial scope, not
the license terms. Invoices, volume commitments, and OEM royalties, if any, are stated in the
order form.

---

## 4. What Is and Is Not Included

Included: the copyright and patent permissions described in ACL-1.0, for the projects,
tier, scope, and term on the certificate.

Not included: technical support, SLAs, maintenance, custom development, indemnification,
training, warranty, or trademark rights. The software is licensed **AS-IS**.

---

## 5. How to Obtain a License

Commercial licensing is handled privately. Nothing is sold or paid for through GitHub, this
repository, or any public page.

1. **Contact by email:** write to `aegean-licensing@proton.me` with the legal licensee name,
   registered address, registration or tax id (if any), country, project(s), tier, intended
   scope, and desired term.
2. **Agree the terms:** the licensor replies with the applicable tier, fees, payment method,
   payment schedule, and any verification requirements. The parties record those terms in the
   Order Form.
3. **Confirm:** once the agreed payment is confirmed in writing, the licensor issues a signed
   License Grant Certificate (JSON and Markdown) that identifies the licensee, tier, projects,
   scope, term, and the digest of the incorporated agreement.
4. **Verify:** anyone can check the certificate against the licensor's public register:
   `python -m aegean_licensing verify <certificate.json> --register licenses/issued.json`.
   The register lists no personal data. Without it the tool can only confirm that the record is
   internally consistent, not that the licensor issued it or that it was not revoked.

### Commercial terms

- Fees, currency, payment method, and schedule are agreed in the Order Form. No payment details
  are published in this repository.
- Payment is complete only when the licensor confirms receipt in writing; the certificate is
  issued after that confirmation.
- Fees exclude applicable taxes, which the licensee bears.
- Fees are non-refundable after the certificate is issued. If the licensor cannot issue a valid
  certificate for a settled order, it will issue the certificate or refund the amount received
  by the agreed method.
- An inquiry, quote, or unpaid Order Form creates no license.
- Disputes are handled under ACL-1.0 Section 10.

---

## 6. Certificate and Agreement

The certificate identifies the licensee, tier, projects, scope, term, digest, and signature.
It incorporates `licenses/ACL-1.0.md` by reference. The order form (if any) controls fees and
payment. If documents conflict, the order of precedence in ACL-1.0 Section 10 applies.

Earlier drafts used an “Exhibit A” summary of commercial terms. That summary is replaced by
ACL-1.0; a certificate issued under this version cites ACL-1.0 and the digest of its text.

---

## 7. Contact

**AegeanWorks Licensing** — `aegean-licensing@proton.me`
Repository: <https://github.com/AegeanWorks>
