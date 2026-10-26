# SPDX and REUSE Policy

**Version 1.0 — October 2026**
**Contact**: `aegean-licensing@proton.me`

A custom license is only machine-readable when the repository states its license expression and
provides the license text in the form a scanner expects. This policy is the baseline for that
metadata; `reuse lint` and SPDX tools remain the external verifier.

## 1. License expressions

| Project tier | SPDX expression |
|---|---|
| Software (AL-1.1) | `LicenseRef-AL-1.1` |
| Game (AGL-1.1) | `LicenseRef-AGL-1.1` |
| Science (ASL-1.1) | `LicenseRef-ASL-1.1` |
| Commercial (ACL-1.0) | A certificate reference, not a public license expression |
| Restricted | `LicenseRef-Aegean-Restricted` |

The `LicenseRef-` prefix is deliberate: these are not OSI identifiers. An SPDX tool must find the
text in `LICENSES/<identifier>.txt`.

## 2. Generated files

`aikit.py` writes, for a personal-tier project:

- `LICENSES/LicenseRef-AL-1.1.txt` (or AGL/ASL), a copy of `LICENSE`; and
- `REUSE.toml` with `SPDX-FileCopyrightText = "2026 AegeanWorks"` and
  `SPDX-License-Identifier = "LicenseRef-AL-1.1"` (or the current tier).

`aikit license <project> --set ...` replaces both when the tier changes; `aikit fix` refreshes them.
`aikit license <project> --restrict` replaces the identifier with `LicenseRef-Aegean-Restricted` and
removes the old personal copy.

## 3. Per-file headers

A project may add a header to each source file:

```text
# SPDX-FileCopyrightText: 2026 AegeanWorks
# SPDX-License-Identifier: LicenseRef-AL-1.1
```

Use the comment syntax of the language. A file copied from a third party keeps its own identifier,
copyright and source URL; the `REUSE.toml` annotation must not claim it.

## 4. Third-party and generated material

1. Third-party code, assets, data and model weights keep their own SPDX identifiers.
2. Generated files should be excluded from REUSE or marked with their source.
3. A file with no header inherits the `REUSE.toml` annotation; a specific file header overrides it.
4. The `LICENSES/` folder contains only license texts, not source code.

## 5. Verification

Run `reuse lint` in the project root after a license change. It checks that every file has an
identifier and that every referenced license text exists. AIKit does not bundle the `reuse` tool;
the generated manifest is the baseline, and CI may install `reuse` to enforce it.

## 6. Limits

- A custom `LicenseRef` will not be recognised by a tool that only knows the SPDX License List.
- The manifest does not replace the full license text; keep `LICENSE` and `COMMERCIAL.md`.
- A project with files under several licenses needs a per-file header or a per-path annotation.
- This policy is not legal advice; the license text controls.

## 7. Adoption

New projects get the manifest automatically. An existing project runs `python aikit.py fix <name>`
to add it, reviews the new `REUSE.toml` and `LICENSES/` files, and commits them. A project that
prefers a single `REUSE.toml` annotation for the whole tree may keep the generated form.
