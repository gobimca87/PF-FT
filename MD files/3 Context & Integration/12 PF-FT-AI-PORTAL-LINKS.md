# PF-FT Enterprise Agentic AI Platform — Portal Links

**Document ID:** PF-FT-AI-PORTAL-LINKS  
**Phase:** Phase 2 — Enterprise Navigation & UI Integration  
**Version:** 1.0.0  
**Status:** Development Baseline  
**Platform:** PF-FT Enterprise Agentic AI Platform / Adam AI  
**Runtime:** Python / FastAPI / LangGraph  
**Primary Scope:** Portal Catalog, Portal URLs, Deep Links, Environment-specific Links, Workflow Links, Entity Links, Link Generation, Link Validation, Security, Expiration/Signed Links, UI Response Integration

---

# 1. Purpose

This document defines the portal-link architecture for the PF-FT Enterprise Agentic AI Platform.

The platform should not merely provide textual answers such as:

```text
"Open the affiliation page."
```

It should be capable of returning controlled, validated, user-appropriate navigation links to the existing PF-FT enterprise portals.

The portal-link capability provides:

- Portal catalog
- Portal ownership
- Portal purpose
- Portal base URLs
- Environment-specific URLs
- Route definitions
- Deep-link templates
- Entity links
- Workflow links
- Task links
- Application links
- Club links
- Team links
- Official links
- Course links
- Link generation
- Link validation
- Link normalization
- Link security
- Signed/temporary links where applicable
- Expiration handling
- Tenant/organization validation
- UI response integration
- Link metadata
- Accessibility considerations
- Observability
- Unit testing
- Security testing
- Evaluation

---

# 2. Core Principle

> **The AI platform may generate navigation links, but it must never invent enterprise portal URLs.**

The link must originate from:

```text
Approved Portal Catalog
        +
Approved Route Template
        +
Validated Entity Identifier
        +
Environment Configuration
```

Result:

```text
Validated Portal Link
```

The SLM must not directly construct production URLs.

---

# 3. Portal Links Position in the Platform

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
Agent / Harness
   │
   ▼
Enterprise Context / ERC
   │
   ▼
Entity Identifier
   │
   ▼
Portal Link Resolver
   │
   ▼
Portal Catalog
   │
   ▼
Environment URL
   │
   ▼
Route Template
   │
   ▼
Validated Link
   │
   ▼
UI Response
```

---

# 4. Portal Catalog

The platform requires a version-controlled portal catalog.

Recommended logical structure:

```text
config/
└── portals/
    ├── catalog.yaml
    ├── club.yaml
    ├── affiliation.yaml
    ├── competition.yaml
    ├── officials.yaml
    └── courses.yaml
```

The final repository structure will be aligned with the complete platform structure.

---

# 5. Portal Catalog Purpose

The portal catalog answers:

```text
What portal exists?
What is the portal used for?
Who owns it?
Which environment does it belong to?
What base URL does it use?
Which routes are available?
Which entities can be linked?
Which workflows can be linked?
Which users/roles can access it?
```

---

# 6. Portal Catalog Metadata

Example:

```yaml
portal:
  portal_id: affiliation-portal
  name: Affiliation Portal
  domain: affiliation
  owner: enterprise-affiliation
  status: ACTIVE
```

---

# 7. Portal Base URL

Base URLs must be configuration controlled.

Example:

```yaml
urls:
  dev: ${AFFILIATION_PORTAL_DEV_URL}
  test: ${AFFILIATION_PORTAL_TEST_URL}
  staging: ${AFFILIATION_PORTAL_STAGING_URL}
  prod: ${AFFILIATION_PORTAL_PROD_URL}
```

The actual URLs should be provided through approved environment configuration.

---

# 8. Never Hard-Code Environment URLs in Agent Code

Avoid:

```python
url = "https://production.example.com/affiliation/..."
```

Prefer:

```python
portal = portal_registry.get("affiliation-portal")
url = portal.resolve(...)
```

This prevents:

- Environment leakage
- Production links from development
- Hard-coded configuration
- Inconsistent portal URLs

---

# 9. Environment Resolution

The runtime determines:

```text
Current Environment
       ↓
Portal Catalog
       ↓
Environment URL
       ↓
Route
```

Example:

```text
DEV → DEV Portal
TEST → TEST Portal
STAGING → STAGING Portal
PROD → PROD Portal
```

---

# 10. Environment Safety

A development AI instance must never generate a production portal link unless explicitly configured and authorized.

Recommended validation:

```text
runtime environment
        ==
portal URL environment
```

---

# 11. Portal Status

Each portal should have:

```text
ACTIVE
DEPRECATED
MAINTENANCE
DISABLED
```

Only active routes should normally be generated.

---

# 12. Portal Ownership

Example:

```yaml
owner:
  team: Affiliation Platform
  service: Affiliation Portal
```

Ownership helps with:

- Route changes
- Broken links
- Migration
- Support
- Incident management

---

# 13. Portal Version

Where the portal has explicit versions:

```yaml
portal:
  version: 2.0.0
