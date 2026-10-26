# Security SLA Exhibit (Draft)

**Version 1.0-draft — October 2026**
**Status**: optional exhibit; effective only when an Order Form names it

This exhibit defines security-response commitments for a commercial licensee. Without a signed
Order Form that names it, ACL-1.0 provides no SLA and the public
[Security Disclosure Policy](../../policies/SECURITY-DISCLOSURE.md) is the only process.

## 1. Scope

- **Covered versions**: the versions listed in the Order Form.
- **Covered products**: the product or service named in the Order Form.
- **Channels**: reports sent to the private security contact in the Order Form.

## 2. Response targets

| Severity | Acknowledgement | Triage | Fix or mitigation target |
|---|---|---|---|
| Critical (remote code execution, key compromise, mass data exposure) | 1 business day | 2 business days | 7 calendar days |
| High (privilege escalation, authentication bypass, serious data exposure) | 2 business days | 5 business days | 30 calendar days |
| Medium | 5 business days | 10 business days | next scheduled release |
| Low | 10 business days | next release | best effort |

Targets are goals, not guarantees. A complex fix may need a longer window agreed in writing.

## 3. Commitments

1. A named security contact and a private channel.
2. A written acknowledgement with a tracking reference.
3. A remediation plan for Critical and High issues.
4. A coordinated-disclosure date; the default is 90 days after acknowledgement.
5. A credit line in the advisory unless the reporter declines.
6. Notice of a confirmed compromise that affects the licensee's data without undue delay.

## 4. Exclusions

- vulnerabilities in third-party dependencies, platforms, storefronts or the licensee's own code;
- a modified build, a misconfiguration or an unsupported version;
- denial-of-service, spam, phishing, physical attacks and social engineering;
- a report without a reproducible impact;
- a failure caused by the licensee's breach of the Agreement.

## 5. Fees and term

The fee, term and covered versions are in the Order Form. This exhibit ends with the Order Form;
the confidentiality and coordinated-disclosure obligations survive for two years.

## 6. No warranty

This exhibit is a service commitment, not a warranty that the software is free of vulnerabilities.
The AS-IS and liability terms of ACL-1.0 and the Order Form apply.
