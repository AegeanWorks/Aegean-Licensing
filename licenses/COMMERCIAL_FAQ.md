# AegeanWorks Commercial Licensing FAQ

Frequently asked questions regarding open source compliance, commercial licensing, and the Aegean-E Commercial License (AECL-1.0).

---

### Q1: Can I use AegeanWorks software commercially for free?
**Yes.** The open-source track uses the GNU Affero General Public License v3.0 (AGPL-3.0). Free software licenses allow commercial usage. However, you must strictly comply with AGPL-3.0 requirements:
- If you distribute modified binaries or packages, you must provide corresponding source code under AGPL-3.0.
- Under Section 13, if you run a modified version of the program over a network (e.g. as a hosted web service or SaaS), you must offer remote users access to the corresponding source code of your modified version.

### Q2: Why would a company purchase an AECL-1.0 license?
Organizations purchase an AECL-1.0 license when they want to:
- Build proprietary, closed-source cloud SaaS or on-premises products without disclosing internal source code or backend modifications.
- Embed AegeanWorks libraries into commercial products without triggering AGPL copyleft obligations.
- Operate with legal certainty without needing to audit whether internal architecture constitutes remote network interaction under AGPL-3.0 Section 13.

### Q3: What is included with the AECL-1.0 license?
The AECL-1.0 is a pure copyright permissions grant and copyleft waiver. It is sold "AS-IS".
- **Included**: Irrevocable/perpetual rights to deploy versions released during the license term in proprietary, closed-source environments.
- **Not Included**: Technical support, custom feature engineering, SLA guarantees, phone consulting, or legal indemnification.

### Q4: How does AegeanWorks deliver and verify licenses?
Licensing is fast, digital, and verifiable. Upon purchase, AegeanWorks issues an authentic **License Grant Certificate** (`.json` and `.md`) signed with a SHA-256 integrity digest and optional cryptographic signature.
You can verify any certificate using our local CLI:
```bash
python -m aegean_licensing verify certificate.json
```

### Q5: How do I request a commercial quote or license?
Send an email to:
**`aegean-licensing@proton.me`**  
Include:
1. Licensee Entity Name (company or individual)
2. Project(s) you wish to license (e.g. Chronos, NeuralBeat, AIKit, or Full Portfolio)
3. Intended use case (e.g. closed SaaS, embedded hardware, proprietary redistribution)