```

The AI platform should maintain the compatible route version.

---

# 14. Route Catalog

Each portal requires a route catalog.

Example:

```yaml
routes:

  club.details:
    path: /clubs/{clubId}

  affiliation.details:
    path: /affiliations/{affiliationId}

  team.details:
    path: /teams/{teamId}

  official.details:
    path: /officials/{officialId}
```

---

# 15. Route Purpose

Every route should describe:

```yaml
purpose:
  why: Open the club profile.
  where_used:
    - club_summary
    - affiliation_context
```

This helps the agent/runtime choose the correct navigation target.

---

# 16. Deep Links

A deep link navigates directly to a specific portal page.

Example:

```text
Portal
  ↓
Club Details
  ↓
Club ID
  ↓
/clubs/{clubId}
```

The runtime should generate the final link only after validating the entity ID.

---

# 17. Deep-Link Template

Example:

```yaml
route:
  route_id: club.details
  path: /clubs/{clubId}
  parameters:
    clubId:
      source: erc.club.id
      required: true
```

---

# 18. Entity Links

Entity links navigate to a specific enterprise object.

Examples:

```text
Club
Team
Official
Course
Application
Affiliation
Competition
```

---

# 19. Entity Link Contract

Example:

```yaml
entity_link:
  entity_type: club
  route_id: club.details
  id_source: erc.club.id
```

---

# 20. Entity Link Generation

Flow:

```text
ERC
 │
 ▼
Entity ID
 │
 ▼
Entity Link Resolver
 │
 ▼
Portal Registry
 │
 ▼
Route Template
 │
 ▼
Validate
 │
 ▼
Final URL
```

---

# 21. Workflow Links

Workflow links navigate to a workflow/application/task.

Examples:

```text
Open affiliation
Open application
Open pending task
Open HIL task
Open review page
```

---

# 22. Workflow Link Contract

Example:

```yaml
workflow_link:
  workflow_type: affiliation
  route_id: affiliation.details
  id_source: workflow.affiliation_id
```

---

# 23. Workflow Link vs Entity Link

Keep the distinction explicit.

| Link Type | Example |
|---|---|
| Portal | Affiliation Portal |
| Entity | Club Details |
| Workflow | Affiliation Journey |
| Task | HIL Review Task |
| Action | Application Review |
| External | Approved external system |

---

# 24. Task Links

A task link may include:

```text
task ID
workflow ID
application ID
```

Example:

```text
/review/tasks/{taskId}
```

The task must be validated against the current user/context before generating a link.

---

# 25. Link Generation Must Be Deterministic

The runtime should generate:

```text
URL = Portal Base URL + Registered Route + Validated Parameters
```

not:

```text
URL = SLM output
```

---

# 26. SLM Role in Link Generation

The SLM may identify:

```text
"The user wants to open the club."
```

It may select:

```text
club.details
```

from an approved capability set.

The runtime generates the actual URL.

---

# 27. SLM Must Not Generate URLs

Unsafe:

```text
SLM → https://some-url/clubs/123
```

Safe:

```text
SLM → portal_route = club.details
          entity_id = club-123

Runtime → validated URL
```

---

# 28. Link Resolver

Recommended component:

```python
class PortalLinkResolver:

    def resolve(
        self,
        portal_id: str,
        route_id: str,
        parameters: dict
    ):
        ...
```

Responsibilities:

```text
Resolve portal
Resolve environment
Resolve route
Validate parameters
Generate URL
Validate URL
Return link metadata
```

---

# 29. Portal Registry

Example:

```python
class PortalRegistry:

    def get_portal(self, portal_id: str):
        ...

    def get_route(self, portal_id: str, route_id: str):
        ...
```

---

# 30. Link Validator

Example:

```python
class PortalLinkValidator:

    def validate(self, link):
        ...
```

Validation includes:

```text
Allowed domain
Allowed scheme
Known portal
Known route
Valid parameters
Correct environment
No unsafe query parameters
```

---

# 31. Allowed Scheme

Normally:

```text
https
```

should be required for enterprise portal links.

Reject:

```text
javascript:
data:
file:
```

and other unsafe schemes.

---

# 32. Allowed Domains

The runtime should maintain an allowlist.

Example:

```yaml
allowed_domains:
  - portal.example.com
  - affiliation.example.com
```

Do not accept arbitrary domains from user/SLM input.

---

# 33. URL Normalization

Normalize:

```text
scheme
host
path
query
fragment
encoding
```

before validation.

---

# 34. Path Parameter Validation

For:

```text
/clubs/{clubId}
```

validate:

```text
clubId exists
clubId format valid
clubId belongs to authorized context
```

---

# 35. Query Parameter Validation

Only registered query parameters may be generated.

Example:

```yaml
query:
  tab:
    allowed:
      - overview
      - teams
      - officials
