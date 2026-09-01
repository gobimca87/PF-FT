---
id: ADR-D5-15
title: API gateway and authorization boundary — APIM
domain: 5 Technology
ws_ref: [WS-25]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [Platform Engineer, Principal Architect]
reviewers: [AI Architecture Lead]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D6-02, ADR-D6-01, ADR-D5-08, ADR-D2-04, ADR-D4-09]
source_docs:
  - "MD files/6 Production/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §6, §7, §64"
  - "MD files/6 Production/27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §5"
build_phases: [2]
impacted_paths:
  - infra/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-15 — API gateway and authorization boundary — APIM

## 1. Summary

PFF AI will front its API with **Azure API Management (APIM)** as the edge gateway and
**authorization boundary**: APIM authenticates and authorizes requests (validating
tokens/claims), applies rate limiting and edge policies, and the AI platform
**consumes already-validated claims** rather than performing authentication itself
(CLAUDE.md Golden Rule; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §6–§7). The AI never authenticates or authorizes a
request on its own.

## 2. Context and Problem Statement

25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §6–§7 define the edge layer and API gateway; §64 rate limits; 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §5 the AI
platform boundary; CLAUDE.md states the AI "never authenticates or authorizes a
request itself (APIM/enterprise auth does that — AI only consumes validated claims)."
Without a designated gateway/authz boundary, the AI would be tempted to re-implement
auth (a Golden-Rule violation and a security risk). This ADR fixes APIM as the gateway
and authz boundary.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | AI consumes validated claims; never authenticates | CLAUDE.md; 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §5 |
| DR-F-01 | Edge gateway: routing, rate limit, policy | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §6–§7, §64 |
| DR-F-02 | Token/claim validation at the edge | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §7; ADR-D6-02 |
| DR-N-01 | Azure-native, private, observable | ADR-D5-08 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Enterprise identity provider issues tokens APIM can validate | Adapt policy | Identity review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | AuthN/Z boundary fidelity (AI consumes claims) | 30 | Golden Rule | Boundary tests |
| EC-02 | Edge policy (rate limit, transform, routing) | 20 | Protection/control | Policy features |
| EC-03 | Azure-native + enterprise integration | 20 | Tenancy/identity | Native fit |
| EC-04 | Observability | 14 | Tracing/metrics | Integration |
| EC-05 | Cost/ops | 16 | Run it | £/ops |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Azure API Management (APIM)

**Description.** APIM as edge gateway + authz boundary; validates JWT/claims, rate
limits, transforms, routes to the FastAPI backend; AI consumes claims.
**Strengths.** Azure-native; rich policy; enterprise identity integration; matches
CLAUDE.md/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md.
**Weaknesses.** Cost at higher tiers; APIM policy learning curve.
**Cost / effort.** Medium; strong fit.

### 5.2 Option B — Azure Application Gateway + WAF only

**Description.** App Gateway/WAF as edge.
**Strengths.** L7 routing + WAF.
**Weaknesses.** Not a full API-management/authz-policy layer; would push authz into the
app (Golden-Rule risk).
**Cost / effort.** Medium; insufficient authz boundary.

### 5.3 Option C — In-app auth (FastAPI middleware) behind a plain LB

**Description.** App validates tokens itself.
**Strengths.** Simple; no gateway product.
**Weaknesses.** AI performing authz violates CLAUDE.md/27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §5; scatters security;
no central rate limit/policy.
**Cost / effort.** Low; wrong boundary.

### 5.4 Option D — Third-party API gateway (e.g. Kong/Apigee)

**Description.** Non-Azure gateway.
**Strengths.** Feature-rich.
**Weaknesses.** Off Azure-native path; extra vendor; weaker Entra integration.
**Cost / effort.** Medium; misaligned.

### 5.5 Option E — NGINX/ingress + external authz service

**Description.** Ingress with an auth sidecar/service.
**Strengths.** Flexible; K8s-native.
**Weaknesses.** Build/run bespoke authz + policy that APIM provides managed; more ops.
**Cost / effort.** High ops.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No gateway (direct to app) | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §6–§7; no edge protection |
| AI issues/validates its own tokens | CLAUDE.md Golden Rule |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §6–§7/§64, 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §5 and
CLAUDE.md.

| Criterion | Weight | A: APIM | B: AppGW+WAF | C: In-app auth | D: Kong/Apigee | E: NGINX+authz |
|---|---|---|---|---|---|---|
| EC-01 AuthN/Z boundary | 30 | 5 | 3 | 1 | 4 | 3 |
| EC-02 Edge policy | 20 | 5 | 3 | 2 | 5 | 3 |
| EC-03 Azure-native | 20 | 5 | 5 | 3 | 2 | 3 |
| EC-04 Observability | 14 | 4 | 4 | 3 | 4 | 3 |
| EC-05 Cost/ops | 16 | 3 | 4 | 5 | 3 | 2 |
| **Weighted total** | **100** | **454** | **376** | **266** | **362** | **288** |

