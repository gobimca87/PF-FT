# PFF AI — Decision Register

> Master register of all Architecture Decision Records in this library. Auto-derived
> from each ADR's YAML front matter (see [ADR-D8-07](../08-business-value/ADR-D8-07-decision-register-and-traceability.md)).
> Generated 2026-08-22.


**Total ADRs:** 136 across 9 domains. **Proposed (open) decisions:** 5 (see [open-decisions.md](open-decisions.md)).


## Domain 0 — Decision Programme & Governance

| ID | Title | Status | Owner | WS | Date |
|---|---|---|---|---|---|
| [ADR-D0-01](../00-decision-programme/ADR-D0-01-adopt-adr-driven-architecture-governance.md) | Adopt an in-repository ADR library with a CMMI DAR-aligned template | Accepted | AI Solution Architect | [WS-36] | 2026-08-21 |
| [ADR-D0-02](../00-decision-programme/ADR-D0-02-adr-identification-lifecycle-supersession.md) | ADR identification, status lifecycle, supersession and amendment policy | Accepted | AI Solution Architect | [WS-36] | 2026-08-21 |
| [ADR-D0-03](../00-decision-programme/ADR-D0-03-decision-authority-and-review-board.md) | Decision authority model and architecture review cadence | Accepted | AI Solution Architect | [WS-36] | 2026-08-21 |
| [ADR-D0-04](../00-decision-programme/ADR-D0-04-open-decision-register-and-escalation.md) | Open and deferred decision register with a phase-gated escalation path | Accepted | AI Solution Architect | [WS-36] | 2026-08-21 |

## Domain 1 — Business Architecture

| ID | Title | Status | Owner | WS | Date |
|---|---|---|---|---|---|
| [ADR-D1-01](../01-business-architecture/ADR-D1-01-platform-scope-boundary.md) | PFF AI scope boundary — a conversational orchestration layer, not a replacement enterprise platform | Accepted | AI Solution Architect | [WS-01] | 2026-08-21 |
| [ADR-D1-02](../01-business-architecture/ADR-D1-02-golden-rule-binding-architectural-constraint.md) | The Golden Rule as a binding architectural constraint with named enforcement points | Accepted | AI Solution Architect | [WS-01, WS-02] | 2026-08-21 |
| [ADR-D1-03](../01-business-architecture/ADR-D1-03-authoritative-truth-precedence-chain.md) | Authoritative-truth precedence chain for resolving source conflicts | Accepted | AI Solution Architect | [WS-01, WS-02] | 2026-08-21 |
| [ADR-D1-04](../01-business-architecture/ADR-D1-04-business-problem-framing-and-success-definition.md) | Business problem framing and measurable success definition | Accepted | AI Product Owner | [WS-02] | 2026-08-21 |
| [ADR-D1-05](../01-business-architecture/ADR-D1-05-club-affiliation-first-reference-workflow.md) | Club Affiliation as the first end-to-end reference workflow | Accepted | AI Product Owner | [WS-02, WS-05] | 2026-08-21 |
| [ADR-D1-06](../01-business-architecture/ADR-D1-06-business-capability-map-and-ownership.md) | Business capability map and capability ownership model | Accepted | AI Solution Architect | [WS-03] | 2026-08-21 |
| [ADR-D1-07](../01-business-architecture/ADR-D1-07-persona-model-and-access-archetypes.md) | Persona model and access archetypes derived from enterprise claims | Accepted | AI Product Owner | [WS-04] | 2026-08-21 |
| [ADR-D1-08](../01-business-architecture/ADR-D1-08-conversational-journey-and-hil-touchpoints.md) | Conversational journey design principles and human-in-the-loop touchpoints | Accepted | AI Product Owner | [WS-04] | 2026-08-21 |
| [ADR-D1-09](../01-business-architecture/ADR-D1-09-adam-persona-charter.md) | Adam AI persona charter — football-commentary tone as a governed product decision | Accepted | AI Product Owner | [WS-04] | 2026-08-21 |
| [ADR-D1-10](../01-business-architecture/ADR-D1-10-enterprise-workflow-catalogue-and-phasing.md) | Enterprise workflow catalogue, prioritisation and phasing | Accepted | AI Product Owner | [WS-05] | 2026-08-21 |
| [ADR-D1-11](../01-business-architecture/ADR-D1-11-agent-catalogue-scope-affiliation-only.md) | Agent catalogue scope — AffiliationAgent only in the first pass | Accepted | AI Solution Architect | [WS-05] | 2026-08-21 |
| [ADR-D1-12](../01-business-architecture/ADR-D1-12-requirements-baseline-and-traceability-scheme.md) | Functional and non-functional requirements baseline and identifier traceability scheme | Accepted | AI Solution Architect | [WS-06] | 2026-08-21 |

