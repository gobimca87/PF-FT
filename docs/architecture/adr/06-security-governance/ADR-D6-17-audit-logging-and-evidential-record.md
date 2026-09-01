---
id: ADR-D6-17
title: Audit logging and evidential record model
domain: 6 Security & Governance
ws_ref: [WS-29]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [AI Governance Lead, SRE, Data Protection Officer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-02, ADR-D7-04, ADR-D6-14, ADR-D6-15, ADR-D7-03]
source_docs:
  - "MD files/5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md §29, §30, §71, §81, §99"
  - "MD files/1 Foundation/5. PF-FT-AI-STATE-MODEL.md §60"
  - "MD files/2 Agent Runtime/6 PF-FT-AI-CONVERSATION-SESSION.md §62"
build_phases: [10]
impacted_paths:
  - src/pf_ft_ai/observability/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-17 — Audit logging and evidential record model

## 1. Summary

PFF AI will keep an **append-only, tamper-evident evidential record** of decisions and
consequential events — HIL decisions (ADR-D6-14), change approvals (ADR-D6-15),
authorization decisions, tool/enterprise actions, state transitions and RAG/ACL
outcomes — separate from operational logs, redacted of unnecessary PII, retained to a
defined schedule, and queryable for compliance evidence (20.PF-FT-AI-GOVERNANCE.md §29–§30, §71, §81, §99;
5. PF-FT-AI-STATE-MODEL.md §60; 6 PF-FT-AI-CONVERSATION-SESSION.md §62). Audit is for accountability, not debugging.

## 2. Context and Problem Statement

20.PF-FT-AI-GOVERNANCE.md §29–§30 traceability/auditability, §71 HIL evidence, §81 approval evidence, §99
compliance evidence; 5. PF-FT-AI-STATE-MODEL.md §60 state-transition audit; 6 PF-FT-AI-CONVERSATION-SESSION.md §62 conversation audit.
Operational logs (ADR-D7-04) are for debugging and rotate quickly; compliance and
safeguarding require a durable, tamper-evident record of *what was decided and by whom*.
This ADR fixes the evidential-record model distinct from operational logging.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Append-only, tamper-evident audit trail | 20.PF-FT-AI-GOVERNANCE.md §30; 5. PF-FT-AI-STATE-MODEL.md §60 |
| DR-F-02 | Capture decisions/consequential events | 20.PF-FT-AI-GOVERNANCE.md §71, §81; 6 PF-FT-AI-CONVERSATION-SESSION.md §62 |
| DR-C-01 | Redact unnecessary PII in audit | ADR-D7-04; UK GDPR |
| DR-F-03 | Defined retention + queryable evidence | 20.PF-FT-AI-GOVERNANCE.md §99 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Audit volume is manageable | Sample/tier audit | Volume review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Evidential integrity (tamper-evident) | 28 | Trustworthy record | Immutability |
| EC-02 | Coverage of decisions/events | 24 | Accountability | Event coverage |
| EC-03 | Privacy (redaction, retention) | 18 | UK GDPR | Redaction/retention |
| EC-04 | Queryability for compliance | 16 | Evidence on demand | Query support |
| EC-05 | Cost/operability | 14 | Sustainable | Storage/ops |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Dedicated append-only tamper-evident audit store, redacted, retained, queryable

**Description.** A separate audit sink (append-only, hash-chained/immutable, e.g.
immutable storage or a WORM-configured log) capturing decision/consequential events with
correlation ids (ADR-D7-03), redacted PII (ADR-D7-04), defined retention, queryable for
evidence.
**Strengths.** Integrity, coverage, privacy, evidence-ready.
**Weaknesses.** Separate store to operate.
**Cost / effort.** Medium.

### 5.2 Option B — Reuse operational logs as the audit trail

**Description.** Treat app logs as audit.
**Strengths.** No extra store.
**Weaknesses.** Logs rotate/are mutable; noisy; not tamper-evident; privacy-mixed.
**Cost / effort.** Low; non-compliant as evidence.

### 5.3 Option C — Langfuse traces as the audit record

**Description.** Use AI-observability traces (ADR-D7-02).
**Strengths.** Rich AI context.
**Weaknesses.** Traces are for observability, not tamper-evident evidence; retention/
immutability differ; may hold sensitive prompt data.
**Cost / effort.** Low; wrong tool for evidence.

### 5.4 Option D — Enterprise system of record holds all audit

**Description.** Rely on PFF to audit everything.
**Strengths.** Single source.
**Weaknesses.** AI-specific decisions (HIL, guardrail, routing) aren't visible to PFF;
gaps.
**Cost / effort.** Low; gaps.

### 5.5 Option E — Dedicated audit store + cryptographic verifiability (signed/hash-chained) + SIEM export

**Description.** Option A with cryptographic hash-chaining/signing and export to a SIEM
for monitoring/retention.
**Strengths.** Strongest integrity + security monitoring.
**Weaknesses.** More setup.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No audit trail | 20.PF-FT-AI-GOVERNANCE.md §30 |
| Mutable audit records | Not evidential |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 20.PF-FT-AI-GOVERNANCE.md §29–§30/§71/§81/§99, 5. PF-FT-AI-STATE-MODEL.md
§60, 6 PF-FT-AI-CONVERSATION-SESSION.md §62.