```

Never allow arbitrary query strings generated by the SLM.

---

# 36. Fragment Validation

If fragments are supported:

```text
#teams
#officials
```

they should be defined in the route catalog.

---

# 37. Link Security

Portal links must respect:

```text
Authentication
Authorization
Tenant isolation
Organization scope
Entity ownership
Environment
Domain allowlist
Route allowlist
```

---

# 38. Authentication

A normal portal link should generally rely on the enterprise portal's existing authentication/session mechanism.

The AI platform should not place credentials in URLs.

Never generate:

```text
?token=secret
?access_token=...
```

unless an explicitly approved architecture requires a short-lived signed mechanism.

---

# 39. Authorization

Generating a link does not itself grant authorization.

Example:

```text
AI generated link
        ↓
User opens portal
        ↓
Portal validates user access
```

The AI platform should additionally avoid generating links for entities outside the user's validated organization/tenant context.

---

# 40. Authorization Boundary

The enterprise application remains authoritative for final access control.

The AI platform performs contextual validation before presenting a link.

```text
AI Context
   ↓
Basic scope validation
   ↓
Generate link
   ↓
Enterprise Portal
   ↓
Final authorization
```

---

# 41. Tenant Isolation

Do not generate:

```text
Club A link
```

for a user scoped to:

```text
Club B
```

unless the enterprise authorization context explicitly permits it.

---

# 42. Entity Ownership Validation

Before generating:

```text
team/{teamId}
```

validate that the team belongs to an authorized club/organization where required.

---

# 43. Workflow Ownership Validation

Before generating:

```text
application/{applicationId}
```

validate that the application is within the user's authorized context.

---

# 44. Sensitive Links

Some routes may expose sensitive information.

Classify routes:

```text
PUBLIC
AUTHENTICATED
AUTHORIZED
SENSITIVE
HIGH_RISK
```

Example:

```yaml
security:
  classification: AUTHORIZED
```

---

# 45. Link Generation Policy

Example:

```yaml
policy:
  allow_generation: true
  require_entity_scope: true
  require_authorization_context: true
  allowed_environments:
    - prod
```

---

# 46. Signed Links

Signed links may be used where the enterprise portal explicitly supports them.

Examples:

```text
Short-lived task access
Temporary external handoff
Secure document access
```

The AI platform must not invent its own signed-link protocol if the target portal does not support it.

---

# 47. Signed Link Principle

If signed links are supported:

```text
Enterprise Portal
       ↓
Signing mechanism
       ↓
AI platform receives approved URL/token
       ↓
AI platform validates metadata
       ↓
UI receives temporary link
```

The AI platform should not expose signing secrets to the SLM.

---

# 48. Signed Link Expiration

Signed links should contain/associate:

```text
issued_at
expires_at
purpose
entity
audience
```

Example:

```yaml
signed_link:
  expires_at: "2026-08-16T12:00:00Z"
```

---

# 49. Expired Links

The platform should not present known-expired temporary links.

If a link expires:

```text
expired
 ↓
regenerate if permitted
```

or:

```text
ask user to reopen through the portal
```

---

# 50. Link Expiration and Chat History

Do not assume that a link stored in conversation history remains valid forever.

The UI/link layer should be capable of indicating:

```text
temporary
expired
requires regeneration
```

where applicable.

---

# 51. Signed Link Security

Never log:

```text
full signed URL
```

if it contains sensitive tokens.

Log:

```text
link_id
route_id
entity_id/hash
expiration
```

instead.

---

# 52. External Links

If external portals are supported:

```text
external portal
```

must be explicitly registered.

Example:

```yaml
external_portal:
  portal_id: approved-external-system
  domain: external.example.com
  approved: true
```

---

# 53. External Link Security

Do not allow:

```text
User-provided arbitrary URL
```

to be returned as a trusted enterprise link.

---

# 54. Link Validation Flow

```text
Link Request
    ↓
Portal Exists?
    ↓
Route Exists?
    ↓
Environment Valid?
    ↓
Parameters Valid?
    ↓
Entity Scope Valid?
    ↓
Domain Allowlisted?
    ↓
Scheme HTTPS?
    ↓
Security Classification Valid?
    ↓
Generate
    ↓
Final Validation
    ↓
Return
```

---

# 55. Link Failure

If link generation fails:

```yaml
link:
  status: UNAVAILABLE
  reason: ROUTE_NOT_CONFIGURED
```

The SLM should not fabricate an alternative URL.

---

# 56. Broken Route

If a configured route is no longer valid:

```text
Portal route
 ↓
Health/validation check
 ↓
BROKEN
```

Mark it:

```text
DISABLED
```

until corrected.

---

# 57. Link Health Checks

Where feasible, the platform may periodically validate:

```text
Portal base URL
Route availability
TLS
Redirect behavior
Environment mapping
```

Do not perform aggressive health checks against production portals.

---

# 58. Route Deprecation

Example:

```yaml
route:
  status: DEPRECATED
  replacement: affiliation.details.v2
```

New workflows should use the replacement route.

---

# 59. Portal Migration

When a portal moves:

```text
Old Portal
    ↓
