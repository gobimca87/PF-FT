---
id: ADR-D6-05
title: Encryption in transit/at rest, key management and rotation
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [Platform Engineer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-07, ADR-D6-04, ADR-D4-10, ADR-D3-24, ADR-D6-06]
source_docs:
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §25, §26, §27, §28, §29, §30"
  - "MD files/6 Production/25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §58, §59, §60"
build_phases: [1, 7]
impacted_paths:
  - infra/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-05 — Encryption in transit/at rest, key management and rotation

## 1. Summary

PFF AI will enforce **TLS 1.2+ in transit everywhere and encryption at rest on all
stores**, using **Azure-managed keys by default and customer-managed keys (CMK) in Key
Vault for Confidential/Personal/special-category data**, with defined **rotation** and
no secrets/keys in code or images (19.PF-FT-AI-SECURITY.md §25–§30; 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §58–§60). Keys are managed in
Key Vault (ADR-D5-07); certificates are automatically managed.

## 2. Context and Problem Statement

19.PF-FT-AI-SECURITY.md §25 TLS, §26 encryption at rest, §27 key management, §28 secret references, §29
secret rotation, §30 secret-exposure prevention; 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §58 encryption, §59 TLS, §60
certificate management. Unencrypted data or unmanaged keys are baseline compliance
failures for FA personal/children's data. This ADR fixes encryption and key management.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | TLS in transit; encryption at rest everywhere | 19.PF-FT-AI-SECURITY.md §25–§26; 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §58–§59 |
| DR-F-01 | Key management in Key Vault; rotation | 19.PF-FT-AI-SECURITY.md §27, §29 |
| DR-C-02 | CMK for sensitive data | 19.PF-FT-AI-SECURITY.md §26–§27 |
| DR-C-03 | No keys/secrets in code/images | 19.PF-FT-AI-SECURITY.md §30; ADR-D5-07 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Azure PaaS supports CMK where needed | Managed keys + compensating controls | Service review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Confidentiality coverage (transit+rest) | 30 | Baseline requirement | Coverage |
| EC-02 | Key control (CMK where needed) | 22 | Sovereignty/compliance | CMK usage |
| EC-03 | Rotation + exposure prevention | 20 | Reduce window | Rotation cadence |
| EC-04 | Operability | 16 | Manage keys/certs | Automation |
| EC-05 | Cost | 12 | HSM/CMK cost | £ |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — TLS everywhere + at-rest encryption; managed keys default, CMK for sensitive; KV-managed rotation

**Description.** TLS 1.2+ enforced; all stores encrypted at rest; Azure-managed keys by
default, CMK in Key Vault for Confidential/Personal/special-category; automated cert
management; scheduled rotation; secrets by reference (ADR-D5-07).
**Strengths.** Full coverage; key control where it matters; rotation; balanced cost.
**Weaknesses.** CMK adds some management.
**Cost / effort.** Low-medium.

### 5.2 Option B — Managed keys only (no CMK)

**Description.** Rely entirely on platform-managed keys.
**Strengths.** Simplest.
**Weaknesses.** Less key sovereignty/control for sensitive data; weaker for
compliance narratives around children's data.
**Cost / effort.** Low; weaker control.

### 5.3 Option C — CMK everywhere (all data)

**Description.** CMK for every store.
**Strengths.** Maximum control.
**Weaknesses.** Management/cost overhead for low-sensitivity data with little benefit.
**Cost / effort.** Higher; over-applied.

### 5.4 Option D — Application-layer encryption (encrypt fields in app before storage)

**Description.** App encrypts sensitive fields itself.
**Strengths.** Defence-in-depth for specific fields.
**Weaknesses.** Key handling in app; complexity; complements, not replaces, at-rest
encryption. Useful for specific ultra-sensitive fields only.
**Cost / effort.** Medium.

### 5.5 Option E — HSM-backed keys (Managed HSM) for sensitive data

**Description.** Use Azure Managed HSM for CMK.
**Strengths.** FIPS 140-2 L3; strongest key protection.
**Weaknesses.** Higher cost; may exceed current requirements.
**Cost / effort.** High.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Plaintext at rest | 19.PF-FT-AI-SECURITY.md §26 |
| Self-managed keys in code | 19.PF-FT-AI-SECURITY.md §30 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 19.PF-FT-AI-SECURITY.md §25–§30 and 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §58–§60.

