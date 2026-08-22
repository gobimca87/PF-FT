---
id: ADR-D6-07
title: External SLM data boundary — what may leave the tenancy
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
related_adrs: [ADR-D3-13, ADR-D6-06, ADR-D6-04, ADR-D3-14, ADR-D6-16]
source_docs:
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §22, §23, §24"
  - "MD files/4 AI/18.PF-FT-AI-GUARDRAILS.md §70, §71"
  - "MD files/4 AI/15.PF-FT-AI-SLM.md §124, §125, §126"
build_phases: [6, 20]
impacted_paths:
  - src/pf_ft_ai/slm/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-07 — External SLM data boundary — what may leave the tenancy

## 1. Summary

While the SLM runs on the external Hugging Face API (initial phase, ADR-D3-13), PFF AI
will **strictly bound what may leave the Azure tenancy**: only the minimum
non-personal, redacted text needed for generation; **no special-category or children's
personal data**, no secrets, no raw enterprise records — enforced at the external-SLM
boundary guardrail (doc 19 §22–§24; doc 18 §70–§71; doc 15 §124–§126). Flows that would
require sending sensitive data are prioritised for the in-tenancy self-hosted SLM.

## 2. Context and Problem Statement

Doc 19 §22 SLM network security, §23 external-SLM data boundary, §24 self-hosted SLM
security; doc 18 §70 external-SLM boundary, §71 self-hosted boundary; doc 15 §124–§126
data residency/sensitive-data/minimisation. Sending text to an external inference API is
a cross-tenancy data transfer with GDPR and safeguarding implications. This ADR fixes
exactly what may cross that boundary and when.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | Minimise + control what leaves the tenancy | doc 19 §23; doc 15 §126 |
| DR-C-02 | No special-category/children's data externally | ADR-D6-16; doc 15 §125 |
| DR-F-01 | Boundary guardrail enforces the policy | doc 18 §70 |
| DR-C-03 | Prioritise sensitive flows for self-host | ADR-D3-13; doc 19 §24 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Redaction/minimisation makes most flows externally safe | Self-host sooner | Data-flow review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Sensitive-data protection (no egress) | 34 | GDPR/safeguarding | Boundary tests |
| EC-02 | Enforceability at boundary | 22 | Real control | Guardrail coverage |
| EC-03 | Utility (flows still work) | 18 | Ship value | Flows enabled |
| EC-04 | Auditability of transfers | 14 | Accountability | Transfer logs |
| EC-05 | Simplicity/clarity | 12 | Team follows | Policy clarity |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Minimise+redact; deny special-category/children's/secrets externally; boundary guardrail; sensitive flows → self-host

**Description.** A boundary guardrail inspects every external-SLM payload: minimise
fields, redact PII (ADR-D6-06), hard-block special-category/children's data and secrets;
such flows are routed to self-host (or deferred until self-host).
**Strengths.** Protects the most sensitive data; enforceable; keeps most flows working.
**Weaknesses.** Some flows blocked until self-host.
**Cost / effort.** Low-medium.

### 5.2 Option B — Send everything (rely on provider DPA)

**Description.** Trust the provider contractually; send full context.
**Strengths.** Simplest; all flows work now.
**Weaknesses.** Cross-tenancy transfer of sensitive/children's data; unacceptable
GDPR/safeguarding risk.
**Cost / effort.** Low; unacceptable.

### 5.3 Option C — Block all external SLM (self-host from day one)

**Description.** No external inference at all.
**Strengths.** Maximum protection.
**Weaknesses.** Contradicts ADR-D3-13 phased strategy; delays time-to-value; GPU ops up
front.
**Cost / effort.** High up-front.

### 5.4 Option D — Anonymise/pseudonymise everything before external send

**Description.** Transform all identifiers/PII before egress, send anonymised context.
**Strengths.** Enables more flows externally.
**Weaknesses.** Anonymisation of free text is imperfect; residual re-identification risk
for children's data; better as a complement to A's hard blocks.
**Cost / effort.** Medium.

### 5.5 Option E — Azure OpenAI (in-Azure-region external model) for sensitive flows

**Description.** Use an in-region managed model for flows needing more context.
**Strengths.** Keeps data in Azure region; managed.
**Weaknesses.** Still a distinct service boundary; conflicts with the self-hosted-SLM
target/cost posture (ADR-D3-13); a fallback, not the base policy.
**Cost / effort.** Medium; strategic tension.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No boundary control | doc 19 §23; unacceptable |
| Log external payloads in full | PII leakage (ADR-D7-04) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 19 §22–§24, doc 18 §70–§71, doc
15 §124–§126.

| Criterion | Weight | A: Minimise+block sensitive | B: Send all | C: Block external | D: Anonymise all | E: Azure OpenAI |
|---|---|---|---|---|---|---|
| EC-01 Sensitive protection | 34 | 5 | 1 | 5 | 3 | 4 |
| EC-02 Enforceability | 22 | 5 | 1 | 5 | 3 | 4 |
| EC-03 Utility | 18 | 4 | 5 | 2 | 5 | 5 |
| EC-04 Auditability | 14 | 5 | 2 | 5 | 4 | 4 |
| EC-05 Simplicity | 12 | 4 | 5 | 4 | 3 | 4 |
| **Weighted total** | **100** | **468** | **228** | **436** | **352** | **416** |

