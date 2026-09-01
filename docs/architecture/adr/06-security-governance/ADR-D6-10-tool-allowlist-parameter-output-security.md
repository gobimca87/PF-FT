---
id: ADR-D6-10
title: Tool allowlist, parameter and output security
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [AI Architecture Lead, Backend Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-04, ADR-D2-09, ADR-D6-03, ADR-D6-09, ADR-D2-13]
source_docs:
  - "MD files/4 AI/18.PF-FT-AI-GUARDRAILS.md §38, §39, §40, §41, §42, §43, §44, §45, §46"
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §53, §54, §55, §56, §58, §59, §60"
build_phases: [9]
impacted_paths:
  - src/pf_ft_ai/harness/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-10 — Tool allowlist, parameter and output security

## 1. Summary

Every tool/enterprise-API/MCP call the AI can make will be constrained by an
**allowlist** (which tools, which endpoints, which methods), **parameter validation +
authorization** (against the propagated authz context, ADR-D6-03) and **output
validation** before results re-enter reasoning — enforced in the Agent Harness
(ADR-D2-09) and guardrail pipeline (ADR-D6-09) (18.PF-FT-AI-GUARDRAILS.md §38–§46; 19.PF-FT-AI-SECURITY.md §53–§60). No
arbitrary URLs, no unvalidated parameters, no unvetted tool output.

## 2. Context and Problem Statement

18.PF-FT-AI-GUARDRAILS.md §38–§41 tool restrictions/authorization/parameter validation, §42–§46 enterprise
API restrictions/endpoint-allowlist/method/payload/response validation; 19.PF-FT-AI-SECURITY.md §53–§56
tool security and §58–§60 arbitrary-URL protection and API request/response security.
An LLM choosing a tool + parameters is an attack surface: it could call an
out-of-scope endpoint, pass a malicious parameter, or ingest a poisoned response. This
ADR fixes tool/API allowlisting and parameter/output security (complementing D3-04's
gate mechanics).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Allowlist tools/endpoints/methods | 18.PF-FT-AI-GUARDRAILS.md §38, §43–§44; 19.PF-FT-AI-SECURITY.md §54 |
| DR-F-02 | Validate + authorize parameters | 18.PF-FT-AI-GUARDRAILS.md §40–§41; 19.PF-FT-AI-SECURITY.md §55 |
| DR-F-03 | Validate tool/API output before use | 18.PF-FT-AI-GUARDRAILS.md §46; 19.PF-FT-AI-SECURITY.md §56, §60 |
| DR-C-01 | No arbitrary URLs | 19.PF-FT-AI-SECURITY.md §58; ADR-D2-19 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Tool set is enumerable/registered | Registry-first tools (ADR-D3-03) | Registry audit |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Prevents out-of-scope/unsafe calls | 30 | Core risk | Boundary tests |
| EC-02 | Parameter safety + authorization | 24 | Injection/escalation | Validation coverage |
| EC-03 | Output safety (no poisoned results) | 20 | Feedback loop | Output validation |
| EC-04 | Enforceability (harness/guardrail) | 14 | Real control | Gate coverage |
| EC-05 | Extensibility (adding tools) | 12 | Growth | Onboarding |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Registry allowlist + parameter validation/authz + output validation, enforced in harness

**Description.** Only registered, allowlisted tools/endpoints/methods callable; each call
validates parameters (schema + semantic, ADR-D3-04 gate 3) and authorizes against context
(ADR-D6-03); responses validated (schema + safety) before re-entering reasoning; no
arbitrary URLs (ADR-D2-19).
**Strengths.** Closes the tool attack surface; authz-consistent; safe feedback.
**Weaknesses.** Registry/validation upkeep.
**Cost / effort.** Medium.

### 5.2 Option B — Allowlist only (no parameter/output validation)

**Description.** Restrict which tools, but trust parameters/outputs.
**Strengths.** Simpler.
**Weaknesses.** Malicious parameters / poisoned outputs still flow.
**Cost / effort.** Low; partial.

### 5.3 Option C — Parameter/output validation but no allowlist (any registered tool)

**Description.** Validate everything but allow any tool.
**Strengths.** Flexible.
**Weaknesses.** Out-of-scope tool/endpoint calls possible; scope creep.
**Cost / effort.** Low-medium; scope risk.

### 5.4 Option D — Model self-restraint (prompt tells model which tools to use)

**Description.** Rely on the prompt to constrain tool use.
**Strengths.** No enforcement code.
**Weaknesses.** Non-deterministic; injection can override; unsafe.
**Cost / effort.** Low; unsafe.

### 5.5 Option E — Allowlist + validation + per-tool rate/quota + anomaly detection

**Description.** Option A plus per-tool rate limits and anomalous-call detection.
**Strengths.** Limits abuse/blast radius; detects misuse.
**Weaknesses.** More config/monitoring.
**Cost / effort.** Medium; strong.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Arbitrary URL/tool invocation | 19.PF-FT-AI-SECURITY.md §58; ADR-D2-19 |
| Trust tool output implicitly | 18.PF-FT-AI-GUARDRAILS.md §46 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 18.PF-FT-AI-GUARDRAILS.md §38–§46 and 19.PF-FT-AI-SECURITY.md §53–§60.

