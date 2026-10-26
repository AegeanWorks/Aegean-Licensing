# AegeanWorks Asset Separation & Licensing Policy

**Version 1.1 — October 2026**
**Contact**: `aegean-licensing@proton.me`

This policy governs the categorization, licensing and commercial use of materials hosted within
AegeanWorks repositories, separating software code from creative, scientific and domain assets.

---

### 1. Scope & Categorization

Files across AegeanWorks repositories fall into these categories:

| Category | Typical File Types | Default public license | Commercial track |
|---|---|---|---|
| **Software source code** | `.py`, `.c`, `.rs`, `.js`, `.ts`, `.html`, build scripts | The project's LICENSE: AL-1.1 (software), AGL-1.1 (games) or ASL-1.1 (research) | ACL-1.0 + certificate |
| **Documentation & guides** | `README.md`, `docs/`, inline docstrings | The project's LICENSE | ACL-1.0 + certificate |
| **Game assets** | 3D models, textures, animation, audio, music, voice, fonts, level data | AGL-1.1 only when listed in the project's asset manifest; otherwise proprietary | ACL-1.0 + dedicated asset grant |
| **Research data & weights** | datasets, annotations, notebooks, model weights | ASL-1.1 only when listed as Project Data and owned by the project; otherwise proprietary or its own license | ACL-1.0 + dedicated data/weights grant |
| **Trademarks & branding** | logos, badges, project names, wordmarks | All rights reserved | Written consent only |

### 2. Category Details

#### 2.1 Software Source Code
Program code, tests, algorithms and scripts are licensed under the project's LICENSE. A software
project uses **AL-1.1** (free private personal use; commercial use needs ACL-1.0); a game uses
**AGL-1.1** (personal play, streaming, modding and the DRM-free covenant); a research project uses
**ASL-1.1** (non-commercial research, publication and non-commercial ML training). Versions
released under GNU AGPL-3.0 before a project moved to an Aegean license keep that license.

#### 2.2 Documentation & Specifications
Documentation, explanations, diagrams and tutorials are Covered Material under the project's
LICENSE. Documentation already released under CC BY 4.0 keeps that license for those versions.
Creative Commons licenses are not used for AegeanWorks software because they do not address source
distribution or patents.

#### 2.3 Game Assets
Art, models, animation, audio, music, voice, fonts, level data and narrative in a game repository
are **not** licensed by AGL-1.1 unless the `LICENSE` names them or the project's asset manifest
lists them. An asset manifest is a file the README names, normally `ASSETS.md`, with one row per
asset set and its license. Unlisted assets remain proprietary: they may be used only as part of
playing the Covered Game, and may not be extracted, redistributed or included in a mod without a
grant (see `commercial/GAME-ASSET-ADDENDUM-DRAFT.md`); ACL-1.0 covers code and
logic only.

#### 2.4 Research Data and Model Weights
Datasets, annotations and model weights in a research repository are **Project Data** only when
the project owns them or may sublicense them and lists them in its LICENSE or asset manifest.
Third-party datasets keep their own licenses. ASL-1.1 permits non-commercial research use of
Project Data; commercial use, redistribution as a standalone dataset, and commercial model
training need a dedicated data/weights grant (see `commercial/DATA-WEIGHTS-ADDENDUM-DRAFT.md`).
Personal data must have a lawful basis and a dataset-specific notice; ASL-1.1 does not grant one.

#### 2.5 Asset Manifests
A project that licenses assets or data should include an asset manifest named in its README. Each
entry states the path or pattern, the rights holder, the license and any restrictions. Assets not
listed are not licensed under the project's public license. An empty or missing manifest means the
project licenses code only.

#### 2.6 Trademarks and Project Identity
The names "AegeanWorks", "AIKit", "Aegean-E" and associated logos, badges and wordmarks are
proprietary. No Aegean license grants trademark rights. Nominative references that accurately
identify the material are allowed; endorsement or origin claims need written authorization.