Totals (×20): **A = 468**, **C = 436**, **E = 416**, **D = 352**, **B = 228**.

**Sensitivity.** A leads; block-all (C) is close but sacrifices the phased time-to-value
of ADR-D3-13. Azure OpenAI (E) is a viable *in-region fallback* for specific flows
needing more context before self-host. Anonymise-all (D) complements A but cannot be the
sole control for children's data. Send-all (B) is unacceptable.

## 7. Decision

**While on the external SLM, PFF AI will minimise and redact payloads, hard-block
special-category data, children's personal data and secrets from leaving the tenancy,
enforce this at an external-SLM boundary guardrail, and route/defer such flows to the
in-tenancy self-hosted SLM (Option A).** An in-Azure-region managed model (E) is a
permitted fallback for specific flows needing more context pre-self-host;
anonymisation (D) complements the hard blocks. Send-all (B) is forbidden; block-all (C)
is unnecessary given the controls.

## 8. Architecture Detail

- The external-SLM boundary guardrail (doc 18 §70; ADR-D6-09) inspects each payload:
  minimise (ADR-D6-06), redact PII, and hard-block special-category/children's/secret
  content; blocked flows are marked for self-host routing (ADR-D3-14 provider selection).
- Transfers are logged (redacted) for audit (ADR-D6-17); egress restricted to the
  provider endpoint only (ADR-D6-04).
- On self-host cutover (ADR-D3-13/D5-10), the external boundary tightens further and the
  HF egress allowlist entry is removed.

## 9. Consequences

### 9.1 Positive
- The most sensitive data never leaves the tenancy; most flows still ship early.
### 9.2 Negative
- Some flows blocked/deferred until self-host.
### 9.3 Neutral
- Boundary tightens after self-host cutover.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Full context to external model | Sensitive-data protection | DPO |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Enterprise records never sent raw externally |
| Precedence chain | External model is lowest authority; boundary protects data |
| Four-state separation | Enterprise/ERC data minimised before any egress |
| Versioned artefacts | Boundary policy versioned |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Children's/special-category data egress | Low | Critical | H | Hard block + guardrail + tests | DPO | Low |
| RSK-02 | Redaction miss sends PII externally | Med | High | H | Minimisation backstop; prioritise self-host | Security Architect | Med |
| RSK-03 | Flow blocked, UX gap | Med | Med | M | Route to Azure OpenAI (E) or self-host | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Special-category/children's data egress | 0 | > 0 | Boundary tests | Continuous |
| QM-02 | External payloads minimised/redacted | 100% | < 100% | Audit | Per release |
| QM-03 | Sensitive flows on self-host | rising to 100% | stalled | Config audit | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Controls a cross-tenancy transfer path |
| Data classification touched | Blocks special-category/Personal externally |
| Personal data / PII | Minimised/redacted; sensitive blocked |
| Children's data and safeguarding | Never sent to external model |
| UK GDPR lawful basis and rights impact | International-transfer + minimisation controls |
| Audit and evidential requirements | Transfers logged (redacted) |
| Standards touched | UK GDPR, ISO/IEC 27701, 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 6 (external), 20 (self-host tighten) |
| Repository paths | `src/pf_ft_ai/slm/` (boundary guardrail) |
| Configuration | Boundary policy; block lists |
| Contracts / schemas | Payload inspection policy |
| Migration | Tighten on self-host cutover |
| Dependencies on other ADRs | ADR-D3-13, D6-06, D6-04, D6-16 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Special-category/children's data never egresses | Boundary tests |
| AC-02 | Payloads minimised/redacted before send | Audit |
| AC-03 | Blocked flows routed to self-host/fallback | Integration test |
| AC-04 | Transfers logged (redacted) | Log test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | External-payload inspection; block rate |
| Alerting | Any sensitive-egress attempt |
| Runbook | `docs/runbooks/slm-boundary.md` |
| Failure mode and degradation | Uncertain → block + route to self-host |
| Rollback | Policy revert |
| Support model impact | DPO + security |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Boundary guardrail | M | small | Build + inspection |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Self-host live | ADR-D5-10 | Tighten/close external boundary |
| RT-02 | Sensitive-egress incident | Incident | CAR; strengthen blocks |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | doc 19 §22–§24; doc 18 §70–§71; doc 15 §124–§126 |
| Requirement IDs | SEC-SLM-BND-* |
| Build phases | 6, 20 |
| Code paths | `src/pf_ft_ai/slm/` |
| Configuration | boundary policy |
| Tests | boundary + egress suites |
| Upstream ADRs | ADR-D3-13, D6-06 |
| Downstream ADRs | ADR-D6-16 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Data Protection Officer | Initial decision recorded. |
