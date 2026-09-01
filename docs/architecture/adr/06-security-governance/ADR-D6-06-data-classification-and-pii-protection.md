---
id: ADR-D6-06
title: Data classification, PII protection and data-flow policy
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Data Protection Officer
contributors: [Security Architect, AI Architecture Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-07, ADR-D6-07, ADR-D6-16, ADR-D7-04, ADR-D6-05]
source_docs:
  - "MD files/5 QualityGovernance/19.PFF-FA-AI-SECURITY.md §31, §32, §33, §34"
  - "MD files/4 AI/18.PFF-FA-AI-GUARDRAILS.md §61, §62, §63, §68, §69"
build_phases: [3, 9]
impacted_paths:
  - src/pff_fa_ai/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-06 — Data classification, PII protection and data-flow policy

## 1. Summary

PFF AI will apply **data minimisation and a data-flow policy driven by classification**
(ADR-D4-07): PII is detected/redacted at inputs and outputs where appropriate, only the
minimum necessary data crosses each boundary, and higher-classification data is barred
from lower-controlled sinks (logs, external SLM, cache) (19.PFF-FA-AI-SECURITY.md §31–§34; 18.PFF-FA-AI-GUARDRAILS.md
§61–§63, §68–§69). Guardrails enforce PII handling at the six boundaries (ADR-D6-09).

## 2. Context and Problem Statement

19.PFF-FA-AI-SECURITY.md §31 PII protection, §32 data classification, §33 data-flow policy, §34 data
minimisation; 18.PFF-FA-AI-GUARDRAILS.md §61–§63 PII input/output handling, §68–§69 data classification and
handling policy. FA data is rich in personal and children's data; uncontrolled flow into
logs or external services is a breach. This ADR fixes classification-driven PII
protection and data-flow control at runtime (D4-07 sets the taxonomy; this ADR enforces
it in data paths).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | Data minimisation across boundaries | 19.PFF-FA-AI-SECURITY.md §34; 18.PFF-FA-AI-GUARDRAILS.md §69 |
| DR-F-01 | PII detection/redaction at input/output | 18.PFF-FA-AI-GUARDRAILS.md §61–§63 |
| DR-C-02 | Classification-driven data-flow control | 19.PFF-FA-AI-SECURITY.md §32–§33; 18.PFF-FA-AI-GUARDRAILS.md §68 |
| DR-C-03 | No high-class data in low-controlled sinks | 18.PFF-FA-AI-GUARDRAILS.md §68; ADR-D6-07, D7-04 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | PII detection accurate enough | Tune/augment detectors | PII eval |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Leakage prevention (to logs/external/cache) | 30 | Breach prevention | Leak tests |
| EC-02 | Minimisation effectiveness | 22 | UK GDPR Art. 5 | Data reduced |
| EC-03 | Detection accuracy (PII) | 18 | Redaction quality | Precision/recall |
| EC-04 | Enforceability at boundaries | 18 | Real controls | Guardrail coverage |
| EC-05 | Performance/utility impact | 12 | Over-redaction harms | Utility |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Classification-driven data-flow policy + PII detect/redact at boundaries + minimisation

**Description.** Every boundary applies classification rules: minimise fields, redact PII
before low-controlled sinks (logs ADR-D7-04, external SLM ADR-D6-07, cache), enforced by
guardrails (ADR-D6-09) using PII detectors + allow/deny by classification.
**Strengths.** Strong leakage prevention; minimisation; enforceable.
**Weaknesses.** Detector tuning; some over/under-redaction risk.
**Cost / effort.** Medium.

### 5.2 Option B — Perimeter-only PII control (redact at egress logs only)

**Description.** Only redact where data leaves to logs.
**Strengths.** Simpler.
**Weaknesses.** Misses external SLM/cache flows; no minimisation; partial.
**Cost / effort.** Low; incomplete.

### 5.3 Option C — Manual/annotation-based handling (developers tag sensitive fields)

**Description.** Rely on code annotations to mark sensitive data.
**Strengths.** Precise where applied.
**Weaknesses.** Gaps where forgotten; no automatic detection of free-text PII.
**Cost / effort.** Medium; error-prone.

### 5.4 Option D — Detection-only (detect + alert, no auto-redaction)

**Description.** Detect PII and alert, but don't redact.
**Strengths.** Visibility; no utility loss.
**Weaknesses.** Data still flows; not prevention.
**Cost / effort.** Low; not protective.

### 5.5 Option E — Tokenization/pseudonymisation of identifiers + redaction of free-text PII

**Description.** Option A plus tokenizing stable identifiers so downstream can operate on
tokens, reversing only where authorised.
**Strengths.** Strong minimisation while preserving referential utility.
**Weaknesses.** Token vault to manage; complexity.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No PII control | UK GDPR; 19.PFF-FA-AI-SECURITY.md §31 |
| Send raw PII to external SLM | ADR-D6-07 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 19.PFF-FA-AI-SECURITY.md §31–§34 and 18.PFF-FA-AI-GUARDRAILS.md
§61–§63/§68–§69.

