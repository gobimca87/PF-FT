# PF-FT Enterprise Agentic AI Platform — Architecture

**Document ID:** PF-FT-AI-ARCHITECTURE  
**Version:** 1.0.0  
**Status:** Development Baseline  
**Runtime:** Python / FastAPI / LangGraph  
**Initial SLM:** Hugging Face API  
**Target SLM:** Internal self-hosted SLM  
**Cloud:** Microsoft Azure

---

## 1. Purpose

This document defines the target technical architecture for the PF-FT Enterprise Agentic AI Platform and Adam AI.

The platform provides a conversational experience across existing PF-FT enterprise portals, APIs, microservices, workflow engines and deterministic rule/compliance engines.

The AI platform owns conversational understanding, workflow-level agent execution, AI orchestration, Enterprise Runtime Context (ERC), knowledge retrieval, SLM interaction, memory/session/cache, guardrails, AI evaluation and AI observability.

Enterprise systems remain authoritative for authentication/authorization decisioning, deterministic business rules, enterprise workflow execution, transactions, payment, database state, scheduled workflows and post-completion HIL processes.

> **Enterprise systems decide and execute; the AI platform interprets, orchestrates, contextualizes, explains and communicates.**

---

## 2. Architectural Boundaries

### 2.1 Enterprise-owned

- Authentication and authorization decisioning
- APIM policies and claims validation
- Deterministic business and compliance rules
- Enterprise workflow engine
- Enterprise database and system of record
- Payment and transaction authority
- Scheduled/timer workflows
- Post-completion workflows
- Human approval/decision authority
- Enterprise operational notifications

### 2.2 AI-platform-owned

- FastAPI AI API boundary
- Conversation and session management
- Supervisor/routing
- Workflow-level agents
- Agent Harness
- LangGraph AI execution
- ERC construction and context engineering
- Controlled tools
- Selective MCP integration
- RAG integration
- Embedding/vector integration
- SLM abstraction
- Prompt management/versioning
- Memory/session/cache
- Input/output guardrails
- AI evaluation
- AI observability/Langfuse
- Service Bus event consumption
- Event-driven ERC refresh and workflow resume
- AI-specific resilience, testing and cost/performance controls

### 2.3 Explicit non-goals

The AI platform must not:

- Reimplement enterprise business rules.
- Access enterprise databases directly.
- Replace enterprise workflow execution.
- Implement an independent enterprise authorization engine.
- Implement enterprise scheduled processing.
- Make independent compliance/eligibility decisions.
- Treat RAG as operational truth.
- Allow the SLM unrestricted API/tool access.
- Invent portal URLs or enterprise API results.

---

## 3. High-Level Architecture

```text
                         ┌────────────────────┐
                         │       CHAT UI      │
                         └─────────┬──────────┘
                                   │ HTTPS / SSE
                         ┌─────────▼──────────┐
                         │      FastAPI       │
                         │   AI API Boundary  │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │ Conversation Mgr   │
                         │ Session / State    │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │     Supervisor     │
                         │ Workflow / Agent   │
                         │ Routing            │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │   Workflow Agent   │
                         │ e.g. Affiliation   │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │    Agent Harness   │
                         │ Security / Tools / │
                         │ ERC / Memory       │
                         └─────────┬──────────┘
                                   │
                         ┌─────────▼──────────┐
                         │     LangGraph      │
                         │   AI Execution     │
                         └─────┬────┬────┬────┘
                               │    │    │
                              ERC Tools RAG
                               │    │    │
                               │    ▼    ▼
                               │ Enterprise Knowledge
                               │ APIs
                               ▼
                         Context Assembly
                               │
                               ▼
                         ┌──────────────┐
                         │     SLM      │
                         │ HF / Internal│
                         └──────┬───────┘
                                │
                         Output Guardrails
                                │
                         Response Formatter
                                │
                              FastAPI
                                │
                              Chat UI
```

---

## 4. Request-driven Runtime

