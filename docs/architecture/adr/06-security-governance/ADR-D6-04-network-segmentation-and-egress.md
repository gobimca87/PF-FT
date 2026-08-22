---
id: ADR-D6-04
title: Network segmentation, private connectivity and egress control
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [Platform Engineer, SRE]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D6-01, ADR-D5-08, ADR-D6-07, ADR-D5-07, ADR-D2-19]
source_docs:
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §18, §19, §20, §21, §22"
  - "MD files/6 Production/25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md §22, §23, §24, §25, §26"
build_phases: [1]
impacted_paths:
  - infra/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-04 — Network segmentation, private connectivity and egress control

## 1. Summary

PFF AI will run on segmented private networks with **private endpoints to all Azure PaaS
(Key Vault, ACR, Service Bus, Redis, vector store), no public data-plane exposure, and
default-deny egress** with an explicit allowlist for the few external destinations (HF
API during the initial phase, enterprise APIs via APIM) — implementing the zero-trust
network layer (doc 19 §18–§22; doc 25 §22–§26). Only APIM is internet-facing inbound.

## 2. Context and Problem Statement

Doc 19 §18–§22 define network security, inbound traffic, FastAPI exposure, outbound
security and SLM network security; doc 25 §22–§26 network architecture, segmentation,
private connectivity, egress control and DNS. Uncontrolled egress is a primary
data-exfiltration path; public PaaS endpoints widen the attack surface. This ADR fixes
segmentation, private connectivity and egress.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | Private endpoints; no public data plane | doc 25 §24; doc 19 §18 |
| DR-C-02 | Default-deny egress + allowlist | doc 19 §21; doc 25 §25 |
| DR-F-01 | Only APIM internet-facing inbound | doc 19 §19–§20 |
| DR-F-02 | Segmentation between trust zones | doc 25 §23; ADR-D6-01 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | External deps are few + known | Broaden allowlist carefully | Egress review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Exfiltration control (egress) | 28 | Primary data-loss path | Egress policy |
| EC-02 | Attack-surface reduction (private PaaS) | 24 | No public data plane | Public exposure |
| EC-03 | Segmentation strength | 20 | Zone isolation | Policy coverage |
| EC-04 | Operability (DNS/PE mgmt) | 16 | Run it | Complexity |
| EC-05 | Performance | 12 | PE latency | Overhead |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Private endpoints + default-deny egress allowlist + APIM-only inbound + zone segmentation

**Description.** All PaaS via private endpoints; egress default-deny with an explicit
allowlist (via firewall/egress gateway); only APIM public inbound; NSGs/network
policies segment zones; private DNS.
**Strengths.** Strong exfiltration + surface control; zero-trust aligned.
**Weaknesses.** PE/DNS/firewall management overhead.
**Cost / effort.** Medium.

### 5.2 Option B — Public PaaS endpoints + firewall rules

**Description.** PaaS reachable publicly, restricted by IP firewall.
**Strengths.** Simpler.
**Weaknesses.** Public data plane; IP allowlists brittle; larger surface (violates §24).
**Cost / effort.** Low; weaker.

### 5.3 Option C — Private endpoints but open egress

**Description.** Private inbound/PaaS, but unrestricted outbound.
**Strengths.** Simpler egress.
**Weaknesses.** Exfiltration path wide open (violates §21).
**Cost / effort.** Low; unsafe egress.

### 5.4 Option D — Service endpoints (not private endpoints)

**Description.** Azure service endpoints instead of private endpoints.
**Strengths.** Simpler than PE.
**Weaknesses.** Traffic stays on Azure backbone but service still has a public endpoint;
weaker than PE for zero-trust.
**Cost / effort.** Low; weaker.

### 5.5 Option E — Private endpoints + egress via a secured proxy/firewall with inspection

**Description.** Option A plus an egress proxy performing TLS inspection/logging of
allowed destinations.
**Strengths.** Strongest egress visibility/control.
**Weaknesses.** Proxy complexity; TLS inspection considerations.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Public FastAPI (no APIM) | doc 19 §19–§20 |
| Open network (no segmentation) | doc 25 §23; ADR-D6-01 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 19 §18–§22 and doc 25 §22–§26.

| Criterion | Weight | A: PE+deny-egress | B: Public+FW | C: PE+open egress | D: Service endpoints | E: PE+egress proxy |
|---|---|---|---|---|---|---|
| EC-01 Egress control | 28 | 5 | 3 | 1 | 3 | 5 |
| EC-02 Surface reduction | 24 | 5 | 2 | 5 | 3 | 5 |
| EC-03 Segmentation | 20 | 5 | 3 | 4 | 3 | 5 |
| EC-04 Operability | 16 | 4 | 5 | 4 | 5 | 3 |
| EC-05 Performance | 12 | 4 | 4 | 4 | 4 | 3 |
| **Weighted total** | **100** | **472** | **314** | **352** | **342** | **456** |