## Domain 2 — Application Architecture

| ID | Title | Status | Owner | WS | Date |
|---|---|---|---|---|---|
| [ADR-D2-01](../02-application-architecture/ADR-D2-01-layered-architecture-and-dependency-rule.md) | Layered architecture with a mechanically enforced dependency rule | Accepted | AI Solution Architect | [WS-07] | 2026-08-21 |
| [ADR-D2-02](../02-application-architecture/ADR-D2-02-single-runtime-agents-as-logical-capabilities.md) | Single AI runtime with agents as logical capabilities, not deployables | Accepted | AI Solution Architect | [WS-07] | 2026-08-21 |
| [ADR-D2-03](../02-application-architecture/ADR-D2-03-dual-runtime-request-and-event-driven.md) | Dual runtime model — request-driven and event-driven entry into one execution core | Accepted | AI Solution Architect | [WS-07] | 2026-08-21 |
| [ADR-D2-04](../02-application-architecture/ADR-D2-04-conversation-manager-responsibility-boundary.md) | Conversation Manager responsibility boundary | Accepted | AI Solution Architect | [WS-07, WS-08] | 2026-08-21 |
| [ADR-D2-05](../02-application-architecture/ADR-D2-05-supervisor-intent-routing.md) | Supervisor intent routing, confidence thresholds and candidate agent selection | Accepted | AI Solution Architect | [WS-08] | 2026-08-21 |
| [ADR-D2-06](../02-application-architecture/ADR-D2-06-workflow-orchestration-engine-langgraph.md) | Workflow orchestration engine — LangGraph | Accepted | AI Solution Architect | [WS-08] | 2026-08-21 |
| [ADR-D2-07](../02-application-architecture/ADR-D2-07-graph-state-typeddict-and-pydantic-boundaries.md) | Graph state representation — TypedDict internally, Pydantic at boundaries, references not copies | Accepted | AI Solution Architect | [WS-08] | 2026-08-21 |
| [ADR-D2-08](../02-application-architecture/ADR-D2-08-execution-model-and-bounded-parallelism.md) | Sequential, parallel and hybrid execution with bounded parallelism | Accepted | AI Solution Architect | [WS-08] | 2026-08-21 |
| [ADR-D2-09](../02-application-architecture/ADR-D2-09-agent-harness-single-execution-boundary.md) | Agent Harness as the single controlled execution boundary | Accepted | AI Solution Architect | [WS-08] | 2026-08-21 |
| [ADR-D2-10](../02-application-architecture/ADR-D2-10-long-running-workflow-and-hil-resume.md) | Long-running workflow durability and human-in-the-loop suspend/resume | Accepted | AI Solution Architect | [WS-08, WS-11] | 2026-08-21 |
| [ADR-D2-11](../02-application-architecture/ADR-D2-11-idempotency-retry-timeout-loop-limits.md) | Workflow idempotency, retry, timeout and loop-limit policy | Accepted | AI Solution Architect | [WS-08] | 2026-08-21 |
| [ADR-D2-12](../02-application-architecture/ADR-D2-12-erc-as-enterprise-context-boundary.md) | ERC as the enterprise context boundary | Accepted | AI Solution Architect | [WS-09] | 2026-08-21 |
| [ADR-D2-13](../02-application-architecture/ADR-D2-13-enterprise-integration-pattern.md) | Enterprise integration pattern — API catalogue, tool registry and selective MCP | Accepted | AI Solution Architect | [WS-10] | 2026-08-21 |
| [ADR-D2-14](../02-application-architecture/ADR-D2-14-integration-matrix-and-coupling-rules.md) | Enterprise integration matrix, service ownership and coupling rules | Accepted | AI Solution Architect | [WS-10] | 2026-08-21 |
| [ADR-D2-15](../02-application-architecture/ADR-D2-15-enterprise-api-contract-and-versioning.md) | Enterprise API contract, versioning and compatibility strategy | Accepted | AI Solution Architect | [WS-10] | 2026-08-21 |
| [ADR-D2-16](../02-application-architecture/ADR-D2-16-asynchronous-eventing-azure-service-bus.md) | Asynchronous eventing platform — Azure Service Bus, consumed not produced | Accepted | AI Solution Architect | [WS-11] | 2026-08-21 |
| [ADR-D2-17](../02-application-architecture/ADR-D2-17-event-envelope-and-contract-versioning.md) | Event envelope, schema registry and event contract versioning | Accepted | AI Solution Architect | [WS-11] | 2026-08-21 |
| [ADR-D2-18](../02-application-architecture/ADR-D2-18-message-reliability-and-reconciliation.md) | Message reliability — deduplication, idempotency, dead-lettering and reconciliation | Accepted | AI Solution Architect | [WS-11] | 2026-08-21 |
| [ADR-D2-19](../02-application-architecture/ADR-D2-19-portal-link-registry-and-no-invented-urls.md) | Portal link registry and the no-invented-URL enforcement mechanism | Accepted | AI Solution Architect | [WS-10] | 2026-08-21 |

