---
id: ADR-D7-18
title: Disaster recovery, business continuity, RPO/RTO
domain: 7 Operations
ws_ref: [WS-33]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [Platform Engineer, Principal Architect, AI Architecture Lead]
reviewers: [Architecture Review Board]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-10, ADR-D3-24, ADR-D5-06, ADR-D7-16, ADR-D2-10]
source_docs:
  - "MD files/6 Production/28.PF-FT-AI-OPERATIONS-RUNBOOK.md §42, §43, §48, §49, §50"
  - "MD files/4 AI/14.PF-FT-AI-EMBEDDING-VECTOR.md §85, §86, §136, §137"
  - "MD files/4 AI/13.FP-FT-AI-RAG.md §186"
build_phases: [21]
impacted_paths:
  - docs/runbooks/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-18 — Disaster recovery, business continuity, RPO/RTO

## 1. Summary

PFF AI will define **RPO/RTO targets per data class and a DR strategy** that leans on the
platform being **largely stateless and reconstructable**: code/config/AI-artefacts redeploy
from Git + manifest (ADR-D5-06); the RAG index rebuilds from canonical documents (doc 14
§85–§86; doc 13 §186); only conversation/session/memory state (Redis, ADR-D4-10) needs
backup/replication (doc 28 §42–§50). Continuity favours graceful degradation over hard
downtime.

## 2. Context and Problem Statement

Doc 28 §42–§43 rollback, §48–§50 SLM/self-hosted-SLM failure procedures; doc 14 §85–§86
canonical data/rebuild, §136–§137 DR/rebuild strategy; doc 13 §186 final RAG architecture
(rebuildable). No DR plan means an outage/region failure could cause data loss or extended
downtime. This ADR fixes RPO/RTO and the DR/BC strategy, exploiting the platform's
reconstructability.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | RPO/RTO per data class | BC/DR practice |
| DR-F-02 | Reconstruct code/config/artefacts/index | ADR-D5-06; doc 14 §86; doc 13 §186 |
| DR-C-01 | Backup/replicate genuinely stateful data | ADR-D4-10 |
| DR-F-03 | Graceful degradation for dependency loss | doc 28 §48–§50; ADR-D3-18 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Enterprise systems have their own BC/DR | Coordinate with PFF | BC review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Data-loss protection (RPO) | 28 | Avoid losing state | RPO met |
| EC-02 | Recovery speed (RTO) | 24 | Downtime | RTO met |
| EC-03 | Cost-appropriateness | 18 | Not over-provisioned | £ vs need |
| EC-04 | Testability of DR | 16 | Proven, not paper | DR drills |
| EC-05 | Simplicity | 14 | Operable | Complexity |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Reconstruct-first DR: redeploy from Git/manifest + rebuild index; backup+replicate only stateful state; degrade gracefully

**Description.** RPO/RTO per data class; code/config/AI-artefacts redeploy from Git +
manifest; RAG index rebuilds from canonical docs (doc 14 §86); conversation/session/memory
(Redis) backed up + optionally geo-replicated (ADR-D4-10); dependency loss → graceful
degradation (ADR-D3-18); DR runbooks + drills.
**Strengths.** Right-sized, fast where it matters, testable; exploits reconstructability.
**Weaknesses.** Index rebuild time; Redis backup config.
**Cost / effort.** Low-medium.

### 5.2 Option B — Full active-active multi-region

**Description.** Run two regions live.
**Strengths.** Near-zero RTO/RPO.
**Weaknesses.** High cost/complexity; overkill for current scale/criticality.
**Cost / effort.** High.

### 5.3 Option C — Backup-only (no rebuild plan, no replication)

**Description.** Periodic backups, restore on disaster.
**Strengths.** Simple/cheap.
**Weaknesses.** Slow RTO; unclear index/artefact recovery; data-loss window.
**Cost / effort.** Low; slow recovery.

### 5.4 Option D — Warm standby in a second region (pilot light)

**Description.** Minimal standby, scale up on failover.
**Strengths.** Good RTO/RPO balance; cheaper than active-active.
**Weaknesses.** Standby cost; failover complexity. Strong for higher criticality.
**Cost / effort.** Medium.

### 5.5 Option E — Reconstruct-first (A) + geo-replicated stateful store + periodic DR game-days

**Description.** Option A with geo-replicated Redis (ADR-D4-10) for low RPO on
conversation/session state and regular DR game-days to prove RTO.
**Strengths.** A's efficiency + low RPO on stateful data + proven recovery.
**Weaknesses.** Replication cost; game-day effort.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No DR plan | BC requirement |
| Untested DR (paper only) | EC-04 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 28 §42–§50, doc 14 §85–§86/§136–
§137, doc 13 §186.

| Criterion | Weight | A: Reconstruct-first | B: Active-active | C: Backup-only | D: Warm standby | E: A+geo-replica+game-days |
|---|---|---|---|---|---|---|
| EC-01 RPO | 28 | 4 | 5 | 2 | 4 | 5 |
| EC-02 RTO | 24 | 4 | 5 | 2 | 4 | 5 |
| EC-03 Cost-appropriate | 18 | 5 | 1 | 5 | 3 | 4 |
| EC-04 Testability | 16 | 4 | 4 | 3 | 4 | 5 |
| EC-05 Simplicity | 14 | 5 | 2 | 5 | 3 | 4 |
| **Weighted total** | **100** | **432** | **372** | **310** | **372** | **472** |

