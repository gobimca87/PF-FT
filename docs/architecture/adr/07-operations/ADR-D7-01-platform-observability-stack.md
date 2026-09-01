---
id: ADR-D7-01
title: Platform observability stack — Azure Monitor / App Insights / Log Analytics
domain: 7 Operations
ws_ref: [WS-31]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: SRE
contributors: [Platform Engineer, AI Architecture Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-02, ADR-D7-03, ADR-D7-04, ADR-D5-08, ADR-D7-07]
source_docs:
  - "MD files/6 Production/24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §4, §5, §6, §11, §12, §49"
build_phases: [10]
impacted_paths:
  - src/pf_ft_ai/observability/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-01 — Platform observability stack — Azure Monitor / App Insights / Log Analytics

## 1. Summary

PFF AI will use the **Azure-native observability stack — Azure Monitor, Application
Insights and Log Analytics** — for platform metrics, traces and logs, answering the four
runtime questions (is it up, is it fast, is it correct, is it costing what we expect)
(24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §4–§6, §11–§12, §49; CLAUDE.md). AI-specific observability (Langfuse) is a
distinct, complementary layer (ADR-D7-02).

## 2. Context and Problem Statement

24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §4–§6 define the observability architecture, pillars and four runtime questions;
§11–§12 application/structured logging; §49 metrics; CLAUDE.md names Azure Monitor/App
Insights/Log Analytics for platform observability and Langfuse for AI-specific. Without a
defined stack, telemetry is fragmented and incident response is blind. This ADR fixes the
platform observability stack (D7-02 covers AI-specific; D7-03 correlation; D7-04 logging).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Metrics + traces + logs (three pillars) | 24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §5 |
| DR-F-02 | Answer the four runtime questions | 24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §6 |
| DR-N-01 | Azure-native integration (AKS/APIM/PaaS) | ADR-D5-08 |
| DR-F-03 | Feed SLOs/alerts | ADR-D7-07/08 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Azure-native telemetry meets needs | Add OSS stack | Ops review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Azure/AKS/PaaS integration | 26 | Full-stack telemetry | Native coverage |
| EC-02 | Three-pillar coverage | 22 | Complete observability | Metrics/traces/logs |
| EC-03 | Operability/managed | 18 | Small team | Managed |
| EC-04 | Cost | 16 | Ingestion cost | £/GB |
| EC-05 | Openness/portability | 18 | Avoid lock-in | OTel support |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Azure Monitor + Application Insights + Log Analytics (OTel-instrumented)

**Description.** Azure-native stack; app instrumented with OpenTelemetry exporting to App
Insights; Log Analytics for logs/queries; Azure Monitor for metrics/alerts.
**Strengths.** Deep Azure/AKS/APIM integration; managed; OTel keeps portability; feeds
alerts/SLOs.
**Weaknesses.** Ingestion cost at volume; some lock-in (mitigated by OTel).
**Cost / effort.** Low-medium.

### 5.2 Option B — Self-hosted Prometheus + Grafana + Loki + Tempo

**Description.** OSS observability stack on AKS.
**Strengths.** Portable; powerful; cost-controlled at scale.
**Weaknesses.** Operate a stateful stack; less native Azure/PaaS integration.
**Cost / effort.** High ops.

### 5.3 Option C — Third-party SaaS APM (Datadog/New Relic)

**Description.** External APM.
**Strengths.** Rich features; managed.
**Weaknesses.** Off-tenancy telemetry; cost; another vendor.
**Cost / effort.** Medium; data-egress/cost.

### 5.4 Option D — Azure-native + self-hosted Grafana for dashboards

**Description.** App Insights/Log Analytics for data, Grafana for visualisation.
**Strengths.** Azure data + flexible dashboards.
**Weaknesses.** Extra Grafana to run; Azure Managed Grafana reduces this.
**Cost / effort.** Medium.

### 5.5 Option E — Azure-native + OTel Collector to a portable backend option

**Description.** Option A with an OTel Collector so telemetry can also/later route to an
OSS/other backend.
**Strengths.** Azure integration now + portability lever.
**Weaknesses.** Collector to manage.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No platform observability | 24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §4 |
| Logs-only (no metrics/traces) | 24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §5 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §4–§12/§49 and ADR-D5-08.