| Criterion | Weight | A: Managed+CMK-sensitive | B: Managed only | C: CMK everywhere | D: App-layer | E: HSM |
|---|---|---|---|---|---|---|
| EC-01 Coverage | 30 | 5 | 5 | 5 | 4 | 5 |
| EC-02 Key control | 22 | 5 | 2 | 5 | 4 | 5 |
| EC-03 Rotation/exposure | 20 | 5 | 4 | 5 | 3 | 5 |
| EC-04 Operability | 16 | 4 | 5 | 3 | 2 | 2 |
| EC-05 Cost | 12 | 4 | 5 | 2 | 3 | 1 |
| **Weighted total** | **100** | **472** | **408** | **424** | **340** | **404** |

Totals (×20): **A = 472**, **C = 424**, **B = 408**, **E = 404**, **D = 340**.

**Sensitivity.** A leads; CMK-everywhere (C) is close but over-applies CMK to
low-sensitivity data; HSM (E) is a targeted upgrade for the most sensitive keys if
compliance demands FIPS L3 (RT-01). App-layer (D) is a complement for specific fields.

## 7. Decision

**PFF AI will enforce TLS 1.2+ in transit and encryption at rest on all stores, using
Azure-managed keys by default and Key-Vault CMK for Confidential/Personal/special-
category data, with automated certificate management and scheduled key/secret rotation
(Option A).** HSM-backed keys (E) may be adopted for the most sensitive keys if required;
application-layer encryption (D) may protect specific ultra-sensitive fields. Plaintext
at rest and in-code keys are forbidden.

## 8. Architecture Detail

- TLS enforced at APIM, ingress and all service-to-service hops (25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §59); cert
  management automated (§60).
- At-rest encryption on Redis (ADR-D4-10), vector store (ADR-D3-24), any storage; CMK in
  Key Vault (ADR-D5-07) for sensitive stores; rotation scheduled (§29).
- Secrets by reference only (ADR-D5-07); no keys in code/images (§30); rotation without
  redeploy.

## 9. Consequences

### 9.1 Positive
- Baseline + sensitive-data key control; rotation reduces exposure window.
### 9.2 Negative
- CMK/rotation management overhead.
### 9.3 Neutral
- Interlocks with secrets (D5-07) and classification (D6-06).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of managed-only | Key control for sensitive data | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Crypto protects data; no business authority |
| Precedence chain | N/A |
| Four-state separation | Each store encrypted per classification |
| Versioned artefacts | Crypto config in IaC |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Key compromise | Low | High | M | CMK + rotation + KV access control | Security Architect | Low |
| RSK-02 | Unencrypted store slips in | Low | High | M | Policy-as-code enforce encryption | Platform Eng | Low |
| RSK-03 | Rotation breaks a dependency | Low | Med | M | Versioned keys; staged rotation | Platform Eng | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Stores encrypted at rest | 100% | < 100% | Config scan | Continuous |
| QM-02 | TLS-only endpoints | 100% | < 100% | Scan | Continuous |
| QM-03 | Key/secret rotation adherence | per policy | overdue | KV audit | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Encrypted transit/rest reduces data-loss impact |
| Data classification touched | CMK for Confidential/Personal/special-category |
| Personal data / PII | Encrypted with controlled keys |
| Children's data and safeguarding | Sensitive stores CMK-protected |
| UK GDPR lawful basis and rights impact | Security-of-processing (Art. 32) |
| Audit and evidential requirements | Key ops + rotation logged |
| Standards touched | ISO/IEC 27001, 27701, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1, 7 |
| Repository paths | `infra/` |
| Configuration | Encryption + CMK + rotation policy |
| Contracts / schemas | N/A |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-07, D6-04, D6-06 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All stores encrypted at rest | Config scan |
| AC-02 | CMK used for sensitive stores | KV/store audit |
| AC-03 | TLS enforced on all hops | Scan |
| AC-04 | Rotation performed per policy | Audit |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Cert expiry; key rotation; encryption posture |
| Alerting | Cert expiry; rotation overdue; unencrypted store |
| Runbook | `docs/runbooks/crypto.md` |
| Failure mode and degradation | Cert/key failure → fail closed on affected hop |
| Rollback | Key version rollback (versioned keys) |
| Support model impact | Security + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| CMK in Key Vault | setup | key ops | Azure KV pricing |
| (HSM if adopted) | — | higher | Managed HSM |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | FIPS L3 required | Compliance | Adopt Managed HSM (E) |
| RT-02 | Key-compromise incident | Incident | CAR; rotate + review |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | 19.PF-FT-AI-SECURITY.md §25–§30; 25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §58–§60 |
| Requirement IDs | SEC-CRYPTO-* |
| Build phases | 1, 7 |
| Code paths | `infra/` |
| Configuration | encryption/CMK/rotation |
| Tests | encryption posture scans |
| Upstream ADRs | ADR-D5-07, D6-04 |
| Downstream ADRs | ADR-D6-06 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
