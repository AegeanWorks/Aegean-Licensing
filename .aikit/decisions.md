# Decisions

Why this project is built the way it is, oldest first. One entry per decision that changes a
contract, a dependency, a data format or the architecture; IDs are consecutive and never reused.

<!-- Entry format:
### ADR-NNN: <decision in one line>
- **Date**: YYYY-MM-DD
- **Status**: Accepted
- **Context**: <what forced the decision>
- **Decision**: <what was decided>
- **Consequences**: <what follows, including what it costs>
-->


### ADR-001: Pure Standard Library Dual-Licensing Framework & Cryptographic Tooling
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: AegeanWorks software is published under GNU AGPL-3.0 for open collaboration, but commercial entities require closed-source operations and copyleft waivers without enterprise bureaucracy (MSAs, SLAs, W-9s). Additionally, repository audits across the portfolio require clear delineation between code and domain assets, inbound contributor rights, and automated verification.
- **Decision**: Establish the Aegean-E Commercial License (AECL-1.0) with binding standard terms (Exhibit A) and pure standard-library tooling (`aegean_licensing`) providing: (1) canonical SHA-256 certificate hashing and optional HMAC-SHA256 signatures, (2) tamper detection and expiration/scope verification, (3) repository compliance auditing, and (4) standard licensing templates.
- **Consequences**: Zero external dependencies required. Certificates are portable, tamper-evident, and auditable in ~2ms. License grants are strictly AS-IS pure copyright waivers without technical support obligations.


### ADR-002: Draft Personal Use License (AL-PU 1.0) and Backward Compatibility Policy
- **Date**: 2026-10-25
- **Status**: Proposed
- **Context**: AegeanWorks is evaluating a transition toward a custom source-available model where personal non-commercial use is free under the Aegean Licensing Personal Use License (AL-PU 1.0), while commercial and organizational use requires prior written authorization. Crucially, earlier releases (e.g., under AGPL-3.0) and third-party contributions cannot be retroactively modified without legal authority.
- **Decision**: Draft `AL-PU-1.0-DRAFT.md`, `COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md`, and establish `BACKWARD-COMPATIBILITY-DRAFT.md` affirming that: (1) existing AGPL-3.0 grants are preserved and cannot be retroactively revoked, (2) older versions reissued by AegeanWorks adopt new terms only when authorized, and (3) a clear migration and legal checklist precedes any operative transition.
- **Consequences**: Provides transparency for future licensing evolution while legally protecting existing community users and open source integrity.


### ADR-003: Optimization of AL-PU 1.0 Draft for Maximum Commercial Conversion & Personal Protection
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The initial AL-PU v0.2 draft had commercial leakage points (unclear startup transitions, freelancer ambiguity, and contributor IP bottlenecks) while risking chilling individual students. Additionally, it lacked a structured commercial agreement draft and a non-litigious conversion ramp for unauthorized commercial users.
- **Decision**: Update `AL-PU-1.0-DRAFT.md` (to v0.3) and `COMMERCIAL-LICENSE-TEMPLATE-DRAFT.md` to: (1) carve out free self-study for enrolled students, (2) define explicit commercialization triggers (first revenue, third-party deployment, client delivery), (3) mandate commercial licensing for billable freelance/consulting work, (4) bind public PRs to the inbound CLA, (5) introduce a Commercial Cure Ramp in Section 9.1 to monetize infringers directly, and (6) establish a 3-tier commercial framework backed by cryptographic License Grant Certificates.
- **Consequences**: Protects grassroots student and developer adoption while maximizing commercial conversion and revenue capture from startups, consulting firms, and enterprise cloud operators.


### ADR-004: Configurable License Types, Multi-Model Auditor and Expanded Template Suite
- **Date**: 2026-10-25
- **Status**: Accepted
- **Context**: The `aegean-license` CLI was hardcoded to `AECL-1.0` and its template generator only produced basic AGPL boilerplate. Furthermore, the repository auditor rejected any repository not starting with AGPL-3.0, preventing future verification of projects adopting AL-PU 1.0 or checking for required policies.
- **Decision**: (1) Add `--type` argument to `issue` enabling tiered certificates (e.g. `ACLA-1.0-Tier1`, `ACLA-1.0-Enterprise`), (2) expand `templates.py` and `template` command with `al-pu`, `acla`, `cla`, `asset-policy`, and `backward-compat`, and (3) update `auditor.py` to recognize both AGPL-3.0 and AL-PU-1.0 bases, with an optional `--check-policies` verification flag.
- **Consequences**: Provides end-to-end tooling for both the present dual-licensing setup and future custom license transitions with 36 passing unit tests.