## Domain 3 — AI Architecture

| ID | Title | Status | Owner | WS | Date |
|---|---|---|---|---|---|
| [ADR-D3-01](../03-ai-architecture/ADR-D3-01-ai-capability-taxonomy.md) | AI capability taxonomy and capability-to-component mapping | Accepted | AI Solution Architect | [WS-12] | 2026-08-21 |
| [ADR-D3-02](../03-ai-architecture/ADR-D3-02-agentic-architecture-style.md) | Agentic architecture style — supervisor with workflow agents, no autonomous delegation | Accepted | AI Solution Architect | [WS-13] | 2026-08-21 |
| [ADR-D3-03](../03-ai-architecture/ADR-D3-03-agent-contract-and-lifecycle.md) | Agent contract, capability registration and lifecycle | Accepted | AI Solution Architect | [WS-13] | 2026-08-21 |
| [ADR-D3-04](../03-ai-architecture/ADR-D3-04-tool-calling-and-validation-boundary.md) | Tool-calling architecture and the tool-validation boundary | Accepted | AI Solution Architect | [WS-13] | 2026-08-21 |
| [ADR-D3-05](../03-ai-architecture/ADR-D3-05-deterministic-vs-model-decided-routing.md) | Deterministic versus model-decided routing — where each governs | Accepted | AI Solution Architect | [WS-14] | 2026-08-21 |
| [ADR-D3-06](../03-ai-architecture/ADR-D3-06-intent-classification-approach.md) | Intent classification approach and the registered intent set | Accepted | AI Solution Architect | [WS-14] | 2026-08-21 |
| [ADR-D3-07](../03-ai-architecture/ADR-D3-07-clarification-and-confirmation-strategy.md) | Clarification, disambiguation and confirmation strategy | Accepted | AI Product Owner | [WS-14] | 2026-08-21 |
| [ADR-D3-08](../03-ai-architecture/ADR-D3-08-transaction-uncertainty-conversational-policy.md) | Transaction-uncertainty and ambiguous-outcome conversational policy | Accepted | AI Product Owner | [WS-14] | 2026-08-21 |
| [ADR-D3-09](../03-ai-architecture/ADR-D3-09-layered-prompt-composition.md) | Layered prompt composition with trust-labelled content boundaries | Accepted | AI Solution Architect | [WS-15] | 2026-08-21 |
| [ADR-D3-10](../03-ai-architecture/ADR-D3-10-adam-persona-prompt-layer.md) | Adam persona prompt layer — versioned, reusable, workflow-independent | Accepted | AI Architecture Lead | [WS-15] | 2026-08-22 |
| [ADR-D3-11](../03-ai-architecture/ADR-D3-11-prompt-storage-versioning-and-promotion.md) | Prompt storage, versioning and promotion | Accepted | AI Architecture Lead | [WS-15] | 2026-08-22 |
| [ADR-D3-12](../03-ai-architecture/ADR-D3-12-prompt-injection-defence-in-prompt-layer.md) | Prompt injection defence inside the prompt layer | Accepted | Security Architect | [WS-15] | 2026-08-22 |
| [ADR-D3-13](../03-ai-architecture/ADR-D3-13-slm-strategy-hosted-first-self-hosted-target.md) | SLM strategy — Hugging Face Inference API first, self-hosted SLM as target | Accepted | AI Architecture Lead | [WS-16] | 2026-08-22 |
| [ADR-D3-14](../03-ai-architecture/ADR-D3-14-slm-provider-abstraction.md) | SLM provider abstraction and provider-neutral contract | Accepted | AI Architecture Lead | [WS-16] | 2026-08-22 |
| [ADR-D3-15](../03-ai-architecture/ADR-D3-15-model-registry.md) | Model registry — capability, purpose and status model | Accepted | AI Architecture Lead | [WS-16] | 2026-08-22 |
| [ADR-D3-16](../03-ai-architecture/ADR-D3-16-generation-parameters-and-temperature-strategy.md) | Generation parameter and temperature strategy per task class | Accepted | AI Architecture Lead | [WS-16] | 2026-08-22 |
| [ADR-D3-17](../03-ai-architecture/ADR-D3-17-structured-output-and-validation.md) | Structured output strategy and output validation | Accepted | AI Architecture Lead | [WS-16] | 2026-08-22 |
| [ADR-D3-18](../03-ai-architecture/ADR-D3-18-slm-fallback-degradation-circuit-breaking.md) | SLM fallback, degradation and circuit-breaking | Accepted | AI Architecture Lead | [WS-16] | 2026-08-22 |
| [ADR-D3-19](../03-ai-architecture/ADR-D3-19-streaming-strategy.md) | Streaming strategy and its interaction with structured output | Accepted | AI Architecture Lead | [WS-16] | 2026-08-22 |
| [ADR-D3-20](../03-ai-architecture/ADR-D3-20-rag-scope-knowledge-only.md) | RAG scope — knowledge and FAQ only, never business truth | Accepted | AI Architecture Lead | [WS-17] | 2026-08-22 |
| [ADR-D3-21](../03-ai-architecture/ADR-D3-21-document-ingestion-and-chunking-strategy.md) | Document ingestion and chunking strategy for a low-churn policy corpus | Accepted | AI Solution Architect | [WS-17] | 2026-08-21 |
| [ADR-D3-22](../03-ai-architecture/ADR-D3-22-retrieval-reranking-and-citation.md) | Retrieval, reranking and mandatory-citation policy | Accepted | AI Architecture Lead | [WS-17] | 2026-08-22 |
| [ADR-D3-23](../03-ai-architecture/ADR-D3-23-embedding-model-selection-and-re-embedding.md) | Embedding model selection, versioning and re-embedding strategy | Proposed | AI Architecture Lead | [WS-17] | 2026-08-22 |
| [ADR-D3-24](../03-ai-architecture/ADR-D3-24-vector-store-selection.md) | Vector store selection | Proposed | AI Architecture Lead | [WS-17] | 2026-08-22 |
| [ADR-D3-25](../03-ai-architecture/ADR-D3-25-context-engineering-assembly-and-budget.md) | Context engineering — assembly order, precedence and token-budget allocation | Accepted | AI Architecture Lead | [WS-18] | 2026-08-22 |

