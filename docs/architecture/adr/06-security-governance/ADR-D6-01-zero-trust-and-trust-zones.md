---
id: ADR-D6-01
title: Zero-trust model and trust-zone definition
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [Platform Engineer, Principal Architect]
reviewers: [AI Architecture Lead]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D6-02, ADR-D6-04, ADR-D5-15, ADR-D6-09, ADR-D5-08]
source_docs:
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §5, §6, §7, §8, §16, §17"
build_phases: [2]
impacted_paths:
  - infra/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-01 — Zero-trust model and trust-zone definition

## 1. Summary

PFF AI will adopt a **zero-trust** security model: no request, service or network
location is trusted by default; every hop authenticates, authorizes and validates. The
platform is divided into explicit **trust zones** (edge/APIM, AI runtime, integration,
data/state, external SLM) with controlled, least-privilege transitions between them
(doc 19 §5–§8, §16–§17). Trust is never inferred from network position alone.

## 2. Context and Problem Statement

Doc 19 §5–§6 define defense-in-depth and security boundaries, §7–§8 trust zones and the
zero-trust principle, §16–§17 the APIM boundary and AI platform security
responsibilities. Implicit trust ("it's inside the VNet, so it's safe") is the root of
lateral-movement breaches. This ADR fixes the zero-trust posture and the trust-zone map
that the other security ADRs build on.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | No implicit trust by network location | doc 19 §8 |
| DR-F-01 | Explicit trust zones + controlled transitions | doc 19 §6–§7 |
| DR-F-02 | Every hop authNs/authZs/validates | doc 19 §5, §16 |
| DR-N-01 | Least privilege between zones | doc 19 §17 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Identity-based controls available (Entra/MI) | Compensating network controls | Infra review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Breach containment (lateral movement) | 30 | Core zero-trust benefit | Blast-radius tests |
| EC-02 | Enforceability (identity + policy) | 24 | Real, not aspirational | Per-hop checks |
| EC-03 | Clarity of zone model | 18 | Teams apply it | Zone map |
| EC-04 | Performance/latency overhead | 14 | Per-hop checks cost | Latency |
| EC-05 | Operability | 14 | Manage it | Complexity |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Zero-trust with explicit trust zones + identity-based transitions

**Description.** Deny-by-default; each zone transition requires identity + authorization
+ validation; least-privilege network + RBAC; APIM as the entry authz boundary
(ADR-D5-15).
**Strengths.** Strong containment; enforceable; aligns with doc 19.
**Weaknesses.** Per-hop checks add some latency/complexity.
**Cost / effort.** Medium.

### 5.2 Option B — Perimeter security (trust the internal network)

**Description.** Hard edge, soft interior.
**Strengths.** Simple; low internal overhead.
**Weaknesses.** One breach → lateral movement; violates doc 19 §8.
**Cost / effort.** Low; unsafe.

### 5.3 Option C — Network segmentation only (no identity zero-trust)

**Description.** VNet/subnet segmentation without per-request identity checks.
**Strengths.** Limits some movement.
**Weaknesses.** Trusts anything within a segment; no per-request authz; partial.
**Cost / effort.** Medium; incomplete.

### 5.4 Option D — Service mesh mTLS as the whole model

**Description.** Rely on mesh mTLS for zero-trust.
**Strengths.** Strong in-cluster identity + encryption.
**Weaknesses.** Covers in-cluster only; external SLM/enterprise/APIM hops need more;
mesh is a mechanism, not the full zone model.
**Cost / effort.** Medium-high; partial.

### 5.5 Option E — Zero-trust + microsegmentation + continuous verification (advanced)

**Description.** Option A plus per-workload microsegmentation and continuous posture
checks.
**Strengths.** Strongest posture.
**Weaknesses.** Higher complexity/cost; more than first release needs.
**Cost / effort.** High; phase later.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Implicit trust anywhere | doc 19 §8 |
| VPN-only access control | Doesn't address per-request authz |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 19 §5–§8/§16–§17.

| Criterion | Weight | A: Zero-trust+zones | B: Perimeter | C: Net-seg only | D: Mesh mTLS | E: ZT+microseg |
|---|---|---|---|---|---|---|
| EC-01 Containment | 30 | 5 | 1 | 3 | 4 | 5 |
| EC-02 Enforceability | 24 | 5 | 2 | 3 | 4 | 5 |
| EC-03 Clarity | 18 | 5 | 4 | 3 | 3 | 4 |
| EC-04 Performance | 14 | 4 | 5 | 4 | 4 | 3 |
| EC-05 Operability | 14 | 4 | 5 | 4 | 3 | 2 |
| **Weighted total** | **100** | **472** | **282** | **330** | **376** | **436** |

