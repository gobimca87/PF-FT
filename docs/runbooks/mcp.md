# MCP Runbook

**Owner:** AI Platform / Integration (doc 28 §4).

## Status note

MCP has **no implementation yet** — `src/pf_ft_ai/integration/mcp/` is an empty
package. This is a genuine gap, not an oversight: no MCP server has been approved or
integrated (see `docs/adr/0003-deferred-decisions-log.md` for the pattern this
follows). There is nothing to troubleshoot in production because nothing runs yet.

## When this changes

Once a real MCP server is approved and built, populate this runbook per doc 28 §36/
§62-63:

- Symptoms: server unavailable, client connection failure, tool schema mismatch,
  authorization failure, network, timeout, server version incompatibility.
- Recovery: retry, reconnect, approved alternate server, controlled tool failure —
  never bypass MCP authorization restrictions (doc 28 §63).
- Escalation: AI Platform / Integration, with server ID, tool ID, and correlation ID.

## Escalation (in the meantime)

If an agent or workflow appears to be attempting MCP-shaped behavior today, that is
itself the incident — no MCP capability is registered or authorized, so any such
behavior indicates a bug, not a legitimate MCP failure. Escalate to AI Platform
immediately as a P2/P1 depending on impact (doc 20 §112 — engineering agents and
platform code must not silently gain new integration capabilities).
