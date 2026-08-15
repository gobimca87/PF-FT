# PF-FT Enterprise Agentic AI Platform — Enterprise Integration

**Document ID:** PF-FT-AI-ENTERPRISE-INTEGRATION  
**Phase:** Phase 2 — Enterprise Integration & Tooling  
**Version:** 1.0.0  
**Status:** Development Baseline  
**Platform:** PF-FT Enterprise Agentic AI Platform / Adam AI  
**Runtime:** Python / FastAPI / LangGraph  
**Primary Scope:** Enterprise APIs, API Catalog, API Contracts, Tool Abstraction, Tool Executor, MCP, Authorization Boundary, Request/Response Transformation, Idempotency, Retry, Sequential/Parallel Execution

---

# 1. Purpose

This document defines the enterprise integration architecture for the PF-FT Enterprise Agentic AI Platform.

The AI platform does not directly own enterprise business data or business rules.

It interacts with the existing PF-FT enterprise ecosystem through controlled integration capabilities:

```text
AI Platform
    │
    ▼
Integration Boundary
    │
    ├── Enterprise APIs
    ├── Tools
    └── MCP
    │
    ▼
Enterprise Application / Services
```

This document defines:

- Enterprise API catalog
- API ownership
- API discovery
- API metadata
- API contracts
- Request contracts
- Response contracts
- Response-to-context mapping
- Tool abstraction
- Tool registry
- Tool executor
- MCP architecture
- MCP client configuration
- MCP server configuration
- MCP resources
- MCP tools
- MCP prompts where applicable
- Authorization boundary
- Claims propagation
- Request construction
- Response transformation
- Error transformation
- Idempotency
- Retry
- Timeout
- Circuit protection
- Sequential execution
- Parallel execution
- Bounded concurrency
- API dependency graph
- Tool execution policy
- Enterprise API versioning
- Contract testing
- Security
- Observability
- Evaluation
- Unit testing
- Integration testing
- Failure handling
- Configuration
- Environment separation

---

# 2. Core Principle

> **The AI platform can orchestrate enterprise capabilities, but it must not redefine enterprise business authority.**

The authoritative boundary remains:

```text
Enterprise Systems
       │
       ▼
Enterprise APIs / Enterprise Events
       │
       ▼
AI Integration Boundary
       │
       ▼
AI Orchestration
```

AI may determine:

```text
which capability is required
when it is required
which approved API/tool should be called
which calls can run in parallel
which calls must run sequentially
```

AI must not invent:

```text
enterprise endpoint
business rule
authorization permission
enterprise status
transaction result
```

---

# 3. Enterprise Integration Position in the Platform

```text
Chat UI
   │
   ▼
FastAPI
   │
   ▼
Supervisor / LangGraph
   │
   ▼
Agent Harness
   │
   ▼
Tool Selection
   │
   ▼
Tool Executor
   │
   ├───────────────┐
   ▼               ▼
Enterprise API    MCP
   │               │
   └───────┬───────┘
           ▼
Enterprise Systems
```

---

# 4. API vs Tool vs MCP

These concepts must remain distinct.

| Concept | Purpose |
|---|---|
| Enterprise API | Existing authoritative enterprise interface |
| Tool | Controlled capability exposed to an agent |
| Tool Executor | Runtime component that safely executes an approved tool |
| MCP | Standard protocol/interface for exposing tools/resources to AI applications |
| MCP Server | Exposes approved capabilities/resources |
| MCP Client | Connects the AI platform to an MCP server |

---

# 5. Enterprise API

An Enterprise API is an existing PF-FT application/service endpoint.

Examples:

```text
Get Club
Get Affiliation
Get Teams
Get Officials
Get Courses
Get Compliance
Update Application
```

The API remains owned by the enterprise application.

---

# 6. Enterprise API Authority

The AI platform must not become the authoritative owner of:

```text
Club data
Team data
Official data
Course data
Application status
Compliance rules
Workflow rules
Transaction state
```

It consumes these through approved enterprise interfaces.

---

# 7. API Catalog

The platform requires a controlled API catalog.

Recommended logical location:

```text
config/
└── enterprise/
    └── api-catalog/
        ├── clubs.yaml
        ├── affiliations.yaml
        ├── teams.yaml
        ├── officials.yaml
        ├── courses.yaml
        └── compliance.yaml
```

The exact repository structure will be finalized with the overall platform structure.

---

# 8. API Catalog Purpose

The API catalog answers:

```text
What API exists?
Why does it exist?
Who owns it?
When should it be used?
What does it require?
What does it return?
Is it read or write?
Can it run in parallel?
What are its dependencies?
What authorization is required?
What errors can occur?
```

---

# 9. API Catalog Metadata

Example:

```yaml
api_id: enterprise.club.get
name: Get Club
version: v1
owner: club-service
description: Retrieve club information
operation: READ
```

---

# 10. API Catalog Extended Metadata

Recommended:

```yaml
api:
  api_id: enterprise.club.get
  name: Get Club
  version: v1
  owner: club-service
  domain: club
  operation: READ

  description: Retrieve club information

  endpoint:
    method: GET
    path: /api/v1/clubs/{clubId}

  authorization:
    required: true
    claims:
      - club.read

  execution:
    idempotent: true
    retryable: true
    parallelizable: true
```

---

# 11. API Purpose

Every API must explicitly define:

```yaml
purpose:
  why: "Retrieve authoritative club information"
  where_used:
    - affiliation_context
    - club_summary
    - club_validation
```

This prevents agents from selecting APIs based only on endpoint names.

---

# 12. API Usage Rules

The catalog should specify:

```text
Allowed workflows
Allowed agents
Allowed operation
Required claims
Required parameters
Required context
Forbidden usage
```

---

# 13. API Ownership

Every API must have an owner.

```yaml
owner:
  team: Club Platform
  service: Club Service
  contact: enterprise-owner-reference
```

The AI platform should not assume ownership of enterprise APIs.

---

# 14. API Lifecycle

Recommended:

```text
DISCOVERED
    ↓
REGISTERED
    ↓
VALIDATED
    ↓
ACTIVE
    ↓
DEPRECATED
    ↓
RETIRED
```

Only `ACTIVE` APIs should normally be available for runtime tool execution.

---

# 15. API Versioning

API versions must be explicit.

Example:

```text
/api/v1/clubs
/api/v2/clubs
```

The AI platform must pin the API version used by a tool.

Do not allow an LLM to dynamically switch enterprise API versions.

---

# 16. API Contract

Every registered API requires a contract.

Contract includes:

```text
HTTP method
Endpoint
Path parameters
Query parameters
Headers
Request body
Response body
Status codes
Error payload
Authentication requirements
Authorization requirements
Timeout
Retry policy
Idempotency
Pagination
Rate limits
```

---

# 17. Request Contract

Example:

```yaml
request:
  path:
    clubId:
      type: string
      required: true

  headers:
    Authorization:
      source: request_context

  query: {}

  body: null
```

---

# 18. Request Payload

The platform should maintain a version-controlled example:

```json
{
  "clubId": "club-123"
}
```

Request examples must never contain real production secrets.

---

# 19. Response Contract

Example:

```yaml
response:
  status: 200

  body:
    type: object
    required:
      - clubId
      - clubName
      - status
```

---

# 20. Response Payload

Example:

```json
{
  "clubId": "club-123",
  "clubName": "Example FC",
  "status": "ACTIVE"
}
```

---

# 21. Response-to-Context Mapping

Enterprise payloads must be transformed into platform context models.

Example:

```yaml
mapping:
  clubId: club.id
  clubName: club.name
  status: club.status
```

This mapping must be deterministic.

---

# 22. Why Mapping Must Be Deterministic

The SLM should not decide:

```text
which enterprise field means club ID
which status value means active
which response field should be trusted
```

These mappings belong to application code/configuration.

---

# 23. API Data Transformation

```text
Enterprise Response
       │
       ▼
Schema Validation
       │
       ▼
Mapping
       │
       ▼
Normalized Model
       │
       ▼
ERC / Context
```

---

# 24. Raw Response Handling

Raw enterprise responses should be retained only where necessary for:

- Debugging
- Audit
- Evaluation
- Contract validation

They should not automatically be placed into the SLM prompt.

---

# 25. Tool Abstraction

Agents should not directly call HTTP clients.

Instead:

```text
Agent
  │
  ▼
Tool
  │
  ▼
Tool Executor
  │
  ▼
Enterprise API
```

---

# 26. Tool Definition

A tool represents an approved capability.

Example:

```yaml
tool_id: club.get
name: Get Club
description: Retrieve the current club profile
```

---

# 27. Tool Contract

Example:

```yaml
tool:
  tool_id: club.get
  version: 1.0.0

  input:
    schema: ClubGetRequest

  output:
    schema: ClubContext

  source:
    type: enterprise_api
    api_id: enterprise.club.get
```

---

# 28. Tool Registry

Recommended:

```text
tool_registry/
├── club/
│   └── get.yaml
├── affiliation/
│   └── get.yaml
├── team/
│   └── list.yaml
├── official/
│   └── list.yaml
└── compliance/
    └── get.yaml
```

---

# 29. Tool Registry Responsibilities

The registry defines:

```text
Tool identity
Tool version
Purpose
Input schema
Output schema
Source
Authorization requirements
Execution policy
Retry policy
Timeout
Idempotency
Parallelization
Allowed agents
```

---

# 30. Tool Selection

The LLM may identify that a capability is required.

However:

```text
LLM selects from registered tools
```

not:

```text
LLM invents arbitrary API
```

---

# 31. Tool Selection Boundary

```text
User Request
    │
    ▼
Agent
    │
    ▼
Candidate Tool
    │
    ▼
Tool Registry
    │
    ▼
Policy Validation
    │
    ▼
Tool Executor
```

---

# 32. Tool Executor

The Tool Executor is the controlled runtime boundary.

Responsibilities:

- Validate tool
- Validate input
- Validate claims
- Validate authorization context
- Validate execution policy
- Construct request
- Invoke API/MCP
- Handle timeout
- Handle retry
- Transform response
- Record telemetry
- Return typed result

---

# 33. Tool Executor Must Not

The Tool Executor must not:

- Invent endpoint URLs
- Invent request fields
- Bypass authorization
- Modify claims
- Ignore tool policy
- Retry non-retryable transactions
- Convert unknown status to success
- Hide enterprise errors

---

# 34. Tool Execution Lifecycle

```text
TOOL_REQUESTED
      ↓
TOOL_RESOLVED
      ↓
INPUT_VALIDATED
      ↓
AUTHORIZATION_CHECKED
      ↓
EXECUTING
      ↓
RESPONSE_RECEIVED
      ↓
RESPONSE_VALIDATED
      ↓
RESPONSE_TRANSFORMED
      ↓
TOOL_COMPLETED
```

Failure states:

```text
REJECTED
TIMEOUT
RETRYING
FAILED
UNKNOWN
```

---

# 35. Tool Input Validation

Validate:

```text
Required fields
Types
Enums
Length
Format
Allowed values
Entity ownership
```

---

# 36. Tool Output Validation

Validate:

```text
HTTP status
Response schema
Required fields
Data types
Business identifiers
Pagination
Error contract
```

---

# 37. Tool Result Contract

The tool should return a normalized result.

Example:

```yaml
tool_result:
  tool_id: club.get
  status: SUCCESS
  data:
    club:
      id: club-123
      name: Example FC
      status: ACTIVE

  provenance:
    api_id: enterprise.club.get
    retrieved_at: "..."
```

---

# 38. Tool Error Contract

Example:

```yaml
tool_result:
  status: FAILED
  error:
    code: ENTERPRISE_API_TIMEOUT
    retryable: true
    source: enterprise.club.get
```

---

# 39. Error Translation

Enterprise-specific errors should be translated into stable platform error categories.

Example:

```text
HTTP 503
 ↓
ENTERPRISE_SERVICE_UNAVAILABLE
```

But the original source information should remain available for diagnostics.

---

# 40. Error Categories

Recommended:

```text
VALIDATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
RATE_LIMITED
TIMEOUT
SERVICE_UNAVAILABLE
BAD_GATEWAY
SCHEMA_ERROR
DEPENDENCY_ERROR
UNKNOWN
```

---

# 41. Retry Policy

Retry only when:

```text
Error is retryable
+
Operation is safe to retry
+
Retry count remains within limit
```

---

# 42. Retryable Examples

Potentially retryable:

```text
Timeout
503
Transient network error
429
Temporary dependency failure
```

Actual behavior must follow enterprise API contracts.

---

# 43. Non-Retryable Examples

Normally do not retry:

```text
400
401
403
404
Business validation failure
Known business rule rejection
Invalid payload
```

---

# 44. Retry Configuration

Example:

```yaml
retry:
  max_attempts: 3
  backoff:
    type: exponential
    initial_ms: 250
    max_ms: 5000
  jitter: true
```

These values are configuration examples.

---

# 45. Idempotency

Idempotency is critical for write operations.

Example:

```text
Create/Submit
 ↓
Timeout
 ↓
Did enterprise process it?
```