| Criterion | Weight | A: Allowlist+validate | B: Allowlist only | C: Validate only | D: Model self-restraint | E: A+rate/anomaly |
|---|---|---|---|---|---|---|
| EC-01 Out-of-scope prevention | 30 | 5 | 4 | 2 | 1 | 5 |
| EC-02 Parameter safety | 24 | 5 | 2 | 5 | 1 | 5 |
| EC-03 Output safety | 20 | 5 | 2 | 5 | 1 | 5 |
| EC-04 Enforceability | 14 | 5 | 4 | 4 | 1 | 5 |
| EC-05 Extensibility | 12 | 4 | 5 | 4 | 5 | 3 |
| **Weighted total** | **100** | **488** | **312** | **388** | **140** | **484** |

Totals (×20): **A = 488**, **E = 484**, **C = 388**, **B = 312**, **D = 140**.

**Sensitivity.** A and E are near-tied; rate limits + anomaly detection (E) are adopted
for high-impact tools to cap blast radius (RT-01). Allowlist-only (B) and validate-only
(C) each leave half the surface open; model self-restraint (D) is unsafe.

## 7. Decision

**PFF AI will constrain every tool/API/MCP call by a registry allowlist (tools,
endpoints, methods), validate and authorize parameters against the propagated authz
context, and validate outputs before they re-enter reasoning — enforced in the harness
and guardrail pipeline, with no arbitrary URLs (Option A); per-tool rate limits and
anomaly detection are added for high-impact tools (Option E enhancement).** B/C/D are
rejected.

## 8. Architecture Detail

- Harness (ADR-D2-09) enforces the allowlist and runs the tool gates (ADR-D3-04):
  parameter schema + semantic validation (gate 3), authorization (ADR-D6-03), endpoint/
  method allowlist (18.PF-FT-AI-GUARDRAILS.md §43–§44), payload validation (§45).
- Output validation (18.PF-FT-AI-GUARDRAILS.md §46; 19.PF-FT-AI-SECURITY.md §56, §60): tool/API responses validated for
  schema + safety (and treated as untrusted for injection, ADR-D6-08) before reasoning.
- Arbitrary-URL protection (19.PF-FT-AI-SECURITY.md §58): outbound targets restricted (ADR-D6-04) and
  portal links resolved via registry (ADR-D2-19).
- High-impact tools get rate/quota + anomaly monitoring.

## 9. Consequences

### 9.1 Positive
- Tool attack surface closed on input, authz and output; blast radius capped.
### 9.2 Negative
- Registry + validation upkeep as tools grow.
### 9.3 Neutral
- Builds on D3-04 gates and D6-03 context.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Unfettered tool flexibility | Safety + scope control | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Tools execute enterprise ops within allowed scope |
| Precedence chain | Tool output validated, ranked below authoritative sources |
| Four-state separation | Tool results validated before touching state |
| Versioned artefacts | Allowlist/registry versioned |
| Adam persona governs *how*, not *what* | Persona can't invoke out-of-scope tools |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Malicious parameter to a permitted tool | Med | High | H | Semantic param validation (gate 3) | AI Arch Lead | Low |
| RSK-02 | Poisoned tool output re-enters reasoning | Med | High | H | Output validation + injection guard | Security Architect | Low |
| RSK-03 | Out-of-scope endpoint called | Low | High | M | Endpoint/method allowlist | Security Architect | Low |
| RSK-04 | Tool abuse (volume) | Low | Med | M | Rate/quota + anomaly (E) | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Out-of-scope tool/endpoint calls | 0 | > 0 | Boundary tests | Continuous |
| QM-02 | Unvalidated parameters/outputs | 0 | > 0 | Gate audit | Per release |
| QM-03 | Arbitrary-URL calls | 0 | > 0 | Egress/tests | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Closes the tool-calling surface |
| Data classification touched | Tool payloads (per classification) |
| Personal data / PII | Parameter/output validation limits leakage |
| Children's data and safeguarding | Scoped tools protect safeguarding actions |
| UK GDPR lawful basis and rights impact | Controlled data access |
| Audit and evidential requirements | Tool calls + validations logged |
| Standards touched | ISO/IEC 27001, 42001, OWASP LLM |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 9 |
| Repository paths | `src/pf_ft_ai/harness/`, guardrails |
| Configuration | Allowlist; validation rules; rate/quota |
| Contracts / schemas | Tool schemas; validation policy |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-04, D2-09, D6-03, D6-09 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Only allowlisted tools/endpoints/methods callable | Boundary test |
| AC-02 | Parameters validated + authorized | Gate test |
| AC-03 | Outputs validated before reasoning | Test |
| AC-04 | No arbitrary URLs | Egress/portal test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Tool-call metrics; validation failures; anomalies |
| Alerting | Out-of-scope attempts; abuse |
| Runbook | `docs/runbooks/tools.md` |
| Failure mode and degradation | Invalid call/output → block (fail closed) |
| Rollback | Allowlist/config revert |
| Support model impact | Security + AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Validation + allowlist + monitoring | M | small | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | High-impact tool abuse risk | Risk review | Add/tighten rate + anomaly (E) |
| RT-02 | Tool-security incident | Incident | CAR; tighten allowlist/validation |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | 18.PF-FT-AI-GUARDRAILS.md §38–§46; 19.PF-FT-AI-SECURITY.md §53–§60 |
| Requirement IDs | SEC-TOOL-* |
| Build phases | 9 |
| Code paths | `src/pf_ft_ai/harness/` |
| Configuration | allowlist/validation |
| Tests | tool security suites |
| Upstream ADRs | ADR-D3-04, D2-09, D6-03 |
| Downstream ADRs | ADR-D6-11 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
