# Aegean Commercial License Order Form (ACL-1.0)

**Template version:** 0.6
**Template date:** 25 October 2026
**Status:** template — complete and execute for each commercial order

This Order Form supplements the **Aegean Commercial License 1.0 (ACL-1.0)** and
incorporates it by reference. Commercial terms are agreed privately by email; nothing is sold
or paid for through GitHub or this repository. If this form and ACL-1.0 conflict, ACL-1.0
Section 10 controls.

---

## 1. Parties

- **Licensor:** AegeanWorks (`aegean-licensing@proton.me`), Türkiye
- **Licensee legal name:** ____________________________________
- **Registration / tax id:** ________________________________
- **Registered address:** ____________________________________
- **Country:** ______________________________________________
- **Licensee contact and notice email:** _____________________

## 2. Order Details

| Field | Value |
|---|---|
| Tier | Tier1 / Tier2 / Tier3 |
| Projects covered | ____________________________ (or `*` for the portfolio) |
| Scope | `internal-use`, `proprietary-saas-and-redistribution`, `client-deliverables`, `oem-embedded`, or `enterprise-unrestricted` |
| Allowances | none / `ai-training` / `hosted-service` (ACL-1.0 Sections 3.9 and 3.10) |
| Affiliates covered | none / ____________________________ (ACL-1.0 Section 3.12) |
| Term | 12 months / perpetual |
| Effective date | ____________________________ |
| Expiration date | ____________________________ (blank if perpetual) |
| Certificate id | assigned by the licensor on issuance |

## 3. Fees and Payment

- **Fees:** ________________________________________________
- **Currency and payment method:** agreed privately by email and recorded here: ____________
- **Payment schedule:** ____________________________________
- **Taxes:** fees exclude taxes; the licensee bears applicable taxes and withholdings.

Payment is complete only when the licensor confirms receipt in writing. The certificate is
issued after that confirmation. Fees are non-refundable after issuance. If the licensor cannot
issue a valid certificate for a settled order, it will refund the amount received by the agreed
method. No payment details are published in the repository. See ACL-1.0 Section 4.

## 4. Acceptance

By signing or accepting this Order Form in writing, the licensee accepts ACL-1.0 and this form,
and declares that it meets the eligibility of the Tier above. It will tell the licensor within 30
days if it stops meeting it (ACL-1.0 Section 3.14). The licensee confirms it has received the
KVKK privacy notice (`licenses/PRIVACY.md`); this is an acknowledgment, not a consent.
The licensor issues the certificate after confirming the agreed payment.

- **Licensee signature / acceptance:** ______________________________
- **Name and title:** ______________________________________________
- **Date:** ________________________________________________________
- **Licensor acceptance:** AegeanWorks, represented by its authorised operator, upon issuance.

## 5. Verification

Verify the issued certificate against the licensor's public register:

```bash
python -m aegean_licensing verify license_certificate_<id>.json --register licenses/issued.json
```

The SHA-256 digest proves internal consistency only. The certificate is authentic only when the
public register (`licenses/issued.json` in the aegean-licensing repository) lists it as valid, or
the licensor confirms it in writing. The licensor never publishes its signing key.

**Contact:** `aegean-licensing@proton.me`
