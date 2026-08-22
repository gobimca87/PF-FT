---
id: ADR-D7-04
title: Logging standards, levels and redaction rules
domain: 7 Operations
ws_ref: [WS-31]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [Backend Lead, Security Architect, Data Protection Officer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-01, ADR-D7-03, ADR-D6-06, ADR-D6-17, ADR-D5-07]
source_docs:
  - "MD files/6 Production/24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §11, §12, §13, §14"
build_phases: [2]
impacted_paths:
  - src/pf_ft_ai/observability/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D7-04 — Logging standards, levels and redaction rules

## 1. Summary

PFF AI will emit **structured JSON logs** with consistent **levels** and **mandatory
redaction of PII/secrets**, carrying the correlation id (ADR-D7-03), to Log Analytics
(ADR-D7-01) — with logs treated as operational (debugging), distinct from the tamper-
evident audit record (ADR-D6-17) (doc 24 §11–§14). No secrets or unnecessary personal
data ever reach logs.

## 2. Context and Problem Statement

Doc 24 §11 application logs, §12 structured logging, §13 log levels, §14 sensitive-data
logging. Unstructured or unredacted logs are both an operability failure and a breach
vector. This ADR fixes logging format, levels and redaction.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Structured JSON logs with correlation id | doc 24 §12; ADR-D7-03 |
| DR-F-02 | Consistent log levels | doc 24 §13 |
| DR-C-01 | Redact PII/secrets | doc 24 §14; ADR-D6-06, D5-07 |
| DR-C-02 | Logs ≠ audit record | ADR-D6-17 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Redaction catches sensitive fields | Structured logging + allowlist fields | Redaction tests |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Sensitive-data safety (redaction) | 30 | Breach prevention | Leak tests |
| EC-02 | Queryability (structured) | 22 | Debugging | Structured coverage |
| EC-03 | Level discipline | 18 | Signal/noise | Level correctness |
| EC-04 | Correlation | 16 | Traceability | Id present |
| EC-05 | Cost (volume) | 14 | Ingestion | £/GB |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Structured JSON + levels + redaction (deny-by-default fields) + correlation

**Description.** JSON logs; standard levels (DEBUG…ERROR); redaction with a
deny-by-default posture for sensitive fields (allowlist safe fields); correlation id on
every line; ship to Log Analytics.
**Strengths.** Safe, queryable, disciplined, correlated.
**Weaknesses.** Redaction/allowlist upkeep.
**Cost / effort.** Low-medium.

### 5.2 Option B — Structured logs, redaction on a denylist (block known-sensitive)

**Description.** JSON + block a list of known-sensitive keys.
**Strengths.** Simpler than allowlist.
**Weaknesses.** New sensitive fields leak until added; weaker than deny-by-default.
**Cost / effort.** Low; gaps.

### 5.3 Option C — Plaintext logs

**Description.** Freeform log strings.
**Strengths.** Easy to write.
**Weaknesses.** Poor query; hard to redact reliably; doc 24 §12 wants structured.
**Cost / effort.** Low; weak.

### 5.4 Option D — Log everything verbosely (debug in prod)

**Description.** Verbose logs always on.
**Strengths.** Max detail.
**Weaknesses.** Cost; noise; higher leak risk.
**Cost / effort.** High cost.

### 5.5 Option E — Structured + allowlist redaction + dynamic log-level control + sampling

**Description.** Option A plus runtime log-level adjustment (per component) and sampling
of high-volume debug logs.
**Strengths.** Safe + cost-controlled + debuggable on demand.
**Weaknesses.** Level-control mechanism to manage.
**Cost / effort.** Low-medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Secrets/PII in logs | doc 24 §14 |
| Logs as the audit trail | ADR-D6-17 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 24 §11–§14.

| Criterion | Weight | A: Allowlist redaction | B: Denylist | C: Plaintext | D: Verbose | E: A+dynamic level+sampling |
|---|---|---|---|---|---|---|
| EC-01 Redaction safety | 30 | 5 | 3 | 2 | 2 | 5 |
| EC-02 Queryability | 22 | 5 | 5 | 2 | 4 | 5 |
| EC-03 Level discipline | 18 | 5 | 4 | 2 | 1 | 5 |
| EC-04 Correlation | 16 | 5 | 5 | 3 | 4 | 5 |
| EC-05 Cost | 14 | 4 | 4 | 3 | 1 | 5 |
| **Weighted total** | **100** | **484** | **424** | **236** | **252** | **500** |