| Criterion | Weight | A: Dedicated audit | B: Ops logs | C: Langfuse | D: Enterprise-only | E: A+crypto+SIEM |
|---|---|---|---|---|---|---|
| EC-01 Integrity | 28 | 5 | 2 | 2 | 3 | 5 |
| EC-02 Coverage | 24 | 5 | 3 | 4 | 2 | 5 |
| EC-03 Privacy | 18 | 5 | 2 | 2 | 4 | 5 |
| EC-04 Queryability | 16 | 4 | 3 | 4 | 3 | 5 |
| EC-05 Cost/ops | 14 | 4 | 5 | 4 | 4 | 3 |
| **Weighted total** | **100** | **472** | **288** | **312** | **304** | **488** |

Totals (×20): **E = 488**, **A = 472**, **C = 312**, **D = 304**, **B = 288**.

**Sensitivity.** E (A + cryptographic verifiability + SIEM export) edges A given the
safeguarding/compliance stakes; hash-chaining/signing makes the record provably
tamper-evident and SIEM export adds security monitoring. A is the baseline; crypto+SIEM
is adopted for the strongest assurance.

## 7. Decision

**PFF AI will maintain a dedicated append-only, cryptographically verifiable
(hash-chained/signed) audit store capturing decisions and consequential events —
HIL decisions, change approvals, authorization decisions, tool/enterprise actions,
state transitions, RAG/ACL outcomes — with PII redaction, defined retention, query
support and SIEM export (Option E).** Operational logs (B), Langfuse traces (C) and
enterprise-only audit (D) are rejected as the evidential record (they complement it).

## 8. Architecture Detail

- `src/pf_ft_ai/observability/`: an audit writer emits structured, redacted audit events
  (with correlation id, ADR-D7-03) to an append-only/WORM store; hash-chaining/signing
  provides tamper-evidence.
- Events: HIL (20.PF-FT-AI-GOVERNANCE.md §71; ADR-D6-14), approvals (§81; ADR-D6-15), authz decisions
  (ADR-D6-02/03), tool/enterprise actions, state transitions (5. PF-FT-AI-STATE-MODEL.md §60), RAG/ACL
  outcomes (ADR-D6-12), conversation audit (6 PF-FT-AI-CONVERSATION-SESSION.md §62).
- PII redaction (ADR-D7-04); retention schedule per classification (ADR-D4-07); SIEM
  export for monitoring; compliance queries supported (§99).
- Audit is separate from operational logs (ADR-D7-04) and Langfuse traces (ADR-D7-02).

## 9. Consequences

### 9.1 Positive
- Trustworthy, queryable, privacy-respecting evidence for compliance/safeguarding.
### 9.2 Negative
- A dedicated store + crypto to operate.
### 9.3 Neutral
- Complements observability (D7-02/04).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of reusing logs | Evidential integrity | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Records who/what decided (human/enterprise) |
| Precedence chain | Audits which source authorised an action |
| Four-state separation | Audit is a distinct evidential plane |
| Versioned artefacts | Audit schema versioned |
| Adam persona governs *how*, not *what* | Audit records facts, not persona wording |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Audit tampering | Low | High | M | Append-only + hash-chain/sign (E) | Security Architect | Low |
| RSK-02 | PII over-retained in audit | Med | High | H | Redaction + retention schedule | DPO | Low |
| RSK-03 | Missing coverage of a decision type | Med | Med | M | Event catalogue + coverage tests | AI Governance Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Consequential events audited | 100% | < 100% | Coverage audit | Per release |
| QM-02 | Audit tamper-evidence verifiable | yes | fail | Integrity check | Continuous |
| QM-03 | PII in audit beyond policy | 0 | > 0 | Redaction tests | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Immutable evidence aids incident response |
| Data classification touched | Confidential audit data |
| Personal data / PII | Redacted; retention-limited |
| Children's data and safeguarding | Safeguarding decisions evidenced (ADR-D6-16) |
| UK GDPR lawful basis and rights impact | Accountability (Art. 5(2)); balanced with minimisation |
| Audit and evidential requirements | This ADR defines them |
| Standards touched | ISO/IEC 27001, 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 10 |
| Repository paths | `src/pf_ft_ai/observability/` |
| Configuration | Audit event catalogue; retention; SIEM export |
| Contracts / schemas | Audit event schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-03, D7-04, D6-14, D6-15 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Audit store is append-only/tamper-evident | Integrity test |
| AC-02 | All consequential event types captured | Coverage audit |
| AC-03 | PII redacted per policy | Redaction test |
| AC-04 | Retention enforced | Retention test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Audit write success; integrity verification; SIEM |
| Alerting | Audit write failure; tamper detection |
| Runbook | `docs/runbooks/audit.md` |
| Failure mode and degradation | Audit-write failure on a consequential action → block/queue (fail safe) |
| Rollback | N/A (append-only) |
| Support model impact | Security + governance |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Audit store + crypto + SIEM | M | storage/SIEM | Azure + SIEM pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | New consequential event type | Change | Add to audit catalogue |
| RT-02 | Audit-integrity incident | Incident | CAR; strengthen controls |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-29 |
| Specification sections | 20.PF-FT-AI-GOVERNANCE.md §29–§30, §71, §81, §99; 5. PF-FT-AI-STATE-MODEL.md §60; 6 PF-FT-AI-CONVERSATION-SESSION.md §62 |
| Requirement IDs | GOV-AUDIT-* |
| Build phases | 10 |
| Code paths | `src/pf_ft_ai/observability/` |
| Configuration | audit catalogue/retention |
| Tests | integrity + coverage suites |
| Upstream ADRs | ADR-D7-03, D6-14, D6-15 |
| Downstream ADRs | ADR-D7-04 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
