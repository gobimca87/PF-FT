---
id: ADR-D8-09
title: Multi-county / multi-tenant extensibility strategy
domain: 8 Business Value
ws_ref: [WS-37]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [AI Architecture Lead, Security Architect, Product Owner]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-01, ADR-D6-12, ADR-D4-10, ADR-D1-07, ADR-D8-08]
source_docs:
  - "MD files/3 Context & Integration/9 PF-FT-AI-MEMORY-CACHE.md §77, §78"
  - "MD files/4 AI/13.FP-FT-AI-RAG.md §36, §37, §152, §153"
  - "MD files/4 AI/14.PF-FT-AI-EMBEDDING-VECTOR.md §47, §48"
build_phases: [23]
impacted_paths:
  - src/pf_ft_ai/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D8-09 — Multi-county / multi-tenant extensibility strategy

## 1. Summary

PFF AI will support multiple CFAs (County Football Associations) as **logical tenants on
shared infrastructure with strict per-tenant isolation** — tenant-scoped keys/namespaces
(memory/cache/session, ADR-D4-10), tenant-filtered RAG (ADR-D6-12), tenant in the
authorization context (ADR-D6-03), and per-tenant configuration overlays — rather than a
separate deployment per county (doc 9 §77–§78; doc 13 §36–§37, §152–§153; doc 14 §47–§48).
Isolation is enforced, not assumed.

## 2. Context and Problem Statement

Doc 9 §77–§78 cross-user/cross-club isolation; doc 13 §36–§37 tenant/org filtering, §152–§153
multi-tenant RAG/tenant-isolation principle; doc 14 §47–§48 index partitioning/multi-tenant
vector architecture. The FA has many county associations; the platform must serve them without
data leakage between counties and without a costly deployment per county. This ADR fixes the
multi-tenant model.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | Strict per-tenant isolation (no leakage) | doc 9 §77–§78; doc 13 §153 |
| DR-F-01 | Tenant in authz context + filters | ADR-D6-03/D6-12 |
| DR-F-02 | Per-tenant config overlays | ADR-D5-06 |
| DR-N-01 | Cost-efficient (shared infra) | FinOps |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Counties can share infra with logical isolation | Isolated deploys for some | Security review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Isolation strength (no cross-tenant leak) | 34 | Confidentiality | Isolation tests |
| EC-02 | Cost efficiency | 20 | Many counties | £/tenant |
| EC-03 | Operability (add a county) | 18 | Growth | Onboarding effort |
| EC-04 | Per-tenant customisation | 16 | County differences | Config overlays |
| EC-05 | Performance (no noisy-neighbour) | 12 | Fairness | Isolation/QoS |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Shared infra + logical isolation (tenant-scoped keys/filters/authz/config)

**Description.** One deployment; tenant id in the authz context (ADR-D6-03); tenant-scoped
namespaces for memory/cache/session (doc 9 §77–§78; ADR-D4-10); tenant-filtered RAG (doc 13
§36–§37; ADR-D6-12); shared or partitioned index (doc 14 §47–§48); per-tenant config overlays
(ADR-D5-06).
**Strengths.** Strong logical isolation, cost-efficient, easy to add counties.
**Weaknesses.** Isolation must be rigorously enforced/tested.
**Cost / effort.** Low-medium.

### 5.2 Option B — Separate deployment per county

**Description.** Full stack per CFA.
**Strengths.** Hard physical isolation.
**Weaknesses.** High cost/ops per county; slow to add; wasteful at FA scale.
**Cost / effort.** High.

### 5.3 Option C — Shared infra, no tenant model (single pool)

**Description.** Treat all counties as one dataset.
**Strengths.** Simplest.
**Weaknesses.** Cross-county data leakage; unacceptable.
**Cost / effort.** Low; unsafe.

### 5.4 Option D — Hybrid: shared infra + isolated index/store per tenant

**Description.** Shared compute, but per-tenant vector index/data store.
**Strengths.** Stronger data isolation than shared index.
**Weaknesses.** Index/store sprawl; higher cost; useful for the most sensitive data only.
**Cost / effort.** Medium.

### 5.5 Option E — Shared infra + logical isolation + per-tenant isolation for sensitive data + isolation test suite

**Description.** Option A with per-tenant isolated store/index only for the most sensitive
data (e.g. safeguarding) (doc 14 §48 hybrid) and a mandatory cross-tenant isolation test
suite in CI.
**Strengths.** A's efficiency + stronger isolation where it matters + proven isolation.
**Weaknesses.** Mixed isolation model.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No tenant isolation | doc 13 §153 |
| Tenant id from user input (spoofable) | ADR-D6-03 (server-owned) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 9 §77–§78, doc 13 §36–§37/§152–§153,
doc 14 §47–§48.

| Criterion | Weight | A: Shared+logical | B: Deploy-per-county | C: No tenant model | D: Shared+isolated store | E: A+sensitive-isolation+tests |
|---|---|---|---|---|---|---|
| EC-01 Isolation | 34 | 4 | 5 | 1 | 5 | 5 |
| EC-02 Cost | 20 | 5 | 1 | 5 | 3 | 4 |
| EC-03 Operability | 18 | 5 | 2 | 5 | 3 | 4 |
| EC-04 Customisation | 16 | 4 | 5 | 2 | 4 | 4 |
| EC-05 Performance | 12 | 4 | 5 | 3 | 4 | 4 |
| **Weighted total** | **100** | **436** | **352** | **296** | **404** | **452** |