```text
Chat UI
  ↓
FastAPI
  ↓
Validated enterprise claims/context
  ↓
Conversation Manager
  ↓
Session / Workflow State
  ↓
Supervisor
  ↓
Workflow Agent
  ↓
Agent Harness
  ↓
LangGraph
  ↓
Sequential / Parallel enterprise context acquisition
  ↓
ERC
  ↓
RAG if knowledge is required
  ↓
Authorized Tool execution
  ↓
Prompt Assembly
  ↓
SLM
  ↓
Output Guardrails
  ↓
Response Formatter
  ↓
FastAPI
  ↓
Chat UI
```

FastAPI is the application entry/delivery boundary. It delegates orchestration to the AI runtime.

---

## 5. Event-driven Runtime

Long-running or externally completed activities use asynchronous continuation.

```text
Enterprise Action
      ↓
Enterprise Workflow / Database
      ↓
Outbox
      ↓
Azure Service Bus
      ↓
PF-FT Subscription
      ↓
AI Event Consumer
      ↓
Schema Validation
      ↓
Idempotency Check
      ↓
ERC Refresh / Invalidation
      ↓
Durable Workflow Lookup
      ↓
Workflow / Conversation Resume
```

FastAPI requests must not remain open while waiting for enterprise processing that can take hours or days.

---

## 6. Authentication and Authorization Boundary

Enterprise/APIM remains authoritative.

```text
Chat UI
 ↓
Enterprise Authentication
 ↓
APIM
 ↓
Token / Claims Validation
 ↓
FastAPI
 ↓
AI Runtime
```

The AI runtime consumes validated claims for workflow eligibility, tool selection, context filtering and response behavior.

The AI platform may enforce defense-in-depth controls such as tool allow-lists, context isolation and sensitive-data filtering, but these do not replace enterprise authorization.

---

## 7. FastAPI Layer

Responsibilities:

- Request validation
- API contract enforcement
- Correlation ID propagation
- Claims/context propagation
- Rate limiting where applicable
- Input guardrail entry
- AI runtime invocation
- Streaming/SSE response
- Response formatting
- API error mapping
- Health/readiness endpoints

Primary conceptual endpoint:

`POST /api/v1/chat`

FastAPI must not contain the complete agent orchestration implementation.

---

## 8. Conversation Manager

The Conversation Manager owns conversational lifecycle, not enterprise business state.

Responsibilities:

- Conversation ID
- Session ID
- Conversation history
- Session retrieval
- Current workflow reference
- Workflow instance reference
- Pending actions
- Previous execution lookup
- Resume handling
- Conversation persistence
- Context-window preparation

---

## 9. Supervisor

The Supervisor determines which workflow-level capability should handle a request.

```text
User Query
   ↓
Supervisor
   ├── Affiliation
   ├── Player Registration
   ├── Discipline
   ├── Accreditation
   ├── Insurance
   ├── Officials
   ├── League Management
   └── Approval / Reviewer
```

Responsibilities:

- Intent interpretation
- Workflow identification
- Agent routing
- Ambiguity handling
- Multi-intent detection
- Agent handoff
- Routing confidence
- Routing observability

The Supervisor does not make enterprise business decisions.

---

## 10. Workflow-level Agents

Agents represent logical business capabilities rather than enterprise microservices.

Initial logical agents:

- Affiliation Agent
- Player Registration Agent
- Discipline Agent
- Accreditation Agent
- Insurance Agent
- Officials Agent
- League Management Agent
- Approval/Reviewer Agent

A separate deployment is introduced only when justified by independent scaling, security, ownership, availability or resource requirements.

---

## 11. Agent Harness

The Agent Harness is the controlled runtime boundary around agents.

```text
Workflow Agent
      ↓
Agent Harness
      ├── Claims
      ├── Prompt / Persona
      ├── ERC
      ├── Memory
      ├── Tools
      ├── MCP
      ├── RAG
      ├── Guardrails
      ├── Retry
      ├── Timeout
      ├── Loop Limits
      ├── Token Limits
      ├── HIL
      ├── Validation
      └── Observability
      ↓
LangGraph
```

The Harness enforces deterministic execution constraints around probabilistic model behavior.

---

## 12. LangGraph

LangGraph is the AI execution graph. It supports:

- Nodes
- Edges
- State
- Conditional routing
- Sequential execution
- Parallel execution
- Hybrid execution
- Loops
- Tool execution
- Retry paths
- Validation
- Interrupts
- Resume
- Termination

