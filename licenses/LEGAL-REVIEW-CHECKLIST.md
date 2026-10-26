# Legal Review Checklist (Draft)

This checklist is the hand-off to qualified counsel. It is not legal advice and does not make a
license operative. A license version is release-ready only when counsel has signed off on the
items that apply to it.

## Family and precedence

- [ ] AL-1.1, AGL-1.1, ASL-1.1 and ACL-1.0 are internally consistent; a conflict rule is stated.
- [ ] AGL-1.1 and ASL-1.1 correctly identify their AL-1.1 base and the sections they override.
- [ ] The 1.0 texts are archived, still identifiable, and not mistaken for a current grant.
- [ ] Each release names its governing version, and a later version cannot revoke an earlier grant.

## Grant, scope and definitions

- [ ] "Covered Material", "Commercial or Organizational Use", "Non-Commercial", "You", "Company"
      and "Version" are defined without circularity.
- [ ] The personal grants match the product story: AL software, AGL games, ASL research.
- [ ] Redistribution, hosting, client work, OEM and evaluation are each addressed.
- [ ] The copyright license, patent grant and patent-defense termination are enforceable and
      consistent with each other.

## Game terms (AGL-1.1)

- [ ] The DRM-free covenant is a condition, not an unenforceable aspiration.
- [ ] "No mandatory client/account/activation" does not conflict with a storefront's own terms.
- [ ] Streaming/recording, mods, private servers and asset manifests are clear.
- [ ] Anti-cheat and consumer-rights carve-outs are balanced and lawful.
- [ ] Platform, console and third-party SDK terms are not overridden by accident.

## Science terms (ASL-1.1)

- [ ] Non-commercial research, teaching, publication, reproducibility and text/data mining are
      permitted without accidentally granting commercial rights.
- [ ] Non-commercial ML training and model-output ownership are clear.
- [ ] Project Data, third-party data, personal data (KVKK/GDPR) and clinical use are addressed.
- [ ] Research ethics, integrity, export control and prohibited-use language are adequate.
- [ ] Commercial data/model-weights grants are separate from ACL-1.0 code rights.

## Commercial terms (ACL-1.0)

- [ ] Scope, tiers, allowances, term, evaluation, fees, taxes, audit and verification are clear.
- [ ] Liability, indemnity, warranty, termination, cure and survival match the Order Form.
- [ ] Assets, datasets and model weights are excluded from the code grant and covered separately.
- [ ] Certificate/register wording does not overstate what the digest or signature proves.

## Assets, data and contributions

- [ ] `ASSET_POLICY.md` matches the license family and the asset-manifest convention.
- [ ] Third-party assets, fonts, audio, datasets and model weights are identified with their own
      terms and provenance.
- [ ] The CLA grants enough rights to relicense contributions and includes a patent grant.
- [ ] Moral rights, attribution and notice-retention rules are workable in Türkiye and abroad.

## Consumer, privacy and trade

- [ ] Mandatory consumer rights, refunds and conformity claims are not limited.
- [ ] The KVKK/GDPR notice covers controller, purposes, transfers, retention and Article 11 rights.
- [ ] Trademark, publicity, endorsement and project-name use are covered by a separate policy.
- [ ] Export-control, sanctions, anti-corruption and accessibility obligations are considered.

## Operability

- [ ] A court can identify the licensor, the version, the grant and the remedy.
- [ ] The cure period, termination triggers and reinstatement are clear.
- [ ] The license is compatible with the distribution channels actually used.
- [ ] The team has a support, security-disclosure and incident-response policy to point to.
- [ ] Counsel has recorded the approved version and date in the ADR register.