Totals (×20): **E = 500**, **A = 484**, **B = 424**, **D = 252**, **C = 236**.

**Sensitivity.** E (A + dynamic level + sampling) wins by controlling cost/noise while
keeping deny-by-default redaction. Denylist (B) risks leaks of new fields; plaintext (C)
and verbose (D) are poor.

## 7. Decision

**PFF AI will emit structured JSON logs with consistent levels, deny-by-default
redaction (allowlisting safe fields) of PII/secrets, correlation ids, dynamic per-
component log-level control and sampling of high-volume debug logs, shipped to Log
Analytics (Option E).** Logs are operational, distinct from the audit record (ADR-D6-17).
Denylist redaction (B), plaintext (C) and always-verbose (D) are rejected.

## 8. Architecture Detail

- A logging wrapper enforces JSON structure, level, correlation id (ADR-D7-03) and
  redaction (deny-by-default; safe-field allowlist); integrates with the classification/
  PII policy (ADR-D6-06) and secret handling (ADR-D5-07).
- Dynamic level control per component; sampling for DEBUG; ship to Log Analytics
  (ADR-D7-01). Sensitive events go to the audit store (ADR-D6-17), not logs.

## 9. Consequences

### 9.1 Positive
- Safe, queryable, cost-controlled logs correlated to requests.
### 9.2 Negative
- Redaction allowlist + level-control upkeep.
### 9.3 Neutral
- Distinct from audit + Langfuse.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Verbose-always convenience | Safety + cost control | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Logs are operational; no business authority |
| Precedence chain | N/A |
| Four-state separation | Logs redacted per classification |
| Versioned artefacts | Log config versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | PII/secret leaks to logs | Med | High | H | Deny-by-default redaction + tests | Security Architect | Low |
| RSK-02 | Log cost overrun | Med | Med | M | Sampling + dynamic levels | FinOps | Low |
| RSK-03 | Over-redaction hides debugging info | Low | Med | M | Safe-field allowlist tuning | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | PII/secrets in logs | 0 | > 0 | Leak tests | Continuous |
| QM-02 | Structured + correlated logs | 100% | < 100% | Log audit | Per release |
| QM-03 | Log ingestion cost | ≤ budget | over | FinOps | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Redaction reduces log-leak vector |
| Data classification touched | Logs redacted per classification |
| Personal data / PII | Deny-by-default redaction |
| Children's data and safeguarding | No safeguarding data in logs |
| UK GDPR lawful basis and rights impact | Minimised log data |
| Audit and evidential requirements | Separate from audit (ADR-D6-17) |
| Standards touched | ISO/IEC 27001, 27701 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 2 |
| Repository paths | `src/pf_ft_ai/observability/` |
| Configuration | Redaction allowlist; levels; sampling |
| Contracts / schemas | Log schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D7-01, D7-03, D6-06, D5-07 |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No PII/secrets in logs | Leak tests |
| AC-02 | Logs structured + correlated | Log audit |
| AC-03 | Dynamic level control works | Ops test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Log volume; error-log rate |
| Alerting | PII-in-log detection; error spikes |
| Runbook | `docs/runbooks/logging.md` |
| Failure mode and degradation | Log pipeline loss doesn't stop serving |
| Rollback | Config revert |
| Support model impact | SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Log ingestion | — | per-GB | Log Analytics pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Log cost too high | QM-03 | Increase sampling; tighten levels |
| RT-02 | Log-leak incident | Incident | CAR; expand redaction |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-31 |
| Specification sections | doc 24 §11–§14 |
| Requirement IDs | OBS-LOG-* |
| Build phases | 2 |
| Code paths | `src/pf_ft_ai/observability/` |
| Configuration | redaction/levels |
| Tests | log leak + structure suites |
| Upstream ADRs | ADR-D7-01, D6-06 |
| Downstream ADRs | ADR-D6-17 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
