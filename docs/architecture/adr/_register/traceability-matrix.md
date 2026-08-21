# Traceability Matrix

End-to-end traceability for every decision in this library, in three directions:

1. **Workshop sheet → ADRs** — which decisions a WS sheet decomposed into.
2. **Specification document → ADRs** — which decisions a `MD files/` doc governs.
3. **ADR → implementation** — build phase, repository path, configuration, tests.

The traceability model itself is a decision, recorded in
[ADR-D8-07](../08-business-value/ADR-D8-07-decision-register-and-traceability-model.md).

## 1. Workshop sheet → ADR

| WS | Sheet | Domain | ADRs |
|---|---|---|---|
| WS-01 | Executive Summary | 1 | |
| WS-02 | Business Vision, Problem Statement & Objectives | 1 | |
| WS-03 | Business Capability Map | 1 | |
| WS-04 | Personas & User Journey Mapping | 1 | |
| WS-05 | Enterprise Workflow Catalogue | 1 | |
| WS-06 | Functional & Non-Functional Requirements | 1 | |
| WS-07 | Enterprise Reference Architecture | 2 | |
| WS-08 | Workflow Orchestration Architecture | 2 | |
| WS-09 | Enterprise Context Architecture | 2 | |
| WS-10 | Integration & 18-Microservice Matrix | 2 | |
| WS-11 | Event Notification & Real-Time Synchronization | 2 | |
| WS-12 | AI Capability Mapping | 3 | |
| WS-13 | Agentic AI Architecture | 3 | |
| WS-14 | Conversation Decision Architecture | 3 | |
| WS-15 | Prompt Engineering & Persona Design | 3 | |
| WS-16 | SLM Architecture & Model Selection | 3 | |
| WS-17 | RAG Architecture — Knowledge & FAQ Only | 3 | |
| WS-18 | Context Engineering Strategy | 3 | |
| WS-19 | Enterprise Context Model | 4 | |
| WS-20 | Data & Knowledge Architecture | 4 | |
| WS-21 | Metadata & API Response Standards | 4 | |
| WS-22 | Session Memory & Conversation State | 4 | |
| WS-23 | Technology Stack Decision Matrix | 5 | |
| WS-24 | Infrastructure & Self-Hosted AI Deployment | 5 | |
| WS-25 | API Security & Enterprise Integration | 5 | |
| WS-26 | Performance, Scalability & Optimization | 5 | |
| WS-27 | AI Security Architecture | 6 | |
| WS-28 | Responsible AI & Governance | 6 | |
| WS-29 | Compliance, Privacy & Audit | 6 | |
| WS-30 | ISO & Enterprise Standards Checklist | 6 | |
| WS-31 | Observability & Monitoring | 7 | |
| WS-32 | DevOps, CI/CD & AI Engineering | 7 | |
| WS-33 | Operational Support Model | 7 | |
| WS-34 | Cost & ROI Analysis | 8 | |
| WS-35 | Business KPI Dashboard | 8 | |
| WS-36 | Risks, Assumptions & Decision Register | 8 | |
| WS-37 | Future Roadmap & Platform Extensibility | 8 | |

## 2. Specification document → ADR

| # | Specification document | ADRs |
|---|---|---|
| 1 | `1 Foundation/1 PF-FT-AI-ARCHITECTURE.md` | |
| 2 | `1 Foundation/2. PF-FT-AI-ARCHITECTURE-DETAILED.md` | |
| 3 | `1 Foundation/3. PF-FT-AI-RESPONSIBILITY-MATRIX.md` | |
| 4 | `1 Foundation/4. PF-FT-AI-RUNTIME.md` | |
| 5 | `1 Foundation/5. PF-FT-AI-STATE-MODEL.md` | |
| 6 | `2 Agent Runtime/6 PF-FT-AI-CONVERSATION-SESSION.md` | |
| 7 | `2 Agent Runtime/7 PF-FT-AI-AGENTIC-ORCHESTRATION.md` | |
| 8 | `3 Context & Integration/8 PF-FT-AI-ERC-CONTEXT.md` | |
| 9 | `3 Context & Integration/9 PF-FT-AI-MEMORY-CACHE.md` | |
| 10 | `3 Context & Integration/10 PF-FT-AI-ENTERPRISE-INTEGRATION.md` | |
| 11 | `3 Context & Integration/11 PF-FT-AI-SERVICE-BUS.md` | |
| 12 | `3 Context & Integration/12 PF-FT-AI-PORTAL-LINKS.md` | |
| 13 | `4 AI/13.FP-FT-AI-RAG.md` | |
| 14 | `4 AI/14.PF-FT-AI-EMBEDDING-VECTOR.md` | |
| 15 | `4 AI/15.PF-FT-AI-SLM.md` | |
| 16 | `4 AI/16.PF-FT-AI-PROMPT-ENGINEERING.md` | |
| 17 | `4 AI/17.PF-FT-AI-CONFIGURATION-VERSIONING.md` | |
| 18 | `4 AI/18.PF-FT-AI-GUARDRAILS.md` | |
| 19 | `5 QualityGovernance/19.PF-FT-AI-SECURITY.md` | |
| 20 | `5 QualityGovernance/20.PF-FT-AI-GOVERNANCE.md` | |
| 21 | `5 QualityGovernance/21.PF-FT-AI-EVALUATION.md` | |
| 22 | `5 QualityGovernance/22.PF-FT-AI-TESTING.md` | |
| 23 | `5 QualityGovernance/23.PF-FT-AI-ENGINEERING-AGENTS.md` | |
| 24 | `6 Production/24.PF-FT-AI-OBSERVABILITY-RESILIENCE.md` | |
| 25 | `6 Production/25.PF-FT-AI-INFRASTRUCTURE-OPERATIONS.md` | |
| 26 | `6 Production/26.PF-FT-AI-PERFORMANCE-COST.md` | |
| 27 | `6 Production/27.PF-FT-AI-DEVELOPMENT-STANDARDS.md` | |
| 28 | `6 Production/28.PF-FT-AI-OPERATIONS-RUNBOOK.md` | |
| 29 | `0 Workflow/pff_affiliation_e2e_flow.md` | |
| — | `Examples/SampleWorkflowchat.md` (persona golden reference) | |

## 3. ADR → implementation

| ADR | Build phase | Repository path | Configuration | Tests |
|---|---|---|---|---|

*Rows are added as each ADR lands.*