## Domain 4 — Information Architecture

| ID | Title | Status | Owner | WS | Date |
|---|---|---|---|---|---|
| [ADR-D4-01](../04-information-architecture/ADR-D4-01-four-state-separation.md) | Four-state separation — conversation / session / workflow / enterprise | Accepted | Principal Architect | [WS-19] | 2026-08-22 |
| [ADR-D4-02](../04-information-architecture/ADR-D4-02-erc-schema-identity-and-versioning.md) | ERC schema, identity and section-level versioning | Accepted | AI Architecture Lead | [WS-19] | 2026-08-22 |
| [ADR-D4-03](../04-information-architecture/ADR-D4-03-erc-provenance-freshness-authority.md) | ERC provenance, freshness policy and authority levels | Accepted | AI Architecture Lead | [WS-19] | 2026-08-22 |
| [ADR-D4-04](../04-information-architecture/ADR-D4-04-erc-collection-planning-and-batching.md) | ERC collection planning, batching and pagination safety | Accepted | AI Architecture Lead | [WS-19] | 2026-08-22 |
| [ADR-D4-05](../04-information-architecture/ADR-D4-05-erc-partial-failure-semantics.md) | ERC partial-failure semantics — mandatory vs optional, completeness tracking | Accepted | AI Architecture Lead | [WS-19] | 2026-08-22 |
| [ADR-D4-06](../04-information-architecture/ADR-D4-06-erc-invalidation-and-event-refresh.md) | ERC invalidation, patching and event-driven refresh | Accepted | AI Architecture Lead | [WS-19] | 2026-08-22 |
| [ADR-D4-07](../04-information-architecture/ADR-D4-07-data-and-knowledge-architecture.md) | Data and knowledge architecture — domains, classification and ownership | Accepted | Principal Architect | [WS-20] | 2026-08-22 |
| [ADR-D4-08](../04-information-architecture/ADR-D4-08-canonical-identifiers-and-reference-data.md) | Canonical identifier and reference-data strategy (WGS alignment) | Accepted | Principal Architect | [WS-20] | 2026-08-22 |
| [ADR-D4-09](../04-information-architecture/ADR-D4-09-metadata-response-envelope-error-codes.md) | Metadata, response envelope and error-code standards | Accepted | Backend Lead | [WS-21] | 2026-08-22 |
| [ADR-D4-10](../04-information-architecture/ADR-D4-10-session-conversation-state-store.md) | Session / conversation / memory / cache state store — Azure Managed Redis | Accepted | Principal Architect | [WS-22] | 2026-08-22 |
| [ADR-D4-11](../04-information-architecture/ADR-D4-11-memory-architecture.md) | Memory architecture — short/long-term, ranking, summarisation, retention | Accepted | AI Architecture Lead | [WS-22] | 2026-08-22 |
| [ADR-D4-12](../04-information-architecture/ADR-D4-12-cache-architecture.md) | Cache architecture — namespaces, TTL, invalidation, stampede protection | Accepted | AI Architecture Lead | [WS-22] | 2026-08-22 |