Example:

```text
START
 ↓
Understand Request
 ↓
Load Session
 ↓
Determine Required Context
 ↓
Retrieve Enterprise Context
 ↓
Build ERC
 ↓
Evaluate Context
 ↓
Retrieve RAG if required
 ↓
Reason / Plan
 ↓
Execute Tool(s)
 ↓
Update ERC
 ↓
Validate
 ↓
Generate Response
 ↓
Output Guardrails
 ↓
END
```

LangGraph does not replace the enterprise workflow engine.

---

## 13. Sequential / Parallel / Hybrid Execution

### Sequential

Used where a dependency exists:

```text
Get Club → Get Application → Get Teams
```

### Parallel

Used for independent operations:

```text
              ┌→ Teams
Club Context ─┼→ Officials
              ├→ Insurance
              ├→ Products
              └→ League
```

### Hybrid

```text
Get Club
 ↓
Get Application
 ↓
 ┌→ Teams
 ├→ Officials
 ├→ Insurance
 └→ Products
      ↓
   Build ERC
      ↓
      SLM
```

Concurrency must be controlled by application/workflow logic, not arbitrarily selected by the SLM.

---

## 14. ERC Architecture

ERC is the controlled runtime context layer between enterprise systems and the SLM.

```text
Enterprise APIs
 ↓
Normalization
 ↓
Validation
 ↓
Claims/Security Filtering
 ↓
Batch Processing
 ↓
Aggregation
 ↓
Prioritization
 ↓
Context Reduction
 ↓
ERC
 ↓
Prompt Assembly
 ↓
SLM
```

ERC is not the enterprise system of record.

Relevant provenance should include:

- Source
- API
- Retrieved timestamp
- Freshness
- Authority
- Schema version
- Correlation ID
- Completeness/status

---

## 15. ERC Batching and Context Budget

Initial processing batch size: **20 records**.

Example:

```text
87 Teams
  1–20
  21–40
  41–60
  61–80
  81–87
```

The same strategy applies to 100+ officials and other large collections.

Batching is deterministic application processing. The SLM does not control pagination.

The final ERC consolidates the required results before prompt assembly.

A failed optional batch must not cause the SLM to invent missing information.

---

## 16. Enterprise API and Tool Boundary

```text
LangGraph
 ↓
Controlled Tool
 ↓
APIM
 ↓
Enterprise API
 ↓
Enterprise Service
```

API metadata must define endpoint, method, purpose, workflow, agent, tool, request/response schema, ERC mapping, error mapping, timeout, retry, idempotency, cache suitability, version, owner and security classification.

The SLM must not construct unrestricted HTTP or database access.

---

## 17. MCP

MCP is selective and must provide clear interoperability value.

It must not automatically wrap every enterprise REST API.

```text
Agent → Harness → MCP Client → MCP Server → Controlled Tool → APIM → Enterprise API
```

Tool governance, security, authorization and observability remain mandatory.

---

## 18. RAG and Embedding/Vector Platform

RAG is for knowledge such as FAQ, policy, guidance and documentation.

```text
Knowledge Source
 ↓
Ingestion
 ↓
Parsing
 ↓
Chunking
 ↓
Metadata
 ↓
Embedding
 ↓
Vector Index
 ↓
Retrieval
 ↓
Reranking
 ↓
Knowledge Context
 ↓
Prompt Assembly
```

RAG is not operational truth.

Embedding/vector capabilities are logically separated so they can have independent model, index, scaling and migration lifecycles.

---

## 19. SLM Architecture

```text
AI Runtime
   ↓
SLM Provider Interface
   ├── Hugging Face API
   └── Internal Self-Hosted SLM
```

Configuration must support provider, model, endpoint, authentication reference, context/output limits, temperature, top-p, timeout, retry, streaming, fallback and model version.

Agents must not be tightly coupled to one provider.

---

## 20. Prompt Architecture

Prompts are versioned artifacts.

Categories:

- System
- Persona
- Agent
- Workflow
- Data/context
- ERC
- Tool
- Guardrail
- Response

Typical composition:

```text
System
+ Persona
+ Workflow
+ User Query
+ Claims Context
+ Conversation Context
+ ERC
+ RAG Context
+ Tool Results
+ Output Constraints
```

Prompt changes participate in AI evaluation before promotion.

---

## 21. Memory and Cache

Separate:

```text
Conversation Memory
Session State
Workflow State
ERC Cache
API Cache
RAG Cache
Semantic Cache
SLM KV Cache
```

Transactional enterprise state must be validated through authoritative enterprise APIs/events where required, especially payment, approval, compliance, completion, official assignment and team status.

---

## 22. Guardrails

```text
User Input
 ↓
Input Guardrails
 ↓
Prompt Assembly
 ↓
SLM
 ↓
Output Guardrails
 ↓
Response
```

Execution guardrails operate around tools.

Required protections include direct/indirect prompt injection, jailbreaks, sensitive-data leakage, unauthorized tools, malicious tool arguments, context poisoning, unsupported claims, excessive loops and unsafe output.

Guardrails cannot be bypassed by agents or prompts.

---

## 23. AI Evaluation

AI evaluation is a first-class platform capability.

Evaluate:

- Intent accuracy
- Supervisor routing
- Agent selection
- Tool selection
- API selection
- Tool argument accuracy
- ERC correctness/completeness
- Groundedness
- Hallucination
- Business-rule preservation
- Prompt-injection resistance
- Authorization boundary behavior
- HIL routing
- Workflow completion
- Response quality
- Latency
- Token/context usage
- Cost

Each evaluation case can define expected intent, agent, tool, API, ERC, response, forbidden behavior and expected guardrail behavior.

Material prompt/model/agent/workflow changes require regression evaluation.

---

## 24. Service Bus Event Architecture

```text
Enterprise Transaction
 ↓
Enterprise Database / Workflow
 ↓
Outbox
 ↓
Azure Service Bus
 ↓
PF-FT Subscription
 ↓
AI Event Consumer
 ↓
Schema Validation
 ↓
Idempotency
 ↓
ERC Refresh / Invalidation
 ↓
Durable Workflow Lookup
 ↓
Workflow Resume
```

Event metadata should include event ID, type, version, timestamp, correlation ID, causation ID, entity ID, workflow ID and payload.

---

## 25. Long-running and HIL Execution

The platform must support durable execution across external actions.

```text
AI
 ↓
WAITING_FOR_EXTERNAL_ACTION / WAITING_FOR_HUMAN
 ↓
Enterprise Portal / HIL
 ↓
Enterprise Decision / State Change
 ↓
Service Bus Event
 ↓
ERC Refresh
 ↓
AI Resume
```

The AI platform participates in HIL but does not own the enterprise decision.

Scheduled enterprise workflows and post-completion workflows remain outside the AI platform.

---

## 26. State Domains

The platform separates:

1. **Conversation State** — what the user is discussing.
2. **Session State** — session lifecycle and identity reference.
3. **AI Execution State** — what the runtime is doing.
4. **Workflow Agent State** — current LangGraph/agent position.
5. **Enterprise Business State** — authoritative enterprise state.
6. **ERC** — derived runtime context.
7. **Event State** — event processing/correlation state.

These states must not be conflated.

---

## 27. Error and Resilience

### Business outcomes

Examples: compliance failed, CFA review required, payment required, team not eligible, application rejected. These are valid enterprise outcomes, not technical exceptions.

### Technical failures

Examples: API timeout/5xx, service unavailable, SLM unavailable, RAG unavailable, Service Bus failure.

Required resilience mechanisms:

- Timeout
- Retry
- Circuit breaker
- Idempotency
- Graceful degradation
- Fallback
- DLQ
- Replay
- Resume

A transaction timeout must not cause an uncontrolled duplicate transaction.

---

## 28. Observability

Use Azure Monitor, Application Insights, Log Analytics and Langfuse.

Trace chain:

```text
Conversation ID
 ↓
Workflow ID
 ↓
Agent Run ID
 ↓
LangGraph Run
 ↓
Tool Request ID
 ↓
API Correlation ID
 ↓
Service Bus Message ID
 ↓
ERC Refresh
```