New Portal
```

update:

```text
environment URL
route catalog
version
validation
tests
```

without changing agent logic.

---

# 60. Portal Link Versioning

Version separately:

```text
Portal catalog
Portal
Route
Link template
Security policy
Signed-link configuration
```

---

# 61. Route Version Example

```yaml
route_id: affiliation.details
version: 2.0.0
```

The workflow may pin the expected route version where reproducibility is required.

---

# 62. Environment Configuration

Recommended:

```text
config/
├── base/
│   └── portals/
│       ├── catalog.yaml
│       ├── routes.yaml
│       └── security.yaml
│
├── dev/
│   └── portals/
├── test/
│   └── portals/
├── staging/
│   └── portals/
└── prod/
    └── portals/
```

---

# 63. Secrets

Do not store:

```text
Signing secret
Portal credentials
Access tokens
Client secrets
```

in Git.

Use approved secret management.

---

# 64. Portal Catalog Example

```yaml
portal:
  portal_id: affiliation-portal
  name: Affiliation Portal
  domain: affiliation
  status: ACTIVE

urls:
  dev: ${AFFILIATION_PORTAL_DEV_URL}
  test: ${AFFILIATION_PORTAL_TEST_URL}
  staging: ${AFFILIATION_PORTAL_STAGING_URL}
  prod: ${AFFILIATION_PORTAL_PROD_URL}

routes:

  affiliation.details:
    version: 1.0.0
    path: /affiliations/{affiliationId}

  application.details:
    version: 1.0.0
    path: /applications/{applicationId}

  club.details:
    version: 1.0.0
    path: /clubs/{clubId}
```

---

# 65. Route Parameter Source

Example:

```yaml
parameters:
  affiliationId:
    source: erc.affiliation.id
    required: true
```

Possible sources:

```text
ERC
Workflow State
Enterprise API result
Validated request context
```

Never use arbitrary user text without validation.

---

# 66. Entity Link Mapping

Example:

```yaml
entity_links:

  club:
    portal: affiliation-portal
    route: club.details
    id_source: erc.club.id

  affiliation:
    portal: affiliation-portal
    route: affiliation.details
    id_source: erc.affiliation.id

  application:
    portal: affiliation-portal
    route: application.details
    id_source: workflow.application_id
```

---

# 67. Workflow Link Mapping

Example:

```yaml
workflow_links:

  affiliation:
    portal: affiliation-portal
    route: affiliation.details
    id_source: workflow.affiliation_id
```

---

# 68. UI Link Metadata

Do not return only:

```text
"https://..."
```

Prefer a structured response.

Example:

```json
{
  "type": "portal_link",
  "label": "Open Affiliation",
  "url": "https://...",
  "portal_id": "affiliation-portal",
  "route_id": "affiliation.details",
  "entity_type": "affiliation",
  "entity_id": "aff-123"
}
```

---

# 69. UI Response Contract

Recommended:

```yaml
links:
  - link_id: link-123
    type: portal_link
    label: Open Affiliation
    url: https://...
    portal_id: affiliation-portal
    route_id: affiliation.details
    entity:
      type: affiliation
      id: aff-123
    security:
      classification: AUTHORIZED
```

---

# 70. Link Label

The label should be user-friendly.

Examples:

```text
Open Club
View Teams
Open Affiliation
Review Application
Open HIL Task
View Official
```

The label may be generated by controlled application configuration rather than freely generated by the SLM.

---

# 71. Link Type

Use explicit types:

```text
portal
entity
workflow
task
external
temporary
```

This allows the Chat UI to render links appropriately.

---

# 72. UI Rendering

The Chat UI can render:

```text
[Open Affiliation]
```

rather than exposing a long URL.

---

# 73. UI Link Response

Example:

```text
Assistant:
"The affiliation information is ready."

[Open Affiliation]
[View Club]
[View Teams]
```

The actual URL is carried in structured metadata.

---

# 74. Multiple Links

For an ERC containing multiple entities:

```text
Club
 ├── Open Club
 ├── Team A
 ├── Team B
 ├── Team C
 └── Officials
```

The backend should generate only links that are relevant and within response limits.

---

# 75. Large Link Collections

For:

```text
100+ teams
100+ officials
```

do not automatically return 100+ UI links.

Use:

```text
summary links
pagination
search
top relevant entities
```

according to UI requirements.

---

# 76. Link Budget

The response layer may define:

```yaml
link_budget:
  max_links: 10
```

Additional entities can remain accessible through the portal.

---

# 77. Link Selection

The agent may determine that:

```text
User wants the affiliation
```

but application code determines:

```text
affiliation.details
```

and generates the link.

---

# 78. Link Provenance

Every generated link should be traceable to:

```text
portal_id
route_id
entity_id
workflow_id
generation time
environment
```

---

# 79. Link ID

Example:

```text
link_id = link-01J...
```

This allows:

```text
observability
analytics
debugging
UI event tracking
```

---

# 80. Link Analytics

Where permitted, track:

```text
link generated
link displayed
link clicked
link expired
link validation failed
```

Avoid tracking sensitive user behavior beyond approved requirements.

---

# 81. Link Click Tracking

If click tracking is implemented:

```text
Chat UI
 ↓
Click
 ↓
Approved analytics event
 ↓