## Domain 5 — Technology Architecture

| ID | Title | Status | Owner | WS | Date |
|---|---|---|---|---|---|
| [ADR-D5-01](../05-technology-architecture/ADR-D5-01-language-and-api-framework.md) | Language and API framework — Python + FastAPI | Accepted | Principal Architect | [WS-23] | 2026-08-22 |
| [ADR-D5-02](../05-technology-architecture/ADR-D5-02-python-version-and-type-checker.md) | Python version range and primary type checker — mypy | Accepted | Backend Lead | [WS-23] | 2026-08-22 |
| [ADR-D5-03](../05-technology-architecture/ADR-D5-03-boundary-validation-pydantic.md) | Boundary validation standard — Pydantic v2 | Accepted | Backend Lead | [WS-23] | 2026-08-22 |
| [ADR-D5-04](../05-technology-architecture/ADR-D5-04-dependency-management-and-pinning.md) | Dependency management, pinning and lock-file policy | Accepted | Backend Lead | [WS-23] | 2026-08-22 |
| [ADR-D5-05](../05-technology-architecture/ADR-D5-05-lint-format-toolchain-ruff.md) | Lint/format toolchain — Ruff as the single tool | Accepted | Backend Lead | [WS-23] | 2026-08-22 |
| [ADR-D5-06](../05-technology-architecture/ADR-D5-06-configuration-and-release-manifest.md) | Configuration architecture and immutable release-manifest model | Accepted | Principal Architect | [WS-23] | 2026-08-22 |
| [ADR-D5-07](../05-technology-architecture/ADR-D5-07-secret-management-key-vault.md) | Secret management — Azure Key Vault with `*_secret_ref` indirection | Accepted | Security Architect | [WS-23] | 2026-08-22 |
| [ADR-D5-08](../05-technology-architecture/ADR-D5-08-cloud-platform-and-compute.md) | Cloud platform and compute — Azure + AKS | Accepted | Principal Architect | [WS-24] | 2026-08-22 |
| [ADR-D5-09](../05-technology-architecture/ADR-D5-09-container-image-and-acr.md) | Container image, ACR and image-immutability policy | Accepted | Platform Engineer | [WS-24] | 2026-08-22 |
| [ADR-D5-10](../05-technology-architecture/ADR-D5-10-self-hosted-slm-serving-stack.md) | Self-hosted SLM serving stack — vLLM vs TGI vs Azure ML | Proposed | AI Architecture Lead | [WS-24] | 2026-08-22 |
| [ADR-D5-11](../05-technology-architecture/ADR-D5-11-gpu-node-pool-and-workload-separation.md) | GPU node pool and CPU/GPU workload separation | Accepted | Platform Engineer | [WS-24] | 2026-08-22 |
| [ADR-D5-12](../05-technology-architecture/ADR-D5-12-iac-tool.md) | Infrastructure-as-Code tool — Terraform vs Bicep | Proposed | Platform Engineer | [WS-24] | 2026-08-22 |
| [ADR-D5-13](../05-technology-architecture/ADR-D5-13-kubernetes-manifest-tool.md) | Kubernetes manifest tool — Helm vs Kustomize | Proposed | Platform Engineer | [WS-24] | 2026-08-22 |
| [ADR-D5-14](../05-technology-architecture/ADR-D5-14-environment-model.md) | Environment model — DEV → TEST → UAT → STAGE → PROD | Accepted | Principal Architect | [WS-24] | 2026-08-22 |
| [ADR-D5-15](../05-technology-architecture/ADR-D5-15-api-gateway-and-authorization-boundary-apim.md) | API gateway and authorization boundary — APIM | Accepted | Security Architect | [WS-25] | 2026-08-22 |
| [ADR-D5-16](../05-technology-architecture/ADR-D5-16-shared-http-client-standard.md) | Shared HTTP client standard — pooling, timeout, retry, tracing | Accepted | Backend Lead | [WS-25] | 2026-08-22 |
| [ADR-D5-17](../05-technology-architecture/ADR-D5-17-scalability-and-autoscaling.md) | Scalability and autoscaling model | Accepted | SRE | [WS-26] | 2026-08-22 |
| [ADR-D5-18](../05-technology-architecture/ADR-D5-18-latency-budget-decomposition.md) | Latency budget decomposition and per-hop SLO allocation | Accepted | AI Architecture Lead | [WS-26] | 2026-08-22 |