| Criterion | Weight | A: Azure-native | B: OSS self-host | C: SaaS APM | D: Azure+Grafana | E: Azure+OTel Collector |
|---|---|---|---|---|---|---|
| EC-01 Azure integration | 26 | 5 | 3 | 3 | 5 | 5 |
| EC-02 Three-pillar | 22 | 5 | 5 | 5 | 5 | 5 |
| EC-03 Operability | 18 | 5 | 2 | 4 | 4 | 4 |
| EC-04 Cost | 16 | 3 | 4 | 2 | 3 | 3 |
| EC-05 Portability | 18 | 4 | 5 | 3 | 4 | 5 |
| **Weighted total** | **100** | **444** | **384** | **344** | **432** | **456** |

Totals (×20): **E = 456**, **A = 444**, **D = 432**, **B = 384**, **C = 344**.

**Sensitivity.** E (Azure-native + OTel Collector) edges A by keeping a portability lever
without giving up Azure integration; the Collector is modest overhead. A is the baseline;
adding the Collector (E) is adopted to avoid lock-in. SaaS APM (C) loses on off-tenancy
telemetry/cost.

## 7. Decision

**PFF AI will use the Azure-native observability stack (Azure Monitor, Application
Insights, Log Analytics), instrumented via OpenTelemetry with an OTel Collector to
preserve portability (Option E).** Managed Grafana may provide dashboards over the same
data. Langfuse (ADR-D7-02) is the complementary AI-specific layer. Self-host OSS (B) and
SaaS APM (C) are rejected as the primary stack.

## 8. Architecture Detail

- OTel instrumentation in `src/pf_ft_ai/observability/`; exporters via an OTel Collector
  to App Insights (traces/metrics) and Log Analytics (logs); Azure Monitor alerts
  (ADR-D7-08).
- Three pillars answer the four runtime questions (§6); correlation ids (ADR-D7-03) tie
  them; structured logs (ADR-D7-04); AI-quality metrics also mirrored where useful (§50).
- Dashboards per subsystem; SLO signals feed ADR-D7-07.

## 9. Consequences

### 9.1 Positive
- Full-stack, managed, Azure-integrated observability with a portability lever.
### 9.2 Negative
- Ingestion cost; Collector to manage.
### 9.3 Neutral
- Complements Langfuse (D7-02).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Full portability of pure-OSS | Azure integration + managed ops | SRE |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Observability of the AI layer; no business authority |
| Precedence chain | N/A |
| Four-state separation | Telemetry redacted per classification (ADR-D7-04) |
| Versioned artefacts | Dashboards/alerts as code |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Ingestion cost overrun | Med | Med | M | Sampling; log-level tuning | FinOps | Low |
| RSK-02 | Lock-in | Low | Low | L | OTel + Collector (E) | SRE | Low |
| RSK-03 | Sensitive data in telemetry | Low | High | M | Redaction (ADR-D7-04) | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Services emitting metrics/traces/logs | 100% | < 100% | Coverage audit | Per release |
| QM-02 | Four-runtime-questions answerable | yes | gaps | Dashboard review | Monthly |
| QM-03 | Telemetry ingestion cost | ≤ budget | over | FinOps | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Telemetry endpoints; in-tenancy |
| Data classification touched | Telemetry (redacted) |
| Personal data / PII | Redacted (ADR-D7-04) |
| Children's data and safeguarding | No safeguarding data in telemetry |
| UK GDPR lawful basis and rights impact | Minimised telemetry |
| Audit and evidential requirements | Distinct from audit (ADR-D6-17) |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 10 |
| Repository paths | `src/pf_ft_ai/observability/` |
| Configuration | OTel + Collector + exporters |
| Contracts / schemas | Telemetry schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-08, D7-03, D7-04 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Metrics/traces/logs emitted for all services | Coverage audit |
| AC-02 | Four runtime questions answerable | Dashboard review |
| AC-03 | Telemetry redacted | Redaction test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | The stack itself; ingestion health |
| Alerting | Telemetry pipeline failures |
| Runbook | `docs/runbooks/observability.md` |
| Failure mode and degradation | Telemetry loss doesn't stop serving |
| Rollback | Config revert |
| Support model impact | SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Azure Monitor/App Insights/Log Analytics | setup | ingestion/retention | Azure pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Ingestion cost too high | QM-03 | Sampling / route some to OSS via Collector |
| RT-02 | Portability required | Strategy | Route via Collector to OSS backend |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-31 Observability |
| Specification sections | 24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md §4–§6, §11–§12, §49–§50 |
| Requirement IDs | OBS-PLAT-* |
| Build phases | 10 |
| Code paths | `src/pf_ft_ai/observability/` |
| Configuration | OTel/Collector |
| Tests | telemetry coverage |
| Upstream ADRs | ADR-D5-08 |
| Downstream ADRs | ADR-D7-02, D7-03, D7-07 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | SRE | Initial decision recorded. |