Portal
```

Do not create an unsafe redirector.

---

# 82. Redirect Security

Avoid:

```text
/go?url=<arbitrary-user-url>
```

Prefer:

```text
/go?link_id=<registered-link-id>
```

where the backend resolves the link from trusted metadata.

---

# 83. Open Redirect Protection

The platform must prevent:

```text
AI-generated redirect
User-generated redirect
External arbitrary redirect
```

---

# 84. Portal Link Security Classification

Recommended:

```yaml
security:
  classification: AUTHORIZED
  domain_allowlist: true
  https_required: true
  entity_scope_required: true
```

---

# 85. Link Generation from ERC

Example:

```text
ERC:
  club.id = club-123
  affiliation.id = aff-456

        ↓

Link Resolver

        ↓

Open Club
Open Affiliation
```

The link layer consumes stable identifiers from ERC rather than asking the SLM to reconstruct them.

---

# 86. Link Generation from Enterprise API

If an enterprise API provides a portal route/entity ID:

```text
API Response
 ↓
Validate ID
 ↓
Resolve registered route
 ↓
Generate link
```

Do not blindly trust a URL field returned by an enterprise API unless that field is explicitly approved by the portal-link contract.

---

# 87. Enterprise URL Field Handling

If an API returns:

```json
{
  "url": "..."
}
```

the platform should classify it as:

```text
approved enterprise link
```

only if the API contract explicitly identifies it as safe navigation metadata.

Otherwise prefer:

```text
entity ID → Portal Link Registry
```

---

# 88. Portal Link and MCP

MCP tools/resources may expose entity information.

The AI platform should still use the Portal Link Resolver.

Do not allow an MCP resource to inject an arbitrary navigation URL into the UI.

---

# 89. Portal Link and Service Bus

Events may identify:

```text
application_id
task_id
workflow_id
```

After workflow resume or ERC refresh, the platform may generate updated portal links.

---

# 90. Portal Link and Memory

Conversation memory may store:

```text
link metadata
```

but temporary/signed URLs should not be treated as permanently valid memory.

Store:

```text
portal_id
route_id
entity_id
link policy
```

and regenerate temporary links when required.

---

# 91. Portal Link and Cache

Safe reusable links may be cached according to route policy.

Temporary signed links should generally not be cached beyond their validity period.

---

# 92. Portal Link and Session

A link may depend on:

```text
current environment
tenant
organization
user authorization
session
```

Therefore link generation may need to occur at response time.

---

# 93. Portal Link and Prompt Injection

Portal content, enterprise text, event payloads or user messages must never be allowed to instruct the system:

```text
Open this arbitrary URL
Redirect the user here
Ignore domain validation
```

The Link Resolver remains authoritative.

---

# 94. Link Generation Guardrail

Before returning a link:

```text
Registered portal?
Registered route?
Correct environment?
Valid entity?
Authorized scope?
Allowed domain?
HTTPS?
No unsafe parameters?
Expiration valid?
```

---

# 95. Invalid Link Guardrail

If any validation fails:

```text
Do not return link.
```

Return:

```yaml
status: UNAVAILABLE
reason: LINK_VALIDATION_FAILED
```

The SLM may explain the limitation but must not fabricate a replacement URL.

---

# 96. Portal Link API

FastAPI may expose a controlled internal endpoint if required:

```text
POST /api/v1/links/resolve
```

Example request:

```json
{
  "portal_id": "affiliation-portal",
  "route_id": "affiliation.details",
  "entity_type": "affiliation",
  "entity_id": "aff-123"
}
```

---

# 97. Link API Response

```json
{
  "status": "ACTIVE",
  "link": {
    "link_id": "link-123",
    "label": "Open Affiliation",
    "url": "https://...",
    "expires_at": null
  }
}
```

---

# 98. Link API Authorization

The endpoint must use the validated request context/claims.

It must not allow the caller to bypass enterprise authorization boundaries.

---

# 99. Chat API Integration

The primary chat endpoint may directly return links as part of the assistant response.

Example:

```text
POST /api/v1/chat

Response:
{
  "message": "...",
  "links": [...]
}
```

A separate link endpoint is optional and depends on the final API design.

---

# 100. UI Response Architecture

```text
LangGraph
   ↓
Agent Result
   ↓
Response Composer
   ↓
Link Resolver
   ↓
Validated Link Metadata
   ↓
Chat Response DTO
   ↓
FastAPI
   ↓
Chat UI
```

---

# 101. Response Composer

The response composer combines:

```text
Answer
+
Citations/Provenance where applicable
+
Portal links
+
UI metadata
```

---

# 102. Link Ordering

Links should be ordered by relevance.

Example:

```text
1. Open Affiliation
2. Open Application
3. Open Club
4. View Teams
```

---

# 103. Link Deduplication

If the same link is generated multiple times:

```text
same portal
+
same route
+
same entity
```

deduplicate it.

---

# 104. Link Generation Failure Should Not Fail the Whole Response

If:

```text
Answer = successful
Link = unavailable
```

the response may still be returned.

Example:

```text
"The affiliation details are available."