Totals (×20): **A = 472**, **E = 436**, **D = 376**, **C = 330**, **B = 282**.

**Sensitivity.** A leads; microsegmentation/continuous verification (E) is a later
hardening step (RT-01). Mesh mTLS (D) is adopted as a *mechanism within* A for
in-cluster hops, not the whole model. Perimeter (B) is decisively rejected.

## 7. Decision

**PFF AI will adopt zero-trust with explicit trust zones (edge/APIM, AI runtime,
integration, data/state, external SLM) and identity-based, least-privilege, validated
transitions between them (Option A).** APIM is the entry authz boundary (ADR-D5-15);
private networking (ADR-D6-04) and RBAC enforce zone transitions; service-mesh mTLS may
implement in-cluster hops. Microsegmentation/continuous verification (E) is a later
hardening. Perimeter (B) and segmentation-only (C) are rejected.

**Status rationale.** `Accepted` — doc 19 §8 mandates zero-trust.

## 8. Architecture Detail

- Trust zones and their allowed transitions documented; deny-by-default network policy
  (ADR-D6-04); each transition requires identity (Managed Identity/Entra) + authorization.
- Guardrails (ADR-D6-09) validate content at zone boundaries; APIM validates at the edge
  (ADR-D5-15); external SLM is its own low-trust zone (ADR-D6-07).
- Least-privilege RBAC per service identity (ADR-D6-05 keys, ADR-D5-07 secrets).

## 9. Consequences

### 9.1 Positive
- Strong breach containment; enforceable per-hop security.
### 9.2 Negative
- Per-hop checks add latency/complexity.
### 9.3 Neutral
- Frames all other security ADRs.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Internal-network convenience | Containment + enforceability | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Zero-trust reinforces enterprise as the authz authority |
| Precedence chain | Trust zones protect authoritative data flows |
| Four-state separation | Data/state zone isolated |
| Versioned artefacts | Zone/network policy in IaC |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Misconfigured zone transition | Low | High | M | Policy-as-code + tests | Security Architect | Low |
| RSK-02 | Latency from per-hop checks | Med | Low | L | Efficient identity caching | Platform Eng | Low |
| RSK-03 | Implicit trust creeps back | Med | High | H | Fitness tests; reviews | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Zone transitions requiring identity+authz | 100% | < 100% | Policy audit | Per release |
| QM-02 | Lateral-movement in breach drills | contained | escapes | Chaos/security tests | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Deny-by-default reduces surface; limits blast radius |
| Data classification touched | All zones classified |
| Personal data / PII | Data zone strongly isolated |
| Children's data and safeguarding | Safeguarding data in most-protected zone |
| UK GDPR lawful basis and rights impact | Supports security-of-processing |
| Audit and evidential requirements | Zone-transition logging |
| Standards touched | ISO/IEC 27001, 42001, NIST CSF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 2 |
| Repository paths | `infra/` (network policy, RBAC) |
| Configuration | Zone map; network policy |
| Contracts / schemas | N/A |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-15, D6-04, D6-05 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Deny-by-default network policy | Config audit |
| AC-02 | Each zone transition identity+authz gated | Security test |
| AC-03 | Breach drill shows containment | Chaos test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Zone-transition + denied-access metrics |
| Alerting | Unexpected cross-zone attempts |
| Runbook | `docs/runbooks/security-zones.md` |
| Failure mode and degradation | Fail closed on authz failure |
| Rollback | Policy revert |
| Support model impact | Security + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Policy/identity infra | setup | low | Azure-native |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Threat level rises | Risk review | Add microsegmentation/continuous verification (E) |
| RT-02 | Lateral-movement incident | Incident | CAR; tighten zones |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 Security |
| Specification sections | doc 19 §5–§8, §16–§17 |
| Requirement IDs | SEC-ZT-* |
| Build phases | 2 |
| Code paths | `infra/` |
| Configuration | zone/network policy |
| Tests | breach-drill + policy suites |
| Upstream ADRs | ADR-D5-08, D5-15 |
| Downstream ADRs | ADR-D6-02, D6-04, D6-09 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