## Domain 6 — Security & Governance

| ID | Title | Status | Owner | WS | Date |
|---|---|---|---|---|---|
| [ADR-D6-01](../06-security-governance/ADR-D6-01-zero-trust-and-trust-zones.md) | Zero-trust model and trust-zone definition | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-02](../06-security-governance/ADR-D6-02-authn-authz-boundary.md) | AuthN/AuthZ boundary — APIM validates, AI consumes claims only | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-03](../06-security-governance/ADR-D6-03-authorization-context-integrity-and-propagation.md) | Authorization context integrity and propagation through the graph | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-04](../06-security-governance/ADR-D6-04-network-segmentation-and-egress.md) | Network segmentation, private connectivity and egress control | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-05](../06-security-governance/ADR-D6-05-encryption-and-key-management.md) | Encryption in transit/at rest, key management and rotation | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-06](../06-security-governance/ADR-D6-06-data-classification-and-pii-protection.md) | Data classification, PII protection and data-flow policy | Accepted | Data Protection Officer | [WS-27] | 2026-08-22 |
| [ADR-D6-07](../06-security-governance/ADR-D6-07-external-slm-data-boundary.md) | External SLM data boundary — what may leave the tenancy | Accepted | Data Protection Officer | [WS-27] | 2026-08-22 |
| [ADR-D6-08](../06-security-governance/ADR-D6-08-prompt-injection-and-jailbreak-defence.md) | Prompt injection and jailbreak defence architecture | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-09](../06-security-governance/ADR-D6-09-guardrail-pipeline-placement.md) | Guardrail pipeline placement at six boundaries, fail-closed policy | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-10](../06-security-governance/ADR-D6-10-tool-allowlist-parameter-output-security.md) | Tool allowlist, parameter and output security | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-11](../06-security-governance/ADR-D6-11-mcp-server-trust-model.md) | MCP server trust model and response validation | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-12](../06-security-governance/ADR-D6-12-rag-acl-enforcement.md) | RAG ACL enforcement and retrieval-time authorization | Accepted | Security Architect | [WS-27] | 2026-08-22 |
| [ADR-D6-13](../06-security-governance/ADR-D6-13-responsible-ai-and-prohibited-use.md) | Responsible AI principles and prohibited-use boundary | Accepted | AI Governance Lead | [WS-28] | 2026-08-22 |
| [ADR-D6-14](../06-security-governance/ADR-D6-14-human-oversight-and-hil-governance.md) | Human oversight and HIL governance model | Accepted | AI Governance Lead | [WS-28] | 2026-08-22 |
| [ADR-D6-15](../06-security-governance/ADR-D6-15-change-governance-and-release-gates.md) | Model/prompt/index change governance and release approval gates | Accepted | AI Governance Lead | [WS-28] | 2026-08-22 |
| [ADR-D6-16](../06-security-governance/ADR-D6-16-gdpr-safeguarding-childrens-data.md) | UK GDPR, safeguarding and children's-data handling | Accepted | Data Protection Officer | [WS-29] | 2026-08-22 |
| [ADR-D6-17](../06-security-governance/ADR-D6-17-audit-logging-and-evidential-record.md) | Audit logging and evidential record model | Accepted | Security Architect | [WS-29] | 2026-08-22 |
| [ADR-D6-18](../06-security-governance/ADR-D6-18-standards-conformance.md) | Standards conformance — ISO/IEC 42001, 27001, 9001, NIST AI RMF, EU AI Act | Accepted | AI Governance Lead | [WS-30] | 2026-08-22 |