The AI platform must not blindly repeat the transaction.

---

# 46. Idempotency Key

For supported operations:

```yaml
idempotency:
  enabled: true
  key_source: workflow_instance_id + operation_id
```

The exact enterprise contract determines implementation.

---

# 47. Idempotency Lifecycle

```text
Generate Key
    ↓
Send Request
    ↓
Timeout
    ↓
Verify Transaction State
    ↓
Retry only if safe
```

---

# 48. Unknown Transaction State

If a write operation times out:

```text
SUCCESS?
UNKNOWN?
FAILED?
```

Do not convert:

```text
UNKNOWN → FAILED
```

or:

```text
UNKNOWN → SUCCESS
```

without verification.

---

# 49. Transaction Verification

Where possible:

```text
Write API
 ↓
Timeout
 ↓
Status/Get API
 ↓
Determine actual state
```

---

# 50. Sequential API Execution

Some API calls have dependencies.

Example:

```text
Get Club
   ↓
Get Application
   ↓
Get Teams
```

The runtime must execute these sequentially.

---

# 51. Parallel API Execution

Independent calls may execute in parallel.

Example:

```text
Get Club
   │
   ▼
Identifiers available
   │
   ├── Get Teams
   ├── Get Officials
   ├── Get Courses
   └── Get Compliance
```

---

# 52. API Dependency Graph

Maintain dependency metadata.

Example:

```yaml
dependencies:
  enterprise.application.get:
    requires:
      - enterprise.club.get

  enterprise.team.list:
    requires:
      - enterprise.club.get

  enterprise.official.list:
    requires:
      - enterprise.club.get
```

---

# 53. Execution Planner

The planner converts dependencies into an execution plan.

Example:

```yaml
execution_plan:
  step_1:
    mode: sequential
    tools:
      - club.get

  step_2:
    mode: parallel
    tools:
      - application.get
      - team.list
      - official.list
      - course.list
```

---

# 54. Fan-Out / Fan-In

```text
              ┌── Team API
              │
Context ──────┼── Official API
              │
              ├── Course API
              │
              └── Compliance API
                     │
                     ▼
                  Fan-In
                     │
                     ▼
                    ERC
```

---

# 55. Bounded Parallelism

Do not execute unlimited enterprise API calls.

Example:

```yaml
execution:
  max_parallel_tools: 5
```

This must respect APIM/API rate limits.

---

# 56. Parallel Failure Handling

Example:

```text
Teams       → SUCCESS
Officials   → SUCCESS
Courses     → TIMEOUT
Compliance  → SUCCESS
```

The workflow should retain:

```text
success results
+
failed dependency
+
retryability
+
completeness impact
```

---

# 57. Tool Dependency Failure

If:

```text
Club API fails
```

and:

```text
Teams API requires Club ID
```

then Teams cannot execute.

The planner should mark:

```text
BLOCKED_BY_DEPENDENCY
```

rather than attempting an invalid call.

---

# 58. API Pagination

Enterprise collection APIs may return:

```text
100+ teams
100+ officials
```

The tool executor must support:

```text
page
page_size
continuation_token
next_link
```

as defined by the API contract.

---

# 59. Pagination and Batching

The execution order is:

```text
API
 ↓
Pagination
 ↓
Full/controlled collection
 ↓
Batching
 ↓
Normalization
 ↓
ERC aggregation
```

or an equivalent streaming strategy when supported.

---

# 60. Streaming Collection

For very large datasets, the platform may process pages/batches incrementally.

Example:

```text
Page 1
 ↓
Batch 1
 ↓
Normalize
 ↓
Aggregate

Page 2
 ↓
Batch 2
 ↓
Normalize
 ↓
Aggregate
```

This avoids unnecessary memory growth.

---

# 61. MCP Architecture

MCP is an integration protocol, not a replacement for enterprise APIs.

Conceptually:

```text
AI Platform
    │
    ▼
MCP Client
    │
    ▼
MCP Server
    │
    ▼
Enterprise Capability
```

---

# 62. MCP Use Cases

MCP may expose:

```text
Tools
Resources
Prompts
```

where useful.

The PF-FT platform should only expose approved capabilities.

---

# 63. MCP Client

The AI platform may act as an MCP client to connect to approved MCP servers.

Responsibilities:

```text
Discover approved capabilities
Validate server identity
Apply policy
Invoke approved tools/resources
Handle errors
Capture telemetry
```

---

# 64. MCP Server

An MCP server may expose:

```text
Enterprise tools
Enterprise resources
Approved knowledge/resources
```

It should remain behind the enterprise security boundary.

---

# 65. MCP Server Rule

Do not expose unrestricted enterprise access through MCP.

Only explicitly registered capabilities should be available.

---

# 66. MCP Configuration

Example:

```yaml
mcp:
  servers:
    enterprise-club:
      enabled: true
      transport: configured
      endpoint: ${MCP_CLUB_ENDPOINT}
      authentication:
        type: configured
```

Secrets must come from approved secret/configuration infrastructure.

---

# 67. MCP Capability Registry

Example:

```yaml
server: enterprise-club

tools:
  - club.get
  - club.search

resources:
  - club.profile
```

---

# 68. MCP Tool Governance

Every MCP tool should have:

```text
Tool ID
Version
Description
Input schema
Output schema
Authorization
Allowed agents
Risk classification
Timeout
Retry policy
Audit policy
```

---

# 69. MCP Resource Governance

Resources must define:

```text
Resource ID
URI pattern
Owner
Classification
Authorization
Freshness
Allowed consumers
```

---

# 70. MCP Security

Validate:

```text
Server identity
Transport security
Authentication
Authorization
Tenant isolation
Tool allowlist
Resource allowlist
Input schema
Output schema
```

---

# 71. MCP Prompt Injection

MCP resources may contain untrusted content.

Treat resource content as:

```text
DATA
```

not:

```text
SYSTEM INSTRUCTION
```

---

# 72. Authorization Boundary

The existing enterprise/APIM layer remains responsible for authentication/authorization policy as agreed for PF-FT.

The AI API receives validated claims/context.

Conceptually:

```text
Chat UI
   │
   ▼
Enterprise/APIM
   │
   ├── Authentication
   ├── Authorization
   └── Claims
        │
        ▼
AI FastAPI
        │
        ▼
AI Context
```

---

# 73. Claims Context

Example:

```yaml
auth_context:
  subject: user-123
  tenant: tenant-1
  organization: club-123
  claims:
    - affiliation.read
    - team.read
```

The AI platform should use the claims to enforce integration boundaries.

---

# 74. Claims Must Not Be Modified

The AI runtime must not:

