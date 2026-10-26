# Aegean Commercial Licensing FAQ

Frequently asked questions about the Aegean License 1.1 (AL-1.1), the Aegean Commercial License
1.0 (ACL-1.0), and commercial orders.

---

### Q1: Can I use AegeanWorks software commercially for free?
**No.** The Aegean License 1.1 is free only for an individual's own private, non-commercial use.
Any use by or for a company or other organization, in paid or client work, or in a product or
hosted service offered to others needs ACL-1.0 before the use begins. The one exception: each
company may evaluate the software for 28 days, once per company group, non-production only
(AL-1.1 Section 4.3). Versions AegeanWorks
released under GNU AGPL-3.0 before a project moved to AL-1.1 stay under AGPL-3.0 for those
versions only.

### Q2: Why buy ACL-1.0?
It is the only license that permits commercial or organizational use: internal business use,
closed-source products and SaaS, client deliverables, embedded redistribution, or OEM rights. It
is a pure copyright and patent grant, not a support contract.

### Q3: What does a certificate include?
A JSON and Markdown License Grant Certificate with the licensee identity, tier, projects, scope,
any allowances (`ai-training`, `hosted-service`), term, issue date, a SHA-256 integrity digest,
the digest of the cited agreement text, and an issuer signature the licensor can check.

### Q3b: What personal data does the licensor keep?
The certificate holds the licensee's name, contact email and, when given, address, registration
number and country. The licensor keeps it to issue, verify and enforce the license, and does not
publish it: the public register lists only certificate ids, digests, dates and status. The full
KVKK information notice, including legal bases, transfers abroad, retention and your rights, is
`licenses/PRIVACY.md`. Ask `aegean-licensing@proton.me` to see or correct your data.

### Q4: How is a certificate verified?
```bash
python -m aegean_licensing verify license_certificate_<id>.json --register licenses/issued.json
```
**The digest is not a signature.** Anyone can recompute a SHA-256 digest. The certificate is
authentic only when the licensor's public register (`licenses/issued.json`) lists its id and
digest as valid, or when the licensor confirms it in writing. Without `--register`, the tool
reports the record as internally consistent (`VALID_UNVERIFIED`) but not authentic. A revoked
certificate reports `REVOKED`.

### Q5: What tiers exist? What do they cost?
Tier1 (indie), Tier2 (business), and Tier3 (OEM). The tier changes price and commercial scope,
not the legal text. Fees are quoted privately; nothing in this repository is an offer.

### Q6: How do I obtain a license?
Email **`aegean-licensing@proton.me`** with the legal licensee name, registration or tax id,
address, country, project(s), tier, intended scope, and desired term. The licensor replies with
the applicable terms, fees, and payment method, and the parties record them in an Order Form.
Purchases are not made through GitHub or this repository.

### Q7: Are prices published?
No. Fees depend on tier, scope, and term, and are quoted privately. Nothing in this repository
is an offer.

### Q8: Can I get a refund?
Fees are non-refundable after the certificate is issued. If the licensor cannot issue a valid
certificate for a settled order, it will issue the certificate or refund the amount received by
the method agreed in the Order Form. Taxes are handled under ACL-1.0 Section 4.

### Q9: Are assets included?
No. Art, audio, textures, datasets, clinical templates, and model weights are proprietary,
evaluation-only assets under `licenses/ASSET_POLICY.md`. Commercial use needs a separate written
asset grant. ACL-1.0 covers code and logic.

### Q10: Do I get support updates?
No support, SLA, maintenance, indemnification, or warranty is included unless a separate written
agreement says so. The software is licensed AS-IS.

### Q11: Who is the licensor?
AegeanWorks (`aegean-licensing@proton.me`), Türkiye. “Aegean-E” is a legacy brand alias for the
same licensor.

### Q12: How do I request a quote or a custom order?
Email **`aegean-licensing@proton.me`** with:
1. legal licensee name, registration/tax id, address, and country;
2. project(s) to license (or the full portfolio);
3. tier, intended use (closed SaaS, embedded, OEM, client deliverables), and desired term;
4. any procurement or security requirements you need the licensor to consider.