## Domain 7 — Operations

| ID | Title | Status | Owner | WS | Date |
|---|---|---|---|---|---|
| [ADR-D7-01](../07-operations/ADR-D7-01-platform-observability-stack.md) | Platform observability stack — Azure Monitor / App Insights / Log Analytics | Accepted | SRE | [WS-31] | 2026-08-22 |
| [ADR-D7-02](../07-operations/ADR-D7-02-ai-observability-langfuse.md) | AI-specific observability — Langfuse | Accepted | AI Architecture Lead | [WS-31] | 2026-08-22 |
| [ADR-D7-03](../07-operations/ADR-D7-03-correlation-id-and-trace-propagation.md) | Correlation ID and trace-propagation standard | Accepted | SRE | [WS-31] | 2026-08-22 |
| [ADR-D7-04](../07-operations/ADR-D7-04-logging-standards-and-redaction.md) | Logging standards, levels and redaction rules | Accepted | SRE | [WS-31] | 2026-08-22 |
| [ADR-D7-05](../07-operations/ADR-D7-05-error-taxonomy-and-platform-error-hierarchy.md) | Error taxonomy and the PlatformError hierarchy | Accepted | Backend Lead | [WS-31] | 2026-08-22 |
| [ADR-D7-06](../07-operations/ADR-D7-06-resilience-patterns.md) | Resilience patterns — retry, circuit breaker, bulkhead, fallback | Accepted | SRE | [WS-31] | 2026-08-22 |
| [ADR-D7-07](../07-operations/ADR-D7-07-sli-slo-and-error-budget.md) | SLI/SLO definition and error-budget policy | Accepted | SRE | [WS-31] | 2026-08-22 |
| [ADR-D7-08](../07-operations/ADR-D7-08-alerting-severity-and-escalation.md) | Alerting, severity model and on-call escalation | Accepted | SRE | [WS-31] | 2026-08-22 |
| [ADR-D7-09](../07-operations/ADR-D7-09-ci-pipeline-and-quality-gates.md) | CI pipeline design and mandatory quality gates | Accepted | Backend Lead | [WS-32] | 2026-08-22 |
| [ADR-D7-10](../07-operations/ADR-D7-10-cd-pipeline-and-deployment-strategy.md) | CD pipeline and deployment strategy — rolling updates | Accepted | SRE | [WS-32] | 2026-08-22 |
| [ADR-D7-11](../07-operations/ADR-D7-11-branching-versioning-release-train.md) | Branching, versioning and release-train model | Accepted | Release Manager | [WS-32] | 2026-08-22 |
| [ADR-D7-12](../07-operations/ADR-D7-12-ai-engineering-lifecycle-llmops.md) | AI engineering lifecycle (LLMOps) — prompt/model/index release bundles | Accepted | AI Architecture Lead | [WS-32] | 2026-08-22 |
| [ADR-D7-13](../07-operations/ADR-D7-13-evaluation-and-regression-gates.md) | Evaluation and regression gates in CI — golden datasets, LLM-as-judge | Accepted | AI Architecture Lead | [WS-32] | 2026-08-22 |
| [ADR-D7-14](../07-operations/ADR-D7-14-test-strategy-and-pyramid.md) | Test strategy and test pyramid, incl. deterministic mock SLM | Accepted | QA Lead | [WS-32] | 2026-08-22 |
| [ADR-D7-15](../07-operations/ADR-D7-15-engineering-agents-scope-and-guardrails.md) | Engineering (dev-time) agents — scope and guardrails | Accepted | AI Architecture Lead | [WS-32] | 2026-08-22 |
| [ADR-D7-16](../07-operations/ADR-D7-16-operational-support-model.md) | Operational support model, runbook ownership and service tiers | Accepted | SRE | [WS-33] | 2026-08-22 |
| [ADR-D7-17](../07-operations/ADR-D7-17-incident-management.md) | Incident management and AI-specific incident classification | Accepted | SRE | [WS-33] | 2026-08-22 |
| [ADR-D7-18](../07-operations/ADR-D7-18-disaster-recovery-and-continuity.md) | Disaster recovery, business continuity, RPO/RTO | Accepted | SRE | [WS-33] | 2026-08-22 |

