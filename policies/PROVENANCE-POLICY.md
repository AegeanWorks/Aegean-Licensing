# Asset and Data Provenance Policy

**Version 1.0 — October 2026**
**Contact**: `aegean-licensing@proton.me`

A license can grant only what the licensor owns or may sublicense. This policy makes the evidence
for that ownership reviewable before a project is published or commercialized.

## 1. Manifest

A project that ships non-code assets or data should include an asset manifest named in its README,
normally `ASSETS.md` or `DATA.md`. Each entry states:

- path or pattern;
- rights holder;
- license or written permission;
- source URL or supplier;
- date obtained;
- whether personal data is present and the lawful basis; and
- restrictions (territory, term, field of use, attribution).

Assets and data not listed are not licensed under the project's public license.

## 2. Third-party material

1. Keep the original license text and receipt or grant letter with the project records.
2. Do not assume that a free download is free to relicense.
3. Fonts, audio, models, datasets and SDKs need their own terms; a code license does not cover them.
4. A dataset with personal data needs a lawful basis, a purpose limitation, a retention period and,
   where required, a data-processing agreement.
5. A model weight file needs its training-data provenance and the terms that attach to it.

## 3. Contributions

A contributor of an asset or dataset must confirm that they own it or have permission to license
it, and must grant the project the rights the CLA describes. A contribution that cannot be traced
is not merged.

## 4. AI-generated material

AI-generated art, audio, text or code must be reviewed for third-party rights, platform terms and
provenance. Record the tool and the date. Do not present generated material as human-authored when
the law or a platform requires disclosure.

## 5. Review before release

Before a public or commercial release:

- [ ] every manifest entry has a rights holder and a license;
- [ ] third-party notices are included;
- [ ] personal data has a lawful basis and a notice;
- [ ] model weights have a training-data provenance note;
- [ ] the commercial grant covers the assets and data, not only the code.

A failed check blocks the release until the gap is closed or the asset is removed.