| Criterion | Weight | A: Class-driven+redact | B: Perimeter logs | C: Annotation | D: Detect-only | E: A+tokenization |
|---|---|---|---|---|---|---|
| EC-01 Leakage prevention | 30 | 5 | 2 | 3 | 1 | 5 |
| EC-02 Minimisation | 22 | 5 | 2 | 3 | 1 | 5 |
| EC-03 Detection accuracy | 18 | 4 | 3 | 2 | 4 | 4 |
| EC-04 Enforceability | 18 | 5 | 3 | 2 | 3 | 5 |
| EC-05 Utility impact | 12 | 3 | 5 | 4 | 5 | 4 |
| **Weighted total** | **100** | **456** | **288** | **278** | **256** | **476** |

Totals (×20): **E = 476**, **A = 456**, **B = 288**, **C = 278**, **D = 256**.

**Sensitivity.** E (A + tokenization) edges A by preserving referential utility while
minimising — valuable given canonical identifiers (ADR-D4-08). Tokenization adds a
token-vault dependency, so **A is the baseline and tokenization is adopted where
referential utility on identifiers is needed** (E as targeted enhancement). B/C/D are
insufficient.

## 7. Decision

**PFF AI will enforce a classification-driven data-flow policy with data minimisation
and PII detection/redaction at boundaries (Option A), adding tokenization/
pseudonymisation of identifiers where downstream referential utility is needed
(Option E enhancement).** Higher-classification data is barred from lower-controlled
sinks (logs ADR-D7-04, external SLM ADR-D6-07, cache); guardrails enforce this at the
six boundaries (ADR-D6-09). Perimeter-only (B), annotation-only (C) and detect-only (D)
are rejected.

## 8. Architecture Detail

- Classification from ADR-D4-07 drives per-boundary rules; a PII detector/redactor runs
  at input (18.PFF-FA-AI-GUARDRAILS.md §62), output (§63) and before low-controlled sinks.
- Minimisation: only required fields cross each boundary (19.PFF-FA-AI-SECURITY.md §34); ERC collects
  minimally (ADR-D4-04).
- Enforcement via guardrails (ADR-D6-09); log redaction (ADR-D7-04); external-SLM
  boundary (ADR-D6-07). Tokenization for identifiers where needed, with a controlled
  reverse path.

## 9. Consequences

### 9.1 Positive
- Strong leakage prevention + minimisation; classification actually enforced in flows.
### 9.2 Negative
- Detector tuning; tokenization adds a vault where used.
### 9.3 Neutral
- Implements the D4-07 taxonomy at runtime.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Some convenience/utility | Leakage prevention + minimisation | DPO |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | AI minimises/redacts; enterprise owns records |
| Precedence chain | Redaction never alters authoritative enterprise data at source |
| Four-state separation | Classification enforced per state/sink |
| Versioned artefacts | Policy/detectors versioned |
| Adam persona governs *how*, not *what* | Persona never reveals redacted PII |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | PII leaks to logs/external | Med | High | H | Redaction + classification gates + tests | Security Architect | Low |
| RSK-02 | Detector misses PII | Med | High | H | Tuned detectors + minimisation as backstop | DPO | Med |
| RSK-03 | Over-redaction harms utility | Med | Med | M | Utility eval; targeted rules | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | PII in logs/external sinks | 0 | > 0 | Leak tests | Continuous |
| QM-02 | PII detection recall | ≥ target | below | PII eval | Per release |
| QM-03 | Minimisation coverage at boundaries | 100% | < 100% | Audit | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Reduces PII exposure across flows |
| Data classification touched | Drives all bands (D4-07) |
| Personal data / PII | Detected, minimised, redacted |
| Children's data and safeguarding | Special-category handling (ADR-D6-16) |
| UK GDPR lawful basis and rights impact | Minimisation (Art. 5), security (Art. 32) |
| Audit and evidential requirements | Redaction/minimisation logged |
| Standards touched | UK GDPR, ISO/IEC 27701, 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 3, 9 |
| Repository paths | `src/pff_fa_ai/` (guardrails, boundaries) |
| Configuration | Classification rules; detector config |
| Contracts / schemas | Redaction/minimisation policy |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-07, D6-07, D6-09, D7-04 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No PII in logs/external sinks | Leak tests |
| AC-02 | Minimisation applied at each boundary | Audit |
| AC-03 | PII detection meets recall target | Eval |
| AC-04 | High-class data barred from low sinks | Boundary tests |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | PII detection hits; redaction rate |
| Alerting | PII-in-sink detection |
| Runbook | `docs/runbooks/data-protection.md` |
| Failure mode and degradation | Uncertain classification → treat as higher (fail safe) |
| Rollback | Policy/detector revert |
| Support model impact | DPO + security |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Detectors + policy | M | small | Build + inference |
| Token vault (if used) | M | small | Where tokenization applied |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Referential utility needs grow | Design | Expand tokenization (E) |
| RT-02 | PII-leak incident | Incident | CAR; tune detectors/policy |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | 19.PFF-FA-AI-SECURITY.md §31–§34; 18.PFF-FA-AI-GUARDRAILS.md §61–§63, §68–§69 |
| Requirement IDs | SEC-PII-* |
| Build phases | 3, 9 |
| Code paths | guardrails/boundaries |
| Configuration | classification/detector |
| Tests | PII leak + eval suites |
| Upstream ADRs | ADR-D4-07 |
| Downstream ADRs | ADR-D6-07, D6-09, D6-16, D7-04 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Data Protection Officer | Initial decision recorded. |
