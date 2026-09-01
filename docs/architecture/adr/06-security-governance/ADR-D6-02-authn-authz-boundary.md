---
id: ADR-D6-02
title: AuthN/AuthZ boundary — APIM validates, AI consumes claims only
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [Principal Architect, AI Architecture Lead]
reviewers: [Platform Engineer]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-15, ADR-D6-03, ADR-D6-01, ADR-D1-02, ADR-D3-04]
source_docs:
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §10, §11, §12, §16, §17"
  - "MD files/4 AI/18.PF-FT-AI-GUARDRAILS.md §33, §34, §35, §60"
build_phases: [2]
impacted_paths:
  - src/pf_ft_ai/api/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-02 — AuthN/AuthZ boundary — APIM validates, AI consumes claims only

## 1. Summary

Authentication and the *validation* of authorization are performed at the APIM/
enterprise boundary; the AI platform **consumes already-validated authorization claims
and never authenticates a request, mints authority, or lets a model output become an
authorization decision** (19.PF-FT-AI-SECURITY.md §10–§12, §16–§17; 18.PF-FT-AI-GUARDRAILS.md §33–§35, §60; CLAUDE.md
Golden Rule). Authorization decisions that gate actions remain deterministic and
enterprise-owned.

## 2. Context and Problem Statement

19.PF-FT-AI-SECURITY.md §10–§12 define authentication, authorization and authorization context;
§16–§17 the APIM boundary and AI responsibilities; 18.PF-FT-AI-GUARDRAILS.md §33–§35 the authorization
boundary and that authorization context cannot be user-controlled, §60 that decision
authority is not the model's. CLAUDE.md forbids the AI authenticating/authorizing or
letting a model output become an authorization decision. Blurring this is the most
dangerous Golden-Rule violation — an LLM "deciding" someone is authorized. This ADR
fixes the boundary.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | AI consumes validated claims; never authenticates | CLAUDE.md; 19.PF-FT-AI-SECURITY.md §16–§17 |
| DR-C-02 | Model output is never an authz decision | 18.PF-FT-AI-GUARDRAILS.md §60; CLAUDE.md |
| DR-C-03 | Authz context not user-controllable | 18.PF-FT-AI-GUARDRAILS.md §35 |
| DR-F-01 | Deterministic authz enforcement | 19.PF-FT-AI-SECURITY.md §11 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Enterprise/APIM issues trustworthy validated claims | Strengthen validation | Identity review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Golden-Rule fidelity (no AI authz) | 34 | Highest-risk violation | Boundary tests |
| EC-02 | Determinism of enforcement | 22 | Reproducible, provable | Deterministic checks |
| EC-03 | Tamper-resistance of claims | 20 | Not user-controllable | Integrity checks |
| EC-04 | Simplicity/clarity | 12 | Team understands | Boundary clarity |
| EC-05 | Performance | 12 | Per-request | Overhead |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — APIM validates; AI consumes claims; deterministic enforcement; model never decides authz

**Description.** APIM authenticates + validates tokens/claims; the AI reads validated
claims (ADR-D6-03) and enforces action-gating deterministically against enterprise
authorization; the model never gates an action.
**Strengths.** Golden-Rule-faithful; deterministic; tamper-resistant.
**Weaknesses.** Requires discipline to keep authz out of model paths.
**Cost / effort.** Low-medium.

### 5.2 Option B — AI performs authentication/authorization

**Description.** AI validates tokens and decides authorization.
**Strengths.** Fewer moving parts.
**Weaknesses.** Direct Golden-Rule violation; security risk; unacceptable.
**Cost / effort.** Low; forbidden.

### 5.3 Option C — Model-assisted authorization (LLM helps decide access)

**Description.** Use the model to interpret access rules.
**Strengths.** Handles fuzzy policies.
**Weaknesses.** Non-deterministic authz; model output as decision (18.PF-FT-AI-GUARDRAILS.md §60
violation); catastrophic if wrong.
**Cost / effort.** Low; forbidden.

### 5.4 Option D — Enterprise services enforce authz on every call; AI passes claims through

**Description.** AI never evaluates authz at all; every gated action calls an enterprise
API that enforces authorization itself.
**Strengths.** Strongest — enterprise is the sole decider.
**Weaknesses.** Requires enterprise APIs to enforce on all actions; AI still needs
claims to route/clarify. Complementary to A rather than distinct.
**Cost / effort.** Depends on enterprise APIs.

### 5.5 Option E — Dedicated policy engine (e.g. OPA) evaluating claims deterministically

**Description.** A policy engine evaluates validated claims against declarative policy
for AI-side gating.
**Strengths.** Deterministic, auditable, externalised policy.
**Weaknesses.** Another component; must still not override enterprise authority; useful
where AI-side gating is complex.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Trust user-supplied authz context | 18.PF-FT-AI-GUARDRAILS.md §35 |
| Cache authz decisions long-term | Staleness/precedence risk |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 19.PF-FT-AI-SECURITY.md §10–§17, 18.PF-FT-AI-GUARDRAILS.md §33–§35/§60
and CLAUDE.md.