No link displayed because the portal route is currently unavailable.
```

The failure should be observable.

---

# 105. Portal Availability Failure

If the portal is known to be unavailable:

```text
Do not generate misleading links.
```

If link generation itself is deterministic and the portal is expected to be available, the platform may still return the link based on configured policy.

---

# 106. Link Validation Modes

Recommended:

```text
CONFIGURATION_VALIDATION
RUNTIME_VALIDATION
HEALTH_VALIDATION
SECURITY_VALIDATION
```

---

# 107. Configuration Validation

At startup/deployment:

```text
Portal exists
Base URL exists
Route exists
Route parameters defined
Domain allowed
```

---

# 108. Runtime Validation

For every generated link:

```text
Entity valid
Scope valid
Environment correct
Route active
URL safe
```

---

# 109. Health Validation

Operational checks may validate:

```text
Portal reachable
TLS valid
Expected redirect behavior
```

without exposing sensitive pages or performing destructive actions.

---

# 110. Security Validation

Validate:

```text
HTTPS
Allowlisted host
No credentials in URL
No arbitrary redirect
No unsafe scheme
No unapproved query parameters
No tenant leakage
```

---

# 111. Portal Link Unit Tests

Test:

```text
Portal lookup
Route lookup
Environment resolution
Parameter substitution
URL encoding
Domain validation
Scheme validation
Entity scope validation
Expiration validation
Signed-link validation
Link deduplication
```

---

# 112. Security Tests

Test:

```text
javascript URL
data URL
file URL
unknown domain
arbitrary external URL
wrong tenant
wrong organization
invalid entity
expired signed link
tampered signed link
token leakage
open redirect
```

---

# 113. Integration Tests

Test:

```text
ERC → Link Resolver
Workflow → Link Resolver
Enterprise API → Link Resolver
MCP → Link Resolver
Service Bus → Workflow → Link Resolver
FastAPI → UI response
```

---

# 114. Evaluation Tests

Golden cases should verify:

```text
Correct portal selected
Correct route selected
Correct entity selected
Correct label
No arbitrary URL
No wrong-environment URL
No unauthorized entity link
```

---

# 115. Link Evaluation Example

Input:

```text
"Open the club profile."
```

Expected:

```yaml
portal_id: club-portal
route_id: club.details
entity_type: club
```

The evaluator should not compare only raw URLs because environment-specific hosts may differ.

---

# 116. Wrong Portal Evaluation

Input:

```text
"Open the affiliation."
```

Expected:

```text
affiliation-portal
```

not:

```text
club-portal
```

---

# 117. Wrong Entity Evaluation

If ERC contains:

```text
Club A
Club B
```

and current workflow is:

```text
Club A
```

the generated link must reference:

```text
Club A
```

only.

---

# 118. Environment Evaluation

If:

```text
environment = test
```

expected:

```text
TEST portal
```

not production.

---

# 119. Portal Link Observability

Record:

```text
link_id
portal_id
route_id
entity_type
environment
workflow_instance_id
correlation_id
trace_id
status
```

Do not log sensitive signed tokens.

---

# 120. Metrics

Track:

```text
Links generated
Links validation failures
Links unavailable
Links expired
Links regenerated
Links clicked
Links by portal
Links by route
```

---

# 121. Alerts

Recommended:

```text
Portal configuration failure
Route validation failure spike
Environment mismatch
Unexpected domain
Signed-link generation failure
Portal unavailable
Link validation failure spike
```

---

# 122. Recommended Python Package Boundary

```text
src/
└── pf_ft_ai/
    ├── portal_links/
    │   ├── models.py
    │   ├── catalog.py
    │   ├── registry.py
    │   ├── route_registry.py
    │   ├── resolver.py
    │   ├── validator.py
    │   ├── security.py
    │   ├── expiration.py
    │   ├── signed_links.py
    │   ├── entity_links.py
    │   ├── workflow_links.py
    │   └── ui_contract.py
    │
    └── tests/
        ├── unit/
        │   └── portal_links/
        ├── integration/
        │   └── portal_links/
        ├── security/
        │   └── portal_links/
        └── evaluation/
            └── portal_links/
```

---

# 123. Configuration Structure

Recommended:

```text
config/
├── base/
│   └── portals/
│       ├── catalog.yaml
│       ├── routes.yaml
│       ├── entities.yaml
│       ├── workflows.yaml
│       ├── security.yaml
│       └── policies.yaml
│
├── dev/
│   └── portals/
├── test/
│   └── portals/
├── staging/
│   └── portals/
└── prod/
    └── portals/
```

---

# 124. Portal Catalog Example

```yaml
portal:
  portal_id: club-portal
  name: Club Portal
  domain: club
  status: ACTIVE

urls:
  dev: ${CLUB_PORTAL_DEV_URL}
  test: ${CLUB_PORTAL_TEST_URL}
  staging: ${CLUB_PORTAL_STAGING_URL}
  prod: ${CLUB_PORTAL_PROD_URL}

routes:

  club.details:
    version: 1.0.0
    path: /clubs/{clubId}

  team.details:
    version: 1.0.0
    path: /teams/{teamId}