## Domain 8 — Business Value & Evolution

| ID | Title | Status | Owner | WS | Date |
|---|---|---|---|---|---|
| [ADR-D8-01](../08-business-value/ADR-D8-01-cost-model-and-unit-economics.md) | Cost model and unit economics per conversation / workflow completion | Accepted | FinOps | [WS-34] | 2026-08-22 |
| [ADR-D8-02](../08-business-value/ADR-D8-02-build-vs-buy-vs-extend.md) | Build vs buy vs extend for the orchestration layer | Accepted | Principal Architect | [WS-34] | 2026-08-22 |
| [ADR-D8-03](../08-business-value/ADR-D8-03-roi-and-benefit-realisation.md) | ROI model and benefit-realisation tracking | Accepted | Product Owner | [WS-34] | 2026-08-22 |
| [ADR-D8-04](../08-business-value/ADR-D8-04-business-kpi-framework.md) | Business KPI framework and dashboard definition | Accepted | Product Owner | [WS-35] | 2026-08-22 |
| [ADR-D8-05](../08-business-value/ADR-D8-05-ai-quality-kpis.md) | AI quality KPIs — containment, deflection, accuracy, persona adherence | Accepted | AI Architecture Lead | [WS-35] | 2026-08-22 |
| [ADR-D8-06](../08-business-value/ADR-D8-06-raid-register-and-ownership.md) | RAID register and ownership | Accepted | Programme Manager | [WS-36] | 2026-08-22 |
| [ADR-D8-07](../08-business-value/ADR-D8-07-decision-register-and-traceability.md) | Decision register and end-to-end traceability model | Accepted | Principal Architect | [WS-36] | 2026-08-22 |
| [ADR-D8-08](../08-business-value/ADR-D8-08-platform-extensibility.md) | Platform extensibility — how a new agent/workflow is added | Accepted | AI Architecture Lead | [WS-37] | 2026-08-22 |
| [ADR-D8-09](../08-business-value/ADR-D8-09-multi-tenant-extensibility.md) | Multi-county / multi-tenant extensibility strategy | Accepted | Principal Architect | [WS-37] | 2026-08-22 |
| [ADR-D8-10](../08-business-value/ADR-D8-10-vendor-lock-in-and-exit-strategy.md) | Vendor lock-in, portability and exit strategy | Accepted | Principal Architect | [WS-37] | 2026-08-22 |