| Criterion | Weight | A: APIM+claims+deterministic | B: AI authNs/Zs | C: Model-assisted | D: Enterprise enforces all | E: Policy engine |
|---|---|---|---|---|---|---|
| EC-01 Golden-Rule fidelity | 34 | 5 | 1 | 1 | 5 | 5 |
| EC-02 Determinism | 22 | 5 | 3 | 1 | 5 | 5 |
| EC-03 Tamper-resistance | 20 | 5 | 3 | 2 | 5 | 5 |
| EC-04 Simplicity | 12 | 4 | 4 | 3 | 3 | 3 |
| EC-05 Performance | 12 | 4 | 4 | 3 | 3 | 4 |
| **Weighted total** | **100** | **476** | **256** | **156** | **452** | **472** |

Totals (×20): **A = 476**, **E = 472**, **D = 452**, **B = 256**, **C = 156**.

**Sensitivity.** A and E are essentially tied; D is complementary (enterprise enforcing
on gated actions is the ideal end-state where APIs support it). A is chosen as the base;
a policy engine (E) may externalise complex AI-side gating later (RT-01); enterprise
enforcement (D) is preferred wherever the API provides it. B and C are forbidden.

## 7. Decision

**APIM/enterprise authenticates and validates authorization; the AI platform consumes
validated claims and enforces any AI-side action-gating deterministically, never
authenticating, minting authority, or letting a model output become an authorization
decision (Option A).** Where an enterprise API enforces authorization on a gated action
(D), that is preferred and the AI relies on it. A declarative policy engine (E) may be
introduced for complex deterministic gating. Options B and C are forbidden.

**Status rationale.** `Accepted` — CLAUDE.md and 19.PF-FT-AI-SECURITY.md / 18.PF-FT-AI-GUARDRAILS.md mandate this.

## 8. Architecture Detail

- APIM validates JWT/claims (ADR-D5-15); the AI reads a validated authorization context
  (ADR-D6-03) that is not user-controllable (18.PF-FT-AI-GUARDRAILS.md §35).
- Any AI-side gate is deterministic code checking claims; the model may *explain* an
  authorization outcome but never *make* it (18.PF-FT-AI-GUARDRAILS.md §60); tool calls are gated by the
  harness (ADR-D3-04) against claims, not model whim.
- Gated business actions call enterprise APIs that enforce authorization (D) where
  available.

## 9. Consequences

### 9.1 Positive
- Eliminates the highest-risk Golden-Rule violation; deterministic, provable authz.
### 9.2 Negative
- Discipline needed to keep authz out of model paths (enforced by tests).
### 9.3 Neutral
- Sets up authz context integrity (D6-03).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| "Smart" model-driven access | Determinism + safety | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | This ADR *is* that rule for authorization |
| Precedence chain | Claims are authoritative input, above model output |
| Four-state separation | Claims context is a distinct, protected input |
| Versioned artefacts | Policy (if any) versioned |
| Adam persona governs *how*, not *what* | Persona may explain access, never grant it |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Model output used as authz | Low | Critical | H | Deterministic gates + tests (§60) | Security Architect | Low |
| RSK-02 | User-forged authz context | Low | High | M | Server-side validated claims only (§35) | Security Architect | Low |
| RSK-03 | Authz logic leaks into model prompt | Med | High | M | Boundary review; guardrail | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Model-made authz decisions | 0 | > 0 | Security tests | Continuous |
| QM-02 | Requests enforced against validated claims | 100% | < 100% | Audit | Per release |
| QM-03 | User-controllable authz context | 0 | > 0 | Security tests | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Removes model as an authz vector |
| Data classification touched | Claims (Personal identifiers) |
| Personal data / PII | Minimal validated claims only |
| Children's data and safeguarding | Access to safeguarding data authoritatively gated |
| UK GDPR lawful basis and rights impact | Access control integrity |
| Audit and evidential requirements | Authz decisions traceable to enterprise/claims |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 2 |
| Repository paths | `src/pf_ft_ai/api/`, harness |
| Configuration | Claims mapping; (optional) policy |
| Contracts / schemas | Authorization context (ADR-D6-03) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-15, D6-03, D3-04 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | AI performs no authentication | Code audit |
| AC-02 | No model output gates an action | Security test |
| AC-03 | Authz context server-validated, immutable | Test (§35) |
| AC-04 | Gated actions enforce claims/enterprise authz | Integration test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Authz decision logs; denials |
| Alerting | Authz anomalies; forged-context attempts |
| Runbook | `docs/runbooks/authz.md` |
| Failure mode and degradation | Missing/invalid claims → deny (fail closed) |
| Rollback | Policy revert |
| Support model impact | Security team |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Enforcement + (opt) policy engine | M | low | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | AI-side gating grows complex | Design review | Introduce policy engine (Option E) |
| RT-02 | Any model-authz incident | Incident | CAR; remove the path |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | 19.PF-FT-AI-SECURITY.md §10–§12, §16–§17; 18.PF-FT-AI-GUARDRAILS.md §33–§35, §60 |
| Requirement IDs | SEC-AUTHZ-* |
| Build phases | 2 |
| Code paths | `src/pf_ft_ai/api/`, harness |
| Configuration | claims mapping |
| Tests | authz boundary suites |
| Upstream ADRs | ADR-D5-15, D1-02 |
| Downstream ADRs | ADR-D6-03, D3-04 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