security:
  https_required: true
  domain_allowlist: true
  entity_scope_required: true
```

---

# 125. Route Definition Example

```yaml
route:
  route_id: club.details
  version: 1.0.0

  method: GET

  path: /clubs/{clubId}

  parameters:
    clubId:
      source: erc.club.id
      required: true

  security:
    classification: AUTHORIZED
    require_entity_scope: true

  ui:
    label: Open Club
```

---

# 126. Workflow Route Definition

```yaml
route:
  route_id: affiliation.details
  version: 1.0.0

  path: /affiliations/{affiliationId}

  parameters:
    affiliationId:
      source: erc.affiliation.id
      required: true

  ui:
    label: Open Affiliation
```

---

# 127. Temporary Link Definition

Where supported:

```yaml
temporary_link:
  enabled: true
  expires_after_seconds: 900
  signing_provider_ref: portal-signing-service
```

Do not place signing credentials in this file.

---

# 128. Link Policy

Example:

```yaml
link_policy:

  max_links_per_response: 10

  allowed_schemes:
    - https

  require_allowlisted_domain: true

  require_entity_scope: true

  allow_external_domains: false
```

---

# 129. Portal Registry Validation

At startup:

```text
Portal ID unique
Route ID unique within portal
Base URL configured
Environment mapping valid
Routes valid
Parameters valid
Security policy valid
```

---

# 130. Route Registration Validation

Each route must pass:

```text
Path syntax
Parameter syntax
Parameter source
Security classification
Environment availability
UI label
Status
```

---

# 131. Portal Link Lifecycle

```text
CONFIGURED
    ↓
VALIDATED
    ↓
ACTIVE
    ↓
GENERATED
    ↓
DISPLAYED
    ↓
CLICKED
    ↓
EXPIRED / RETIRED
```

---

# 132. Link State

Example:

```yaml
link:
  status: ACTIVE
```

Possible states:

```text
ACTIVE
EXPIRED
REVOKED
DISABLED
INVALID
```

---

# 133. Link Revocation

Temporary/signed links may be revoked by the enterprise signing mechanism.

The AI platform should not assume a previously issued temporary link remains valid.

---

# 134. Link Regeneration

When allowed:

```text
Expired link
 ↓
Validate current context
 ↓
Resolve route
 ↓
Generate new link
 ↓
Return to UI
```

---

# 135. Link Cache Policy

For static route/entity links:

```text
cacheable: true
```

For signed links:

```text
cacheable: false
```

or cache only within the remaining validity period and approved policy.

---

# 136. Portal Link and Chat Session

The chat session may retain:

```text
portal_id
route_id
entity_id
```

rather than permanently storing an environment-specific temporary URL.

---

# 137. Portal Link and ERC

ERC should contain stable entity references:

```yaml
erc:
  club:
    id: club-123
```

The Portal Link layer converts this to:

```text
Open Club
```

This keeps ERC independent from portal URL implementation.

---

# 138. Portal Link and API Catalog

The Enterprise API catalog may define:

```text
entity identifiers
```

but the Portal Link catalog defines:

```text
navigation routes
```

These are separate concerns.

---

# 139. Portal Link and Service Bus

Service Bus events can carry:

```text
entity ID
workflow ID
task ID
```

The event handler can use those identifiers to generate or refresh navigation links.

---

# 140. Portal Link and MCP

MCP may expose entity data, but:

```text
MCP result → Entity ID → Portal Link Resolver
```

rather than:

```text
MCP result → arbitrary URL → UI
```

---

# 141. Portal Link and Agent Harness

The Agent Harness may allow an agent to request:

```text
create_portal_link
```

but the tool is constrained by:

```text
Portal Registry
Route Registry
Security Policy
Entity Scope
Environment
```

---

# 142. Portal Link Tool

Example:

```yaml
tool_id: portal.link.create
description: Generate an approved portal navigation link.
```

Input:

```json
{
  "portal_id": "club-portal",
  "route_id": "club.details",
  "entity_type": "club",
  "entity_id": "club-123"
}
```

The runtime performs all validation.

---

# 143. Link Tool Guardrails

The tool must reject:

```text
Unknown portal
Unknown route
Arbitrary URL
Wrong environment
Invalid entity
Unauthorized entity
Unsupported query parameter
Unsafe scheme
Unapproved domain
```

---

# 144. Portal Link API / Tool Separation

The internal implementation may expose:

```text
PortalLinkService
```

and optionally:

```text
portal.link.create
```

as a controlled agent tool.

The agent should not access the underlying registry directly.

---

# 145. Complete Portal-Link Flow

```text
User:
"Open the affiliation."

        ↓

FastAPI

        ↓

LangGraph / Agent

        ↓

Intent:
OPEN_AFFILIATION

        ↓

Approved Link Capability

        ↓

Portal Link Resolver

        ↓

Portal Registry

        ↓

Affiliation Route

        ↓

ERC.affiliation.id

        ↓

Entity Scope Validation

        ↓

Environment Resolution

        ↓

URL Validation

        ↓

