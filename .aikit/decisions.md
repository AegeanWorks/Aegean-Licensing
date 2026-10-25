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