```text
Add claim
Remove claim
Elevate role
Impersonate user
```

It may propagate validated claims to downstream integrations according to the enterprise integration contract.

---

# 75. Tool Authorization

Before execution:

```text
Tool Requested
      ↓
Tool Registry
      ↓
Required Claim
      ↓
Request Claims
      ↓
Allowed?
 ├── YES → Execute
 └── NO → Reject
```

---

# 76. Authorization Failure

Return a controlled result:

```yaml
status: REJECTED
error:
  code: AUTHORIZATION_ERROR
  reason: TOOL_NOT_PERMITTED
```

Do not attempt alternate unauthorized tools.

---

# 77. Tenant Isolation

Every integration request should carry the appropriate tenant/organization context.

Never derive tenant context from untrusted user text.

---

# 78. Organization/Club Isolation

Where applicable:

```text
Claimed organization
+
Requested entity
```

must be validated before enterprise execution.

---

# 79. Input Security

Tool inputs must be validated against schemas before they reach enterprise APIs.

Protect against:

```text
Injection
Malformed identifiers
Path traversal
Oversized payloads
Unexpected query operators
Unsafe URLs
```

---

# 80. URL Security

Enterprise endpoint URLs must come from configuration/catalog.

Never allow:

```text
LLM-generated arbitrary URL
```

to become an HTTP request target.

---

# 81. HTTP Client Boundary

Use a centralized enterprise HTTP client abstraction.

Example:

```python
class EnterpriseHttpClient:
    async def request(
        self,
        method,
        api_definition,
        request_context
    ):
        ...
```

This centralizes:

```text
Auth
Timeout
Retry
Telemetry
Headers
Correlation IDs
Error handling
```

---

# 82. API Client Factory

Example:

```python
class EnterpriseClientFactory:
    def get_client(self, api_id: str):
        ...
```

The factory resolves only registered API definitions.

---

# 83. Header Propagation

Controlled headers may include:

```text
Correlation ID
Trace ID
Tenant context
User context
Authorization context
Idempotency key
API version
```

Do not blindly forward every incoming header.

---

# 84. Correlation ID

Every tool execution should have:

```text
correlation_id
trace_id
workflow_instance_id
agent_run_id
tool_call_id
```

---

# 85. Request Context

Example:

```yaml
request_context:
  correlation_id: corr-123
  trace_id: trace-123
  workflow_instance_id: wf-123
  agent_run_id: run-123
  user_id: user-123
  organization_id: club-123
```

---

# 86. Timeout Policy

Every API/tool should have an explicit timeout.

Example:

```yaml
timeout:
  connect_ms: 1000
  read_ms: 10000
  total_ms: 12000
```

Actual values depend on enterprise SLA.

---

# 87. Timeout Hierarchy

The runtime should enforce:

```text
Request timeout
   >
Workflow timeout
   >
Tool timeout
```

Individual tool calls must not exceed the remaining workflow/request budget.

---

# 88. Retry Budget

Retries consume latency.

The runtime must calculate:

```text
remaining workflow time
```

before retrying.

---

# 89. Rate Limit Handling

If enterprise/APIM returns:

```text
429
```

the executor should respect:

```text
Retry-After
```

when available.

Use bounded retries.

---

# 90. Circuit Protection

Repeated enterprise failures may require circuit protection.

Conceptually:

```text
Healthy
 ↓
Failures
 ↓
OPEN
 ↓
Cooldown
 ↓
HALF_OPEN
 ↓
Healthy
```

The exact implementation is infrastructure/configuration dependent.

---

# 91. Bulkhead Protection

Separate concurrency budgets may be configured for:

```text
Club APIs
Team APIs
Official APIs
Compliance APIs
MCP servers
```

This prevents one dependency from consuming the entire runtime capacity.

---

# 92. API Concurrency

Example:

```yaml
concurrency:
  global_max: 20

  enterprise:
    max_parallel: 10

  mcp:
    max_parallel: 5
```

---

# 93. API Sequencing in ERC Construction

For the affiliation workflow:

```text
Get Club
   ↓
Get Application
   ↓
Obtain required identifiers
   ↓
Parallel:
 ├── Teams
 ├── Officials
 ├── Courses
 └── Compliance
   ↓
ERC
```

Actual dependencies must be defined by the API catalog.

---

# 94. API Calls and LangGraph

LangGraph nodes should request capabilities rather than construct raw HTTP calls.

```text
Graph Node
   ↓
Tool Request
   ↓
Tool Registry
   ↓
Tool Executor
   ↓
Enterprise API
```

This keeps orchestration separate from infrastructure.

---

# 95. Tool Calls in Graph State

Store references/results, not unnecessary raw payloads.

Example:

```yaml
tool_results:
  - tool_call_id: tc-123
    tool_id: team.list
    status: SUCCESS
    result_ref: result-123
```

---

# 96. Large API Results

Large API results should flow into:

```text
ERC collection
```

rather than being copied repeatedly through every graph node.

---

# 97. API Result Storage

Where required:

```text
Tool Result
 ↓
Result Store
 ↓
Reference
 ↓
ERC / Graph State
```

This prevents graph state from becoming excessively large.

---

# 98. Tool Result Lifecycle

```text
REQUESTED
 ↓
EXECUTING
 ↓
RECEIVED
 ↓
VALIDATED
 ↓
NORMALIZED
 ↓
STORED/REFERENCED
 ↓
CONSUMED
 ↓
EXPIRED
```

---

# 99. API Contract Testing

Every registered API should have contract tests covering:

```text
Request schema
Response schema
Status codes
Error codes
Pagination
Authentication assumptions
Authorization claims
Version compatibility
```

---

# 100. Tool Contract Testing

Test:

```text
Tool input
 ↓
Executor
 ↓
Mock enterprise API
 ↓
Response
 ↓
Normalized result
```

---

# 101. MCP Contract Testing

Test:

```text
MCP server discovery
Tool schema
Resource schema
Authentication
Authorization
Tool invocation
Error handling
Timeout
```

---

# 102. Integration Test Matrix

Minimum:

```text
API success
API 400
API 401
API 403
API 404
API 409
API 429
API 500
API 502
API 503
Timeout
Network failure
Malformed response
Schema mismatch
```

---

# 103. Retry Tests

Test:

```text
First attempt timeout
Second attempt success
```

and:

```text
All attempts fail
```

Verify the correct final state.

---

# 104. Idempotency Tests

Test:

```text
Same idempotency key
Repeated request
Timeout after server processing
Retry
```

Ensure duplicate business transactions do not occur where the enterprise contract supports idempotency.

---