Totals (×20): **A = 454**, **B = 376**, **D = 362**, **E = 288**, **C = 266**.

**Sensitivity.** APIM leads by 78; it is the only option that cleanly provides a managed
authz boundary the AI consumes from. C is rejected outright as a Golden-Rule violation.
App Gateway/WAF (B) can sit *in front of* APIM for WAF, but does not replace it.

## 7. Decision

**PFF AI will use Azure API Management (APIM) as the edge gateway and authorization
boundary; APIM authenticates/authorizes requests and the AI platform consumes
validated claims only (Option A).** Application Gateway/WAF may front APIM for WAF.
In-app auth (C) is forbidden by the Golden Rule; non-Azure gateways (D) and bespoke
NGINX authz (E) are rejected.

**Status rationale.** `Accepted` — CLAUDE.md and 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §6–§7 mandate this.

## 8. Architecture Detail

- APIM validates JWT/claims from the enterprise IdP (ADR-D6-02), applies rate limits
  (§64), transforms, and routes to the FastAPI backend over private networking
  (ADR-D6-04).
- The AI reads authorization context from validated claims (ADR-D6-03) and never
  re-authenticates; the Conversation Manager (ADR-D2-04) receives claims context
  (6 PFF-FA-AI-CONVERSATION-SESSION.md §36).
- Standard error envelope (ADR-D4-09) preserved through APIM policies.

## 9. Consequences

### 9.1 Positive
- Central, managed authz boundary honouring the Golden Rule; edge protection.
### 9.2 Negative
- APIM cost/policy learning curve.
### 9.3 Neutral
- Anchors security ADRs (D6-01/02/03).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of in-app auth | Correct authz boundary + edge policy | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | APIM/enterprise auth decides; AI consumes claims only |
| Precedence chain | Claims are authoritative input, not AI-derived |
| Four-state separation | Claims context distinct from other state |
| Versioned artefacts | APIM policies versioned in IaC |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | AI code re-implements authz | Low | High | M | Boundary tests; code review (27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §5) | Security Architect | Low |
| RSK-02 | APIM misconfig bypasses validation | Low | High | M | Policy tests; least-privilege backend | Security Architect | Low |
| RSK-03 | APIM cost at scale | Med | Med | M | Tier right-sizing | FinOps | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Requests reaching backend unvalidated | 0 | > 0 | Security tests | Continuous |
| QM-02 | AI-side auth logic instances | 0 | > 0 | Code audit | Per release |
| QM-03 | Rate-limit policy coverage | 100% | < 100% | APIM config | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Central edge validation + WAF option |
| Data classification touched | Claims (Personal identifiers) validated at edge |
| Personal data / PII | AI receives only necessary validated claims |
| Children's data and safeguarding | Access decisions at authoritative boundary |
| UK GDPR lawful basis and rights impact | Access control supports lawful processing |
| Audit and evidential requirements | APIM request logs |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 2 |
| Repository paths | `infra/` (APIM policies) |
| Configuration | APIM policies; rate limits |
| Contracts / schemas | Claims contract (ADR-D6-03) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D6-02, D6-03, D5-08 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No unvalidated request reaches backend | Security test |
| AC-02 | AI performs no authentication | Code audit |
| AC-03 | Rate limiting enforced | Load test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | APIM metrics; auth failures; rate-limit hits |
| Alerting | Auth-bypass attempts; error spikes |
| Runbook | `docs/runbooks/apim.md` |
| Failure mode and degradation | APIM down → no unauthenticated access (fail closed) |
| Rollback | Policy version revert |
| Support model impact | Security + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| APIM | setup | tier-based | Azure APIM pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | APIM cost/features misfit | FinOps/ops | Re-evaluate tier / topology |
| RT-02 | Auth-bypass incident | Incident | CAR; tighten policies |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-25 Security/Gateway |
| Specification sections | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §6–§7, §64; 27.PFF-FA-AI-DEVELOPMENT-STANDARDS.md §5 |
| Requirement IDs | GW-* |
| Build phases | 2 |
| Code paths | `infra/` |
| Configuration | APIM policies |
| Tests | authz boundary tests |
| Upstream ADRs | ADR-D5-08 |
| Downstream ADRs | ADR-D6-02, D6-03 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