Totals (×20): **E = 472**, **A = 432**, **B = 372**, **D = 372**, **C = 310**.

**Sensitivity.** E (reconstruct-first + geo-replicated stateful store + DR game-days) edges
A by lowering RPO on conversation/session state and proving RTO through drills, at modest
cost. Active-active (B) is over-provisioned now; warm standby (D) is the escalation if
criticality rises (RT-01).

## 7. Decision

**PFF AI will use a reconstruct-first DR strategy — redeploy code/config/AI-artefacts from
Git + immutable manifest, rebuild the RAG index from canonical documents, and back up +
geo-replicate the genuinely stateful conversation/session/memory store — with RPO/RTO
targets per data class, graceful degradation for dependency loss, and periodic DR
game-days (Option E).** Active-active (B) is deferred until criticality warrants; warm
standby (D) is the intermediate escalation; backup-only (C) is rejected for slow RTO.

## 8. Architecture Detail

- RPO/RTO table per data class: enterprise data (PFF-owned, their BC); AI code/config/
  artefacts (RPO≈0 via Git/manifest, RTO=redeploy time); RAG index (RPO from canonical
  docs, RTO=rebuild time, doc 14 §86); conversation/session/memory (RPO from Redis
  backup/geo-replica, ADR-D4-10).
- Long-running workflows resume from durable state (ADR-D2-10); dependency loss →
  degraded mode (ADR-D3-18; doc 28 §48–§50); DR runbooks (doc 28) + scheduled game-days
  validate RTO/RPO.
- Region failover procedure documented; index rebuild automated (doc 14 §137; doc 13
  §186).

## 9. Consequences

### 9.1 Positive
- Right-sized DR exploiting reconstructability; low RPO on real state; proven recovery.
### 9.2 Negative
- Index rebuild time; replication cost; game-day effort.
### 9.3 Neutral
- Escalation path (warm standby/active-active) if criticality grows.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Active-active's near-zero RTO | Cost-appropriateness now | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Enterprise data recovered by PFF; AI recovers its own layer |
| Precedence chain | Rebuilt index/state stays below authoritative enterprise truth |
| Four-state separation | DR strategy differs per state class |
| Versioned artefacts | Redeploy from immutable manifest |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Conversation/session data loss | Low | Med | M | Backup + geo-replica (E) | SRE | Low |
| RSK-02 | Long index rebuild → extended RAG downtime | Med | Med | M | Automated rebuild; degrade RAG meanwhile | AI Arch Lead | Low |
| RSK-03 | DR plan untested | Med | High | H | Periodic game-days (E) | SRE | Low |
| RSK-04 | Region outage | Low | High | M | Failover procedure; escalate to warm standby | Platform Eng | Med |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | RPO met per data class | yes | breach | DR drills | Per game-day |
| QM-02 | RTO met per data class | yes | breach | DR drills | Per game-day |
| QM-03 | DR game-days run | on schedule | missed | Ops calendar | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Backups/replicas encrypted (ADR-D6-05) |
| Data classification touched | Backups classified + encrypted |
| Personal data / PII | Backup retention per policy (ADR-D4-07) |
| Children's data and safeguarding | Safeguarding data backups CMK-encrypted |
| UK GDPR lawful basis and rights impact | Backup retention/erasure honoured |
| Audit and evidential requirements | DR events + game-days recorded |
| Standards touched | ISO/IEC 27001 (A.17), ISO 22301-aligned |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 21 |
| Repository paths | `docs/runbooks/` (DR) |
| Configuration | Backup/replica; RPO/RTO table |
| Contracts / schemas | N/A |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-10, D3-24, D5-06, D2-10 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | RPO/RTO defined per data class | DR plan review |
| AC-02 | Code/artefacts redeploy from manifest | Recovery drill |
| AC-03 | Index rebuilds from canonical docs | Rebuild drill |
| AC-04 | Stateful store backup/replica restore | Restore drill |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Backup/replica health; rebuild status |
| Alerting | Backup failure; replication lag |
| Runbook | `docs/runbooks/dr.md` |
| Failure mode and degradation | Dependency loss → degraded mode; region loss → failover |
| Rollback | Restore from backup/redeploy manifest |
| Support model impact | SRE + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Backups + geo-replica | setup | storage/replica | Azure pricing |
| DR game-days | — | periodic effort | Ops time |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Criticality/RTO needs tighten | BC review | Adopt warm standby (D) / active-active (B) |
| RT-02 | DR drill fails targets | Game-day | Fix gaps; re-drill |

**Scheduled review:** `review_due` (and after every game-day).

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-33 |
| Specification sections | doc 28 §42–§50; doc 14 §85–§86, §136–§137; doc 13 §186 |
| Requirement IDs | DR-* |
| Build phases | 21 |
| Code paths | `docs/runbooks/` |
| Configuration | backup/replica/RPO-RTO |
| Tests | DR game-days |
| Upstream ADRs | ADR-D4-10, D5-06, D2-10 |
| Downstream ADRs | ADR-D7-16 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