Monitor latency, throughput, tool/API calls, ERC build time, SLM inference, tokens/context, retries, errors, workflow duration, GPU/VRAM, evaluation quality and cost.

Sensitive data must be redacted according to security requirements.

---

## 29. Performance and Cost

Performance requirements include concurrent conversations, async I/O, parallel enterprise calls, bounded ERC processing, streaming, SLM concurrency, CPU/GPU scaling, connection pooling and backpressure.

Measure:

- End-to-end latency
- Requests/sec
- Tokens/sec
- Concurrent inference
- GPU/VRAM
- KV cache
- Replica count
- Cost/request
- Cost/workflow

Optimize through context reduction, ERC reuse, safe caching, batch processing, model routing, prompt optimization, retrieval filtering, token limits and GPU utilization.

---

## 30. Configuration and Versioning

### Code

Git/package versioning.

### YAML

Structured metadata/configuration for prompts, agent metadata, workflow metadata, tool registry, API catalog, portal links, MCP metadata, model metadata and evaluation configuration.

### Environment variables

Environment-specific runtime values.

### Key Vault

Secrets.

Version independently where lifecycle requires it:

- Platform
- Application
- Agent
- Workflow
- Prompt
- Tool
- API
- ERC schema
- Event schema
- Model
- Embedding model

`VERSION.yaml` is a platform manifest; it does not replace Git, API or package versioning.

---

## 31. Security Principles

1. No direct database access from the AI runtime.
2. Enterprise/APIM authorization remains authoritative.
3. Least privilege for tools.
4. Secrets outside source control.
5. Managed identity where applicable.
6. Input/output guardrails.
7. Sensitive context filtering.
8. Prompt-injection protection.
9. Tool-action auditing.
10. Model/prompt/version traceability.
11. Security scanning in CI/CD.
12. Environment isolation.

---

## 32. Testing Architecture

```text
Unit
 ↓
Component
 ↓
API
 ↓
Integration
 ↓
Tool
 ↓
Agent
 ↓
Workflow
 ↓
RAG
 ↓
Security
 ↓
AI Evaluation
 ↓
Performance
 ↓
End-to-End
```

Traditional code coverage is necessary but insufficient for AI quality.

---

## 33. Engineering Support Agents

Engineering agents may include:

- Unit Test Agent
- Code Review Agent
- Security Scan Agent
- Prompt Review Agent
- Evaluation Agent
- Documentation Agent
- Dependency/Vulnerability Agent

These are engineering governance capabilities, not production business agents. Deterministic CI/CD gates and human review remain authoritative.

---

## 34. Deployment Architecture

Target Azure components:

```text
Azure
 ├── AKS
 │    ├── AI Runtime CPU workloads
 │    └── SLM GPU workloads
 ├── APIM
 ├── Service Bus
 ├── Key Vault
 ├── Azure Monitor
 ├── Application Insights
 ├── RAG / Vector Platform
 └── Cache / Session Services
```

CPU and GPU workloads should scale independently where justified. Private networking and enterprise security controls are applied according to environment requirements.

---

## 35. Environment Architecture

```text
LOCAL → DEV → TEST → QA → STAGING → PROD
```

Environment-specific resources and values must be isolated for enterprise APIs, Service Bus, SLM, Langfuse, RAG/vector, cache, prompts, feature flags and secrets.

---

## 36. Data and Provenance

Three categories remain distinct:

### Operational truth
Enterprise APIs and systems.

### Runtime context
ERC.

### Knowledge
RAG/vector platform.

Important ERC values should retain source, API, retrieved time, freshness, authority, schema version and correlation ID where practical.

---

## 37. Club Affiliation Reference Architecture

The supplied Affiliation E2E flow is the first concrete business reference.

```text
User
 ↓
Affiliation Agent
 ↓
Agent Harness
 ↓
LangGraph
 ↓
Retrieve club/application context
 ↓
Sequential / Parallel enterprise API calls
 ↓
20-record batching for large collections
 ↓
ERC construction
 ↓
RAG when policy/knowledge is required
 ↓
SLM reasoning/explanation
 ↓
Authorized tool execution
 ↓
Enterprise API
 ↓
Enterprise workflow/business rules
 ↓
Result/Event
 ↓
ERC refresh
 ↓
Response / Resume
```