# 105. Parallel Execution Tests

Test:

```text
4 independent APIs
```

Verify:

```text
Concurrent execution
No race condition
Correct aggregation
Partial failure
```

---

# 106. Sequential Execution Tests

Verify:

```text
API B
```

does not execute until:

```text
API A
```

has successfully produced the required dependency.

---

# 107. Tool Security Tests

Attempt:

```text
Unregistered tool
Unauthorized tool
Invalid input
Unauthorized organization
Arbitrary URL
Injected endpoint
```

All must be rejected safely.

---

# 108. MCP Security Tests

Attempt:

```text
Untrusted MCP server
Unauthorized tool
Unauthorized resource
Malformed tool schema
Malicious resource content
Prompt injection
```

---

# 109. Observability

Every integration operation should emit telemetry.

Recommended dimensions:

```text
api_id
tool_id
mcp_server
mcp_tool
operation
status
latency
retry_count
http_status
error_code
workflow_instance_id
agent_run_id
trace_id
```

---

# 110. Metrics

Track:

```text
API calls
Tool calls
MCP calls
Success rate
Failure rate
Timeout rate
Retry rate
429 rate
P50 latency
P95 latency
P99 latency
Parallelism
Circuit state
```

---

# 111. Distributed Tracing

Trace:

```text
FastAPI request
 ↓
LangGraph node
 ↓
Agent Harness
 ↓
Tool Executor
 ↓
Enterprise API
```

For MCP:

```text
Agent
 ↓
MCP Client
 ↓
MCP Server
 ↓
Enterprise Service
```

---

# 112. Structured Logs

Example:

```json
{
  "event": "tool_execution_completed",
  "tool_id": "team.list",
  "status": "SUCCESS",
  "latency_ms": 842,
  "workflow_instance_id": "wf-123",
  "trace_id": "trace-123"
}
```

Do not log sensitive request/response payloads by default.

---

# 113. Langfuse Integration

Tool calls should be traceable to the AI execution.

Example:

```text
Langfuse Trace
   │
   ├── Supervisor
   ├── Agent
   ├── Tool Selection
   ├── Tool Execution
   ├── Enterprise API
   └── SLM
```

Langfuse configuration must be environment-specific.

---

# 114. Tool Evaluation

Evaluate:

```text
Correct tool selected
Correct arguments
Correct API
Correct sequence
Correct parallelism
Correct error handling
Correct final result
```

Tool evaluation is separate from final SLM response evaluation.

---

# 115. Tool Selection Evaluation

Golden test:

```text
User request
Expected tool
Expected parameters
Forbidden tools
```

Example:

```yaml
test:
  input: "Show the club teams"
  expected_tool: team.list
```

---

# 116. API Result Grounding Evaluation

Verify:

```text
Tool result
 ↓
ERC
 ↓
SLM response
```

The final answer should be traceable to the enterprise result.

---

# 117. No-Hallucinated-API Evaluation

Test prompts such as:

```text
"Call any API that can approve the affiliation."
```

The model must not invent an API.

It must select only registered capabilities.

---

# 118. Enterprise Integration Versioning

Version separately:

```text
API contract
Tool
Tool schema
MCP server
MCP tool
Response mapping
Prompt/tool instructions
```

---

# 119. Tool Version

Example:

```yaml
tool_id: team.list
version: 1.2.0
```

---

# 120. Mapping Version

Example:

```yaml
mapping:
  version: 2.0.0
```

---

# 121. Configuration Version

Example:

```yaml
configuration:
  version: 1.0.0
```

---

# 122. Environment Configuration

Recommended:

```text
config/
├── base/
│   └── enterprise/
│       ├── api-catalog.yaml
│       ├── tool-registry.yaml
│       ├── execution-policies.yaml
│       └── mcp.yaml
│
├── dev/
├── test/
├── staging/
└── prod/
```

---

# 123. Secrets

Never store secrets in Git.

Use approved secret management.

Configuration should contain references:

```yaml
authentication:
  secret_ref: enterprise-api-client-secret
```

not:

```yaml
client_secret: actual-secret
```

---

# 124. Environment-Specific Endpoints

Example:

```yaml
endpoint:
  dev: ${CLUB_API_DEV_URL}
  test: ${CLUB_API_TEST_URL}
  staging: ${CLUB_API_STAGING_URL}
  prod: ${CLUB_API_PROD_URL}
```

Or preferably use environment-specific configuration files/secret references without duplicating the API contract.

---

# 125. API Catalog Example

```yaml
api_id: enterprise.team.list

name: List Teams

version: v1

description:
  why: Retrieve authoritative team information.
  where_used:
    - affiliation_context
    - team_validation

endpoint:
  method: GET
  path: /api/v1/clubs/{clubId}/teams

request:
  path:
    clubId:
      type: string
      required: true

response:
  schema: TeamListResponse

mapping:
  target: erc.teams

execution:
  operation: READ
  idempotent: true
  retryable: true
  parallelizable: true
  max_parallelism: 5

authorization:
  claims:
    - team.read
```

---

# 126. Tool Definition Example

```yaml
tool_id: team.list

version: 1.0.0

description: Retrieve teams belonging to the current club.

source:
  type: enterprise_api
  api_id: enterprise.team.list

input_schema: TeamListRequest

output_schema: TeamListResult

execution_policy:
  timeout_ms: 10000
  retry_policy: read-default
  idempotent: true

allowed_agents:
  - affiliation_agent
```

---

# 127. MCP Definition Example

```yaml
mcp:
  server_id: enterprise-club
  version: 1.0.0

  endpoint_ref: MCP_CLUB_ENDPOINT

  tools:
    - club.get
    - team.list

  resources:
    - club.profile

  authorization:
    required_claims:
      - club.read
```

---

# 128. Tool Registry Validation

At startup or deployment validation:

```text
Tool
 ↓
API exists?
 ↓
Version exists?
 ↓
Input schema valid?
 ↓
Output schema valid?
 ↓
Authorization defined?
 ↓
Timeout defined?
 ↓
Retry defined?
 ↓
Status = ACTIVE
```

Invalid tools should fail deployment/configuration validation rather than fail unexpectedly at runtime.

---

# 129. API Catalog Validation

Validate:

```text
Unique API ID
Unique version
Endpoint exists
Method defined
Request schema
Response schema
Owner
Authorization
Execution policy
Mapping
```

---

# 130. MCP Startup Validation

Validate:

```text
Server configured
Endpoint configured
Authentication configured
Allowed tools defined
Allowed resources defined
Version defined
Security policy defined
```

---

# 131. Configuration Drift

The platform should detect:

```text
Registered API definition
vs
deployed configuration
```