Totals (×20): **A = 472**, **E = 456**, **C = 352**, **D = 342**, **B = 314**.

**Sensitivity.** A leads; an egress proxy with inspection (E) adds visibility and is a
strong hardening step for higher threat levels (RT-01). Open egress (C) and public PaaS
(B) fail the exfiltration/surface criteria.

## 7. Decision

**PFF AI will use private endpoints for all Azure PaaS, default-deny egress with an
explicit allowlist, APIM-only internet-facing inbound, and network segmentation between
trust zones with private DNS (Option A).** An egress proxy with inspection (E) is a
documented hardening for elevated threat levels. Public PaaS (B), open egress (C) and
service-endpoints-only (D) are rejected.

## 8. Architecture Detail

- Private endpoints for Key Vault (ADR-D5-07), ACR (ADR-D5-09), Service Bus (ADR-D2-16),
  Redis (ADR-D4-10), vector store (ADR-D3-24); private DNS zones.
- Egress: default-deny NSG/Azure Firewall with an allowlist (HF API for the initial SLM
  phase — removed after self-host cutover, ADR-D3-13; enterprise APIs via APIM).
- Inbound: only APIM public (ADR-D5-15); FastAPI not directly exposed (doc 19 §20).
- Zone segmentation per ADR-D6-01; portal links resolved server-side (ADR-D2-19) so no
  arbitrary outbound from model output.

## 9. Consequences

### 9.1 Positive
- Exfiltration path closed; minimal public surface; zone isolation.
### 9.2 Negative
- PE/DNS/firewall operational overhead.
### 9.3 Neutral
- Egress allowlist shrinks after self-host cutover.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Network simplicity | Exfiltration + surface control | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Enterprise APIs reached only via controlled paths |
| Precedence chain | Protects authoritative data flows |
| Four-state separation | Data-zone network isolation |
| Versioned artefacts | Network policy in IaC |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Data exfiltration via egress | Low | High | M | Default-deny + allowlist (+ proxy option) | Security Architect | Low |
| RSK-02 | Misconfigured PE exposes PaaS | Low | High | M | IaC policy + scans | Platform Eng | Low |
| RSK-03 | Allowlist too broad | Med | Med | M | Periodic egress review | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | PaaS with public data plane | 0 | > 0 | Config scan | Continuous |
| QM-02 | Unallowlisted egress attempts | 0 (blocked) | > 0 allowed | Firewall logs | Continuous |
| QM-03 | Internet-facing services besides APIM | 0 | > 0 | Config audit | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Major reduction (private PaaS, deny egress) |
| Data classification touched | Protects all data in transit |
| Personal data / PII | Exfiltration control |
| Children's data and safeguarding | Prevents unauthorised outbound of safeguarding data |
| UK GDPR lawful basis and rights impact | Security-of-processing |
| Audit and evidential requirements | Egress + PE logs |
| Standards touched | ISO/IEC 27001, NIST CSF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `infra/` |
| Configuration | PE, DNS, egress allowlist, NSGs |
| Contracts / schemas | N/A |
| Migration | Remove HF egress after self-host |
| Dependencies on other ADRs | ADR-D5-08, D6-01, D6-07 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All PaaS via private endpoint | Config scan |
| AC-02 | Egress default-deny + allowlist | Firewall config test |
| AC-03 | Only APIM public inbound | Config audit |
| AC-04 | Zones segmented | Network policy test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Egress attempts; PE health; DNS |
| Alerting | Blocked/anomalous egress |
| Runbook | `docs/runbooks/network.md` |
| Failure mode and degradation | Egress deny fails closed |
| Rollback | IaC revert |
| Support model impact | Security + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Private endpoints/firewall | setup | per-PE/firewall | Azure pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Elevated threat/exfiltration risk | Risk review | Add egress proxy with inspection (E) |
| RT-02 | Exfiltration incident | Incident | CAR; tighten egress |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | doc 19 §18–§22; doc 25 §22–§26 |
| Requirement IDs | SEC-NET-* |
| Build phases | 1 |
| Code paths | `infra/` |
| Configuration | PE/egress/NSG |
| Tests | network policy suites |
| Upstream ADRs | ADR-D6-01, D5-08 |
| Downstream ADRs | ADR-D6-07 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
