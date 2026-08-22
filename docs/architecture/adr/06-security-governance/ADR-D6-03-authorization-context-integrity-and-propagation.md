---
id: ADR-D6-03
title: Authorization context integrity and propagation through the graph
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
related_adrs: [ADR-D6-02, ADR-D2-07, ADR-D3-04, ADR-D6-12, ADR-D2-09]
source_docs:
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §12, §13, §14, §15"
  - "MD files/4 AI/18.PF-FT-AI-GUARDRAILS.md §34, §35, §36, §37"
build_phases: [3]
impacted_paths:
  - src/pf_ft_ai/orchestration/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-03 — Authorization context integrity and propagation through the graph

## 1. Summary

The validated **authorization context** (identity + claims from APIM, ADR-D6-02) will
be carried as **immutable, server-owned state propagated through every LangGraph node,
tool call and ERC/RAG access** — never re-derived from user input, never mutated by the
model, and checked at each enforcement point (doc 19 §12–§15; doc 18 §34–§37). Tools
and retrieval receive the same authorization context so access is consistent end-to-end.

## 2. Context and Problem Statement

Doc 19 §12–§15 define authorization context, its integrity, propagation and boundary;
doc 18 §34–§37 authorization-context enforcement, that it cannot be user-controlled, its
propagation and the authorization-context guardrail. In a multi-node agent graph, the
authorization context must reach every node/tool/retrieval unchanged; if a node could
alter it or a tool ran without it, privilege escalation or cross-tenant access follows.
This ADR fixes integrity + propagation.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | Authz context immutable + server-owned | doc 18 §35; doc 19 §13 |
| DR-F-01 | Propagate to every node/tool/retrieval | doc 19 §14; doc 18 §36 |
| DR-F-02 | Enforced at each access (tool/ERC/RAG) | doc 18 §37; ADR-D3-04, D6-12 |
| DR-C-02 | Never re-derived from user input | doc 18 §35 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Graph state can carry an immutable context safely | Out-of-band context store | Design review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Integrity (immutable, tamper-proof) | 30 | No escalation | Mutation tests |
| EC-02 | Complete propagation | 24 | No unauthenticated hop | Coverage |
| EC-03 | Consistent enforcement points | 20 | Tool/ERC/RAG uniform | Enforcement audit |
| EC-04 | Simplicity | 14 | Maintainable | Concepts |
| EC-05 | Performance | 12 | Per-node overhead | Overhead |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Immutable authz context in graph state, propagated + enforced at each access

**Description.** Context injected once (from validated claims), stored immutably in
graph state (ADR-D2-07), read by every node/tool/retrieval; enforcement at tool gate
(ADR-D3-04) and RAG ACL (ADR-D6-12); an authorization-context guardrail (doc 18 §37)
verifies presence/integrity.
**Strengths.** Tamper-proof; complete; consistent.
**Weaknesses.** Must thread context everywhere (framework support helps).
**Cost / effort.** Low-medium.

### 5.2 Option B — Re-fetch/re-derive context per node

**Description.** Each node re-derives authz from request/user input.
**Strengths.** Always "fresh".
**Weaknesses.** Re-derivation from user input is forbidden (§35); inconsistency;
escalation risk.
**Cost / effort.** Low; unsafe.

### 5.3 Option C — Context in a mutable shared object

**Description.** Shared context nodes can update.
**Strengths.** Flexible.
**Weaknesses.** Mutable → a node/model could weaken it; violates §35.
**Cost / effort.** Low; unsafe.

### 5.4 Option D — Out-of-band context store keyed by request id

**Description.** Context in a side store, fetched by id per access.
**Strengths.** Not carried in prompt/state; central.
**Weaknesses.** Extra fetch per access; store becomes critical dependency; still needs
immutability. A viable variant of A.
**Cost / effort.** Medium.

### 5.5 Option E — Signed context token passed with each call

**Description.** A signed token (claims) verified at each enforcement point.
**Strengths.** Cryptographic tamper-evidence; stateless propagation.
**Weaknesses.** Signing/verification overhead; key management; essentially A with
crypto — good for cross-service hops.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Context in the LLM prompt as text | Model could alter/leak it (§35) |
| Trust first-node context downstream without checks | No per-access enforcement |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 19 §12–§15 and doc 18 §34–§37.