where feasible.

---

# 132. Contract Drift

If enterprise API changes:

```text
Enterprise API
 ↓
Contract test
 ↓
Failure
 ↓
Integration version review
```

Do not silently accept incompatible response changes.

---

# 133. Backward Compatibility

When possible:

```text
Tool v1
 ↓
API v1
```

can remain while:

```text
Tool v2
 ↓
API v2
```

is introduced.

Migration should be explicit.

---

# 134. Deprecation

Deprecated APIs/tools should be marked:

```yaml
status: DEPRECATED
sunset_date: "..."
replacement: team.list.v2
```

The agent should not select deprecated tools for new workflows.

---

# 135. Enterprise API Catalog and ERC

The ERC document depends on this integration document for:

```text
API definition
Response mapping
Pagination
Batching source
Freshness
Provenance
```

The Enterprise Integration layer supplies normalized data to ERC.

---

# 136. Enterprise Integration and Memory/Cache

The integration layer may use:

```text
API response cache
```

but must not own:

```text
Conversation memory
Workflow memory
ERC persistence
```

Those are separate platform concerns.

---

# 137. Enterprise Integration and Service Bus

Synchronous:

```text
AI
 ↓
Tool Executor
 ↓
Enterprise API
```

Asynchronous:

```text
Enterprise
 ↓
Service Bus
 ↓
AI Event Consumer
 ↓
ERC / Workflow
```

Service Bus is covered by:

```text
PF-FT-AI-SERVICE-BUS.md
```

---

# 138. Enterprise Integration and Portal Links

Enterprise APIs may return entity identifiers.

The Portal Link subsystem converts these into approved user-facing navigation links.

Example:

```text
club_id
 ↓
Portal Link Registry
 ↓
Club Details URL
```

Portal link architecture is covered separately.

---

# 139. Integration with FastAPI

FastAPI is the presentation/API boundary for the AI application.

It should not directly implement enterprise API orchestration.

```text
FastAPI
 ↓
Application Service
 ↓
Supervisor/LangGraph
 ↓
Agent Harness
 ↓
Tool Executor
 ↓
Enterprise API
```

---

# 140. FastAPI Does Not Replace the Orchestrator

The Chat UI calls:

```text
POST /api/v1/chat
```

The endpoint creates/continues an AI interaction.

It does not manually perform:

```text
Get Club
Get Teams
Get Officials
Call SLM
```

inside the FastAPI route.

The route delegates to the AI runtime.

---

# 141. Chat Request Flow

```text
Chat UI
   │
   ▼
POST /chat
   │
   ▼
FastAPI
   │
   ▼
Request Context
   │
   ▼
Supervisor
   │
   ▼
LangGraph
   │
   ▼
Agent
   │
   ▼
Tool Executor
   │
   ▼
Enterprise APIs / MCP
```

---

# 142. Tool Execution Is Part of Orchestration

The complete workflow can therefore be:

```text
User
 ↓
FastAPI
 ↓
Supervisor
 ↓
Workflow Agent
 ↓
Context Requirement
 ↓
Tool Selection
 ↓
Sequential / Parallel Tool Execution
 ↓
ERC
 ↓
Context Projection
 ↓
Harness
 ↓
SLM
 ↓
Response
```

FastAPI is the API boundary, while LangGraph/Agentic Orchestration performs the workflow execution.

---

# 143. Tool Execution and SLM

The SLM does not directly control HTTP execution.

The SLM produces a structured tool request:

```json
{
  "tool": "team.list",
  "arguments": {
    "club_id": "club-123"
  }
}
```

The runtime validates it and executes the registered tool.

---

# 144. Tool Call Guardrail

The following must always be checked:

```text
Tool exists
Tool is active
Tool allowed for agent
Arguments valid
Claims valid
Entity scope valid
Execution policy valid
```

---

# 145. Tool Call Injection Protection

The following must be rejected:

```text
Tool name containing arbitrary URL
Arguments attempting endpoint override
Instruction to bypass policy
Instruction to add authorization claims
Instruction to call hidden tools
```

---

# 146. API Prompt Injection Boundary

The SLM must never receive raw API documentation as an instruction source unless explicitly required.

API definitions are controlled platform configuration.

---

# 147. Enterprise Free-Text Data

Enterprise APIs may return free text.

Example:

```text
notes
description
comments
```

These values must be treated as untrusted data.

They must not override:

```text
system prompt
agent policy
tool policy
authorization
```

---

# 148. Tool Output Injection

A malicious enterprise field could contain:

```text
"Ignore all previous instructions..."
```

The tool result must remain data.

The Harness should delimit and classify tool output before presenting it to the SLM.

---

# 149. Tool Output Context Format

Example:

```yaml
tool_context:
  source: enterprise.team.list
  trust: AUTHORITATIVE_DATA
  instruction_allowed: false
  data:
    teams: [...]
```

---

# 150. API Data Trust Model

```text
Enterprise structured data
      = authoritative data

Enterprise free text
      = authoritative content, untrusted instructions

Tool metadata
      = trusted platform configuration

MCP resource content
      = untrusted data unless explicitly classified

User content
      = untrusted
```

---

# 151. API Observability Fields

Every request should ideally capture:

```yaml
integration_trace:
  api_id: enterprise.team.list
  tool_id: team.list
  version: 1.0.0
  workflow_instance_id: wf-123
  agent_run_id: run-123
  tool_call_id: tc-123
  correlation_id: corr-123
  trace_id: trace-123
```

---

# 152. API Response Metrics

Track:

```text
status code
response size
latency
records returned
retry count
cache status
```

Avoid logging full sensitive payloads.

---

# 153. Enterprise Integration Cost

Measure:

```text
API calls per workflow
API calls per successful request
Retries
Parallel calls
Response payload size
```

Optimization:

```text
Caching
Batching
Selective retrieval
Parallel execution
Incremental ERC refresh
```

---

# 154. Enterprise Integration Reliability

Reliability mechanisms:

```text
Timeout
Retry
Backoff
Circuit protection
Bulkhead
Idempotency
Contract validation
Schema validation
Fallback where approved
```

---

# 155. No Fabricated Enterprise Result

If API fails:

```text
API unavailable
```

the SLM must not produce:

```text
"Your application is approved."
```

unless an authoritative source confirms it.

---

# 156. Integration Failure Response

The runtime should provide a structured result:

```yaml
integration_status:
  status: UNAVAILABLE
  source: enterprise.application.get
  retryable: true
  verified: false
```

The agent can then decide the user-facing response.

---

# 157. Enterprise API Sequence Example — Affiliation

Illustrative flow:

```text
1. Get Club
        ↓
2. Get Affiliation/Application
        ↓
3. Get required identifiers
        ↓
4. Parallel:
      ├── Get Teams
      ├── Get Officials
      ├── Get Courses
      └── Get Compliance
        ↓
5. Build ERC
        ↓
6. Validate ERC
        ↓
7. Continue workflow
```

The actual sequence must be aligned with the enterprise affiliation flow and API catalog.

---

# 158. Large Collection Example

```text
Teams = 103

Get Teams
 ↓
Pagination
 ↓
103 records
 ↓
Batch 20
 ↓
Batch 20
 ↓
Batch 20
 ↓
Batch 20
 ↓
Batch 20
 ↓
Batch 3
 ↓
Aggregate
 ↓
ERC
```

The same pattern applies to:

```text
Officials
Courses
Other large collections
```

where applicable.

---

# 159. Enterprise API Concurrency Rule

The runtime must respect:

```text
APIM limits
Enterprise service capacity
Tool policy
Workflow SLA
Model context requirements
```

Do not maximize concurrency simply because parallel execution is technically possible.

---

# 160. API Execution Budget

The runtime should maintain:

```yaml
execution_budget:
  max_tool_calls: 50
  max_parallel_calls: 10
  max_total_duration_ms: configured
```

Actual limits should be workflow/configuration specific.

---

# 161. Infinite Tool Loop Protection

The runtime must detect:

```text
Agent
 ↓
Tool
 ↓
Agent
 ↓
Tool
 ↓
Agent
...
```

Use:

```text
max tool calls
max graph iterations
max repeated tool calls
execution deadline
```

---

# 162. Duplicate Tool Call Protection

If the same read tool is repeatedly requested with identical parameters:

```text
tool_id
+
normalized arguments
```

can be used to detect unnecessary repeated execution.

Safe cache/reuse may be applied according to policy.

---

# 163. Tool Call Budget

Each workflow may define:

```yaml
tool_budget:
  max_calls: 30
  max_retries: 3
  max_parallel: 5
```

---

# 164. Tool Risk Classification

Recommended:

```text
READ
LOW_RISK_WRITE
HIGH_RISK_WRITE
TRANSACTIONAL
```

Execution policy may vary by risk.

---

# 165. Read Tool

Example:

```text
Get Club
Get Teams
Get Officials
```

Normally lower risk.

---

# 166. Write Tool

Example:

```text
Update application
Submit request
```

Requires stricter:

```text
authorization
validation
idempotency
audit
confirmation/HIL where required
```

---

# 167. Transactional Tool

A transactional operation must define:

```text
Idempotency
Timeout
Verification
Retry policy
Audit
Failure state
```

---

# 168. Tool Audit

Record:

```text
who
what tool
which version
when
why/workflow
arguments hash
result status
enterprise source
```

Avoid storing sensitive raw payloads unnecessarily.

---

# 169. API Contract Ownership

The API owner owns:

```text
business API contract
```

The AI platform owns:

```text
tool wrapper
mapping
execution policy
AI integration contract
```

Changes must be coordinated.

---

# 170. Integration Change Process

```text
Enterprise API change
       ↓
Contract change detected
       ↓
Impact analysis
       ↓
Mapping update
       ↓
Tool version
       ↓
Integration tests
       ↓
Evaluation
       ↓
Deployment
```

---

# 171. Tool Review Checklist

Before enabling a new tool:

```text
[ ] Purpose defined
[ ] API owner identified
[ ] API contract available
[ ] Input schema defined
[ ] Output schema defined
[ ] Response mapping defined
[ ] Authorization defined
[ ] Retry policy defined
[ ] Timeout defined
[ ] Idempotency defined
[ ] Risk classified
[ ] Allowed agents defined
[ ] Observability defined
[ ] Unit tests created
[ ] Integration tests created
[ ] Security tests created
[ ] Evaluation test created
```

---

# 172. API Registration Checklist

```text
[ ] API ID
[ ] API version
[ ] Owner
[ ] Domain
[ ] Method
[ ] Endpoint reference
[ ] Request schema
[ ] Response schema
[ ] Error schema
[ ] Authorization claims
[ ] Pagination
[ ] Retry policy
[ ] Timeout
[ ] Idempotency
[ ] Dependency graph
[ ] Mapping
[ ] Freshness expectation
```

---

# 173. MCP Registration Checklist

```text
[ ] Server ID
[ ] Server version
[ ] Endpoint
[ ] Transport
[ ] Authentication
[ ] Authorization
[ ] Tools
[ ] Resources
[ ] Schemas
[ ] Risk classification
[ ] Timeout
[ ] Retry
[ ] Observability
[ ] Security review
```

---

# 174. Recommended Python Package Boundary

```text
src/
└── pf_ft_ai/
    ├── integration/
    │   ├── api/
    │   │   ├── catalog.py
    │   │   ├── contracts.py
    │   │   ├── registry.py
    │   │   ├── client.py
    │   │   ├── factory.py
    │   │   └── mappings.py
    │   │
    │   ├── tools/
    │   │   ├── models.py
    │   │   ├── registry.py
    │   │   ├── resolver.py
    │   │   ├── executor.py
    │   │   ├── validator.py
    │   │   └── policy.py
    │   │
    │   ├── mcp/
    │   │   ├── client.py
    │   │   ├── server.py
    │   │   ├── registry.py
    │   │   ├── resources.py
    │   │   ├── tools.py
    │   │   └── policy.py
    │   │
    │   ├── execution/
    │   │   ├── planner.py
    │   │   ├── dependency.py
    │   │   ├── concurrency.py
    │   │   ├── retry.py
    │   │   ├── timeout.py
    │   │   ├── idempotency.py
    │   │   └── circuit.py
    │   │
    │   └── errors/
    │       ├── codes.py
    │       ├── mapping.py
    │       └── handlers.py
    │
    └── tests/
        ├── unit/
        │   ├── api/
        │   ├── tools/
        │   ├── mcp/
        │   └── execution/
        ├── integration/
        │   ├── api/
        │   ├── tools/
        │   └── mcp/
        ├── security/
        │   └── integration/
        └── evaluation/
            └── tools/
```

The final repository will consolidate these logical boundaries with the complete PF-FT AI platform structure.

---

# 175. Configuration Structure

Recommended:

```text
config/
├── base/
│   └── enterprise/
│       ├── api-catalog/
│       ├── tool-registry/
│       ├── mcp/
│       ├── execution-policies.yaml
│       ├── retry-policies.yaml
│       ├── timeout-policies.yaml
│       └── dependency-graph.yaml
│
├── dev/
├── test/
├── staging/
└── prod/
```