Structured Link

        ↓

FastAPI Response

        ↓

Chat UI

        ↓

[Open Affiliation]
```

---

# 146. Portal Link Acceptance Criteria

The implementation must satisfy:

1. Portal catalog exists.
2. Every portal has an owner.
3. Every portal has a lifecycle status.
4. Portal URLs are environment-specific.
5. URLs are configuration controlled.
6. Production URLs are not hard-coded in agent code.
7. Routes are cataloged.
8. Routes are versioned.
9. Route parameters are defined.
10. Entity links are supported.
11. Workflow links are supported.
12. Task links are supported.
13. Deep links are supported.
14. Link generation is deterministic.
15. SLM cannot generate arbitrary URLs.
16. Domains are allowlisted.
17. HTTPS is required.
18. Unsafe URL schemes are rejected.
19. Arbitrary query parameters are rejected.
20. Entity scope is validated.
21. Tenant isolation is enforced.
22. Organization isolation is enforced.
23. Portal authorization remains authoritative.
24. Temporary/signed links are supported where the enterprise portal provides them.
25. Signed-link secrets are never exposed to the SLM.
26. Expiration is handled.
27. Expired links are not presented as active temporary links.
28. Open redirects are prevented.
29. External domains are explicitly allowlisted.
30. Portal route deprecation is supported.
31. Environment mismatch is prevented.
32. Link generation failures do not fabricate alternatives.
33. Structured UI link metadata is returned.
34. Links can be rendered as UI actions.
35. Large entity collections do not create uncontrolled link output.
36. Link generation is observable.
37. Sensitive signed URLs are not logged.
38. Unit tests exist.
39. Integration tests exist.
40. Security tests exist.
41. Evaluation tests exist.
42. Portal configuration is version controlled.
43. Portal secrets are externalized.
44. Link resolution integrates with ERC.
45. Link resolution integrates with Enterprise Integration.
46. Link resolution integrates with workflow state.
47. Link resolution integrates with Service Bus-triggered workflows where required.
48. Link resolution is compatible with MCP-derived entity data.
49. Portal links remain independent of SLM-generated text.
50. The complete entity/workflow → validated link → Chat UI path is traceable.

---

# 147. Final End-to-End Architecture

```text
                         PF-FT ENTERPRISE PORTALS
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
          Club Portal       Affiliation       Other Portals
                              Portal
                │                 │
                └────────┬────────┘
                         │
                         ▼
                   PORTAL CATALOG
                         │
                         ▼
                   ROUTE REGISTRY
                         │
                         ▼
                  LINK RESOLVER
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
         ERC          Workflow        Event
      Entity IDs        State          Context
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  SECURITY VALIDATOR
                         │
                         ▼
                  ENVIRONMENT RESOLVER
                         │
                         ▼
                    URL VALIDATOR
                         │
                         ▼
                  STRUCTURED LINK
                         │
                         ▼
                    RESPONSE DTO
                         │
                         ▼
                       FastAPI
                         │
                         ▼
                      CHAT UI
                         │
                         ▼
                 [Open Enterprise Portal]
```

---

# 148. Final Design Principles

1. **Portal URLs are configuration, not model knowledge.**
2. **The SLM never directly generates trusted enterprise URLs.**
3. **Every portal is registered in a controlled catalog.**
4. **Every route is explicitly registered.**
5. **Every route is versioned where required.**
6. **Environment-specific URLs are mandatory.**
7. **Entity IDs come from trusted validated context.**
8. **Workflow IDs come from validated workflow state.**
9. **Link generation is deterministic.**
10. **The Link Resolver is the authoritative URL construction component.**
11. **Only HTTPS links are normally permitted.**
12. **Domains are allowlisted.**
13. **Arbitrary redirects are prohibited.**
14. **Arbitrary query parameters are prohibited.**
15. **Tenant and organization boundaries are enforced.**
16. **Final authorization remains with the enterprise portal.**
17. **Temporary/signed links are used only where explicitly supported.**
18. **Signed-link secrets never enter prompts or model context.**
19. **Expired temporary links are not presented as active.**
20. **Portal links are structured UI data, not plain model-generated text.**
21. **ERC stores stable entity identity rather than portal-specific URL construction.**
22. **Enterprise APIs provide authoritative entity identifiers.**
23. **Service Bus events can trigger link regeneration after workflow/context changes.**
24. **MCP data does not bypass the Portal Link Resolver.**
25. **Portal links can be exposed through controlled agent tools.**
26. **Link generation is observable.**
27. **Sensitive link tokens are protected from logs.**
28. **Large collections are bounded for UI usability.**
29. **Link failures must never cause URL hallucination.**
30. **Portal migration should require configuration changes rather than agent-code changes.**
31. **Portal and route configuration is version controlled.**
32. **Environment secrets and signing credentials remain externalized.**
33. **Portal links are independently unit tested, integration tested and security tested.**
34. **Portal-link selection and generation are evaluated independently from SLM response quality.**
35. **The complete ERC/workflow → link resolver → validation → FastAPI → Chat UI path must be traceable.**