| Criterion | Weight | A: Immutable in state | B: Re-derive | C: Mutable shared | D: Out-of-band store | E: Signed token |
|---|---|---|---|---|---|---|
| EC-01 Integrity | 30 | 5 | 2 | 1 | 4 | 5 |
| EC-02 Propagation | 24 | 5 | 3 | 4 | 4 | 5 |
| EC-03 Enforcement consistency | 20 | 5 | 3 | 3 | 4 | 5 |
| EC-04 Simplicity | 14 | 4 | 3 | 4 | 3 | 3 |
| EC-05 Performance | 12 | 5 | 3 | 4 | 3 | 3 |
| **Weighted total** | **100** | **488** | **276** | **288** | **376** | **452** |

Totals (×20): **A = 488**, **E = 452**, **D = 376**, **C = 288**, **B = 276**.

**Sensitivity.** A leads; signed tokens (E) add cryptographic tamper-evidence valuable
for cross-service hops and can layer onto A (RT-01). Out-of-band (D) is a viable variant
where state-carrying is undesirable. Re-derivation (B) and mutable context (C) are
forbidden by §35.

## 7. Decision

**PFF AI will carry the validated authorization context as immutable, server-owned
graph state, propagate it to every node, tool call and ERC/RAG access, and enforce it at
each access, with an authorization-context guardrail verifying its presence and
integrity (Option A).** Signed context tokens (E) may be layered for cross-service hops.
Re-derivation from user input (B) and mutable context (C) are forbidden.

**Status rationale.** `Accepted` — doc 19 §12–§15 and doc 18 §34–§37 mandate this.

## 8. Architecture Detail

- Authorization context (from ADR-D6-02) injected once at graph entry into an immutable
  field of TypedDict state (ADR-D2-07); nodes read, never write it.
- Enforcement: the harness (ADR-D2-09) passes context to every tool and gates on it
  (ADR-D3-04); RAG retrieval filters by it (ADR-D6-12); ERC access respects it.
- The authorization-context guardrail (doc 18 §37) fails closed if context is missing,
  altered, or user-sourced.

## 9. Consequences

### 9.1 Positive
- Consistent, tamper-proof authorization end-to-end across the agent graph.
### 9.2 Negative
- Context must be threaded through all access paths.
### 9.3 Neutral
- Ties tool gate (D3-04) and RAG ACL (D6-12) to one context.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Flexibility of mutable context | Integrity + consistency | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Enforces enterprise-validated authorization uniformly |
| Precedence chain | Authz context is authoritative input, never model-derived |
| Four-state separation | Authz context is a protected, immutable part of state |
| Versioned artefacts | Enforcement config versioned |
| Adam persona governs *how*, not *what* | Persona cannot alter authorization |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | A node mutates/weakens context | Low | Critical | H | Immutable field + guardrail (§37) | Security Architect | Low |
| RSK-02 | Tool runs without context | Low | High | M | Harness injects context; gate refuses without it | AI Arch Lead | Low |
| RSK-03 | Context leaked into prompt text | Med | High | M | Keep in state, not prompt; redaction | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Accesses with valid authz context | 100% | < 100% | Enforcement audit | Continuous |
| QM-02 | Context mutation attempts blocked | 100% | < 100% | Security tests | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Removes escalation paths in the graph |
| Data classification touched | Claims (Personal) |
| Personal data / PII | Minimal claims; not in prompt |
| Children's data and safeguarding | Consistent gating of safeguarding access |
| UK GDPR lawful basis and rights impact | Access-control integrity |
| Audit and evidential requirements | Per-access authz logged |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 3 |
| Repository paths | `src/pf_ft_ai/orchestration/` |
| Configuration | Enforcement points |
| Contracts / schemas | Immutable authz-context type |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D6-02, D2-07, D3-04, D6-12 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Context immutable in state | Unit test |
| AC-02 | Every tool/ERC/RAG access carries context | Enforcement audit |
| AC-03 | Guardrail fails closed if context missing/altered | Test (§37) |
| AC-04 | Context never sourced from user input | Security test (§35) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Enforcement coverage; guardrail hits |
| Alerting | Missing/altered context |
| Runbook | `docs/runbooks/authz.md` |
| Failure mode and degradation | No valid context → deny (fail closed) |
| Rollback | Config revert |
| Support model impact | Security team |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Propagation + guardrail | M | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Cross-service hops need crypto tamper-evidence | Architecture | Add signed context tokens (E) |
| RT-02 | Escalation incident | Incident | CAR; tighten enforcement |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | doc 19 §12–§15; doc 18 §34–§37 |
| Requirement IDs | SEC-CTX-* |
| Build phases | 3 |
| Code paths | `src/pf_ft_ai/orchestration/` |
| Configuration | enforcement points |
| Tests | context integrity suites |
| Upstream ADRs | ADR-D6-02, D2-07 |
| Downstream ADRs | ADR-D3-04, D6-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