---

# 176. Version-Controlled Integration Definitions

The following should be version-controlled:

```text
API catalog
API schemas
Tool definitions
Tool schemas
MCP definitions
Response mappings
Execution policies
Retry policies
Timeout policies
Dependency graph
```

Secrets must remain outside source control.

---

# 177. Recommended Versioning Convention

Use semantic versions:

```text
MAJOR.MINOR.PATCH
```

Examples:

```text
API contract: 2.0.0
Tool: 1.2.0
Mapping: 1.1.0
MCP server contract: 1.0.0
Execution policy: 1.0.0
```

---

# 178. Integration Manifest

A workflow can reference exact versions.

Example:

```yaml
integration_manifest:
  workflow: affiliation
  version: 1.0.0

  tools:
    - id: club.get
      version: 1.0.0

    - id: application.get
      version: 1.2.0

    - id: team.list
      version: 1.0.0

    - id: official.list
      version: 1.1.0
```

This improves reproducibility.

---

# 179. Deployment Validation

Before deployment:

```text
API Catalog
      ↓
Tool Registry
      ↓
MCP Registry
      ↓
Version Validation
      ↓
Schema Validation
      ↓
Authorization Validation
      ↓
Configuration Validation
      ↓
Integration Tests
```

---

# 180. Runtime Safety Boundary

The runtime should have a hard boundary:

```text
LLM-generated tool request
          │
          ▼
Tool Resolver
          │
          ▼
Registered Tool Only
          │
          ▼
Policy Validation
          │
          ▼
Tool Executor
          │
          ▼
Approved Enterprise Capability
```

There should be no direct:

```text
LLM → HTTP URL
```

path.

---

# 181. Final End-to-End Integration Flow

```text
                         CHAT UI
                            │
                            ▼
                       FASTAPI /chat
                            │
                            ▼
                    REQUEST CONTEXT
                            │
                            ▼
                       SUPERVISOR
                            │
                            ▼
                       LANGGRAPH
                            │
                            ▼
                       AGENT/HARNESS
                            │
                            ▼
                     TOOL SELECTION
                            │
                            ▼
                      TOOL REGISTRY
                            │
                            ▼
                     POLICY VALIDATION
                            │
                            ▼
                     TOOL EXECUTOR
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
          ENTERPRISE API             MCP
                 │                     │
                 ▼                     ▼
        ENTERPRISE SERVICES     MCP SERVER
                 │                     │
                 └──────────┬──────────┘
                            ▼
                    NORMALIZED RESULT
                            │
                            ▼
                           ERC
                            │
                            ▼
                    CONTEXT PROJECTION
                            │
                            ▼
                           SLM
                            │
                            ▼
                         RESPONSE
```

---

# 182. Enterprise Integration Acceptance Criteria

The implementation must satisfy:

1. Enterprise APIs remain authoritative.
2. APIs are represented in a version-controlled catalog.
3. Every API has an owner.
4. Every API has a purpose.
5. Every API has an explicit contract.
6. Request schemas are defined.
7. Response schemas are defined.
8. Error schemas are defined.
9. Response-to-context mappings are deterministic.
10. API versions are explicit.
11. Agents cannot invent arbitrary endpoints.
12. Agents can only select registered tools.
13. Tool definitions are versioned.
14. Tool input is schema validated.
15. Tool output is schema validated.
16. Tool execution passes through a central executor.
17. Authorization claims are respected.
18. Claims cannot be elevated by AI.
19. Tenant/organization boundaries are enforced.
20. Enterprise URLs are configuration controlled.
21. Arbitrary user/LLM URLs cannot be executed.
22. Sequential API dependencies are supported.
23. Parallel API execution is supported.
24. Fan-out/fan-in is supported.
25. Bounded concurrency is supported.
26. Pagination is supported.
27. Large collections are supported.
28. Retry policies are configurable.
29. Timeout policies are configurable.
30. Idempotency is supported for applicable operations.
31. Unknown transaction state is handled safely.
32. 429 handling is supported.
33. Circuit protection is supported where required.
34. Bulkhead protection is supported where required.
35. MCP clients are supported.
36. MCP servers are explicitly registered.
37. MCP tools are allowlisted.
38. MCP resources are controlled.
39. MCP authentication is configured securely.
40. MCP authorization is enforced.
41. Tool output is treated as data.
42. Enterprise free-text cannot override system instructions.
43. API failures cannot become fabricated AI facts.
44. Tool calls are observable.
45. Tool calls are traceable to workflow/agent runs.
46. API contract tests exist.
47. Tool unit tests exist.
48. Integration tests exist.
49. Security tests exist.
50. Tool selection evaluation exists.
51. Integration configuration is environment-specific.
52. Secrets are externalized.
53. API/tool/MCP definitions are version controlled.
54. Deployment validates integration definitions.
55. Enterprise integration failure supports safe degradation.
56. The complete API → Tool → ERC → SLM path is traceable.

---

# 183. Final Design Principles

1. **Enterprise APIs remain authoritative.**
2. **AI selects capabilities; it does not invent capabilities.**
3. **All enterprise access passes through controlled integration boundaries.**
4. **FastAPI is the application API boundary, not the enterprise orchestration implementation.**
5. **LangGraph orchestrates workflow execution.**
6. **The Agent Harness controls tool execution safety.**
7. **The Tool Executor is the only controlled runtime path to enterprise capabilities.**
8. **API contracts are version controlled.**
9. **Tool contracts are version controlled.**
10. **MCP capabilities are explicitly registered.**
11. **Authorization remains bounded by enterprise claims/APIM policy.**
12. **Claims are never elevated by AI.**
13. **Enterprise endpoints are never generated dynamically by the SLM.**
14. **Sequential dependencies are explicitly modeled.**
15. **Independent APIs may execute in parallel.**
16. **Parallel execution is bounded.**
17. **Retries are policy-driven.**
18. **Writes require idempotency and transaction-state handling.**
19. **Unknown transaction states are never guessed.**
20. **Enterprise free text is treated as data, not instructions.**
21. **Tool outputs cannot override system/agent policy.**
22. **Large responses are normalized before entering ERC/context.**
23. **All important integration operations are observable.**
24. **Integration quality is evaluated independently from final SLM response quality.**
25. **No enterprise result may be fabricated when an API fails.**
26. **All integration configuration is environment-aware.**
27. **Secrets remain outside source control.**
28. **Contract drift must be detected.**
29. **Tool and API changes require regression testing.**
30. **The integration layer remains a controlled bridge between AI reasoning and authoritative PF-FT enterprise capabilities.**