Totals (×20): **E = 452**, **A = 436**, **D = 404**, **B = 352**, **C = 296**.

**Sensitivity.** E (shared + logical isolation + per-tenant isolation for the most sensitive
data + mandatory isolation test suite) edges A by hardening isolation exactly where the
consequence is highest (safeguarding), and proving isolation in CI. Deploy-per-county (B) is
too costly; no-tenant-model (C) is unsafe.

## 7. Decision

**PFF AI will serve multiple CFAs as logical tenants on shared infrastructure with strict
enforced isolation — tenant in the server-owned authz context, tenant-scoped keys/namespaces,
tenant-filtered RAG, per-tenant config overlays — with per-tenant isolated store/index for the
most sensitive data (e.g. safeguarding) and a mandatory cross-tenant isolation test suite in
CI (Option E).** Deployment-per-county (B), no-tenant-model (C) and blanket isolated-store (D)
are rejected.

## 8. Architecture Detail

- Tenant id derived from validated claims (ADR-D6-03), never user input; tenant-scoped keys
  for memory/cache/session (doc 9 §77–§78; ADR-D4-10); RAG metadata filter includes tenant
  (doc 13 §36; ADR-D6-12); shared or partitioned index (doc 14 §47), with an isolated index/
  store for safeguarding-grade data (§48; ADR-D6-16).
- Per-tenant config overlays (ADR-D5-06) for county differences (personas remain shared,
  ADR-D3-10); onboarding a county = config + registration, no core change (ADR-D8-08); a CI
  isolation test suite (doc 22 §56) proves no cross-tenant access.

## 9. Consequences

### 9.1 Positive
- Cost-efficient multi-county scaling with enforced, tested isolation.
### 9.2 Negative
- Rigorous isolation testing; mixed isolation model for sensitive data.
### 9.3 Neutral
- Builds on isolation (D6-12), store (D4-10), extensibility (D8-08).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Physical isolation of deploy-per-county | Cost efficiency + tested logical isolation | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Tenant scope from validated claims, not the model |
| Precedence chain | Tenant-scoped ERC/RAG respect precedence |
| Four-state separation | Tenant scoping applied within each state class |
| Versioned artefacts | Per-tenant overlays versioned |
| Adam persona governs *how*, not *what* | Shared persona; tenant affects data, not persona |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Cross-tenant data leak | Low | Critical | H | Tenant in authz + scoped keys/filters + CI isolation tests | Security Architect | Low |
| RSK-02 | Noisy neighbour | Low | Med | M | Fair scheduling/QoS; autoscaling (ADR-D5-17) | SRE | Low |
| RSK-03 | Tenant id spoofed | Low | High | M | Server-owned claims only (ADR-D6-03) | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Cross-tenant leaks | 0 | > 0 | Isolation tests | Continuous |
| QM-02 | Cost per tenant | ≤ target | rising | FinOps | Monthly |
| QM-03 | County onboarding effort | ≤ target | rising | Delivery | Per county |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Multi-tenant boundary; enforced isolation |
| Data classification touched | Per-tenant data incl. Personal/special-category |
| Personal data / PII | Tenant-scoped; no cross-county access |
| Children's data and safeguarding | Sensitive data per-tenant isolated (ADR-D6-16) |
| UK GDPR lawful basis and rights impact | Controller boundaries per CFA clarified |
| Audit and evidential requirements | Tenant on every access log |
| Standards touched | ISO/IEC 27001, 27701, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 23 → multi-tenant rollout |
| Repository paths | `src/pf_ft_ai/` (tenant scoping) |
| Configuration | Per-tenant overlays; isolation config |
| Contracts / schemas | Tenant in authz context + metadata |
| Migration | Single→multi-tenant enablement |
| Dependencies on other ADRs | ADR-D6-03, D6-12, D4-10, D5-06, D6-16 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No cross-tenant access | CI isolation suite |
| AC-02 | Tenant from validated claims only | Security test |
| AC-03 | Sensitive data per-tenant isolated | Config/security review |
| AC-04 | County onboarding = config only | PR diff |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Per-tenant metrics; isolation checks |
| Alerting | Any cross-tenant access (sev-1) |
| Runbook | `docs/runbooks/multi-tenant.md` |
| Failure mode and degradation | Tenant issue isolated to that tenant |
| Rollback | Disable tenant |
| Support model impact | Per-tenant support routing |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Multi-tenant enablement | M | shared infra | Efficient at scale |
| Isolated store for sensitive data | setup | per-tenant store | Only where needed |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | A tenant needs full isolation | Compliance | Dedicated deploy for that tenant |
| RT-02 | Cross-tenant incident | Incident | CAR; harden isolation |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-37 |
| Specification sections | doc 9 §77–§78; doc 13 §36–§37, §152–§153; doc 14 §47–§48 |
| Requirement IDs | MT-* |
| Build phases | 23 → rollout |
| Code paths | tenant scoping |
| Configuration | per-tenant overlays |
| Tests | isolation suite |
| Upstream ADRs | ADR-D6-03, D6-12, D4-10 |
| Downstream ADRs | ADR-D6-16 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