Enterprise affiliation statuses, business rules, CFA/HIL decisions, scheduled processing and post-completion workflows remain enterprise-owned.

---

## 38. Non-Functional Requirements

The platform must support:

- Availability
- Reliability
- Scalability
- Performance
- Security
- Observability
- Maintainability
- Testability
- Versionability
- Recoverability
- Cost control

Detailed targets will be defined in the NFR and performance documents.

---

## 39. Architecture Success Criteria

The architecture is successful when:

1. Chat UI invokes the AI platform through FastAPI.
2. Supervisor routes to the correct workflow agent.
3. Agent Harness controls execution.
4. LangGraph supports sequential and parallel AI execution.
5. ERC aggregates multiple enterprise APIs.
6. ERC supports 20-record batching.
7. Tools safely invoke enterprise APIs.
8. RAG provides knowledge without replacing operational truth.
9. SLM provider can change without rewriting agents.
10. Prompts are versioned and evaluated.
11. Guardrails prevent injection and unauthorized behavior.
12. Service Bus events refresh ERC and resume workflows.
13. Long-running workflows survive request termination.
14. AI executions are traceable.
15. AI evaluation detects regressions.
16. Security and automated testing run in CI/CD.
17. Enterprise authorization remains authoritative.
18. Enterprise workflow remains authoritative.
19. Enterprise scheduled workflows remain outside the AI platform.
20. New workflow-level agents can be added without redesigning the platform core.

---

## 40. Architecture Governance

ADF/ADR remains the external architecture governance mechanism. The runtime project does not require an ADR folder.

Changes affecting enterprise/AI boundaries, agent model, LangGraph execution, ERC, security, SLM, tools, events, state, data ownership or AI evaluation gates must follow the agreed architecture governance process.

---

## 41. Related Detailed Documents

This document is the parent architecture for:

- `PF-FT-AI-PLATFORM-OVERVIEW.md`
- `PF-FT-AI-RESPONSIBILITY-MATRIX.md`
- `PF-FT-AI-RUNTIME.md`
- `PF-FT-CONVERSATION-SESSION-MANAGEMENT.md`
- `PF-FT-SUPERVISOR-ARCHITECTURE.md`
- `PF-FT-AGENT-ARCHITECTURE.md`
- `PF-FT-AGENT-HARNESS.md`
- `PF-FT-LANGGRAPH-WORKFLOW.md`
- `PF-FT-ERC-ARCHITECTURE.md`
- `PF-FT-ERC-BATCHING-AND-CONTEXT-BUDGET.md`
- `PF-FT-MEMORY-SESSION-CACHE.md`
- `PF-FT-ENTERPRISE-API-INTEGRATION.md`
- `PF-FT-TOOL-ARCHITECTURE.md`
- `PF-FT-MCP-ARCHITECTURE.md`
- `PF-FT-SERVICE-BUS-EVENT-ARCHITECTURE.md`
- `PF-FT-RAG-ARCHITECTURE.md`
- `PF-FT-EMBEDDING-VECTOR-PLATFORM.md`
- `PF-FT-SLM-ARCHITECTURE.md`
- `PF-FT-PROMPT-ENGINEERING-AND-VERSIONING.md`
- `PF-FT-CONFIGURATION-AND-VERSIONING.md`
- `PF-FT-AI-GUARDRAILS.md`
- `PF-FT-AI-SECURITY.md`
- `PF-FT-AI-EVALUATION.md`
- `PF-FT-TESTING-STRATEGY.md`
- `PF-FT-AI-OBSERVABILITY.md`
- `PF-FT-LANGFUSE.md`
- `PF-FT-ERROR-AND-RESILIENCE.md`
- `PF-FT-PERFORMANCE-AND-COST.md`
- `PF-FT-INFRASTRUCTURE.md`
- `PF-FT-CI-CD-DEVOPS.md`
- `PF-FT-DISASTER-RECOVERY.md`
- `PF-FT-PRODUCTION-READINESS.md`

These documents elaborate this architecture and must not introduce contradictory ownership boundaries.
