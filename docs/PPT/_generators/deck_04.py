#!/usr/bin/env python3
"""Deck 04 — Information, Context & Data (D4), FA light theme."""
import os
from fa import (Deck, adrs_for, PP_ALIGN, MSO_SHAPE, MSO_ANCHOR,
                NAVY, NAVY_DEEP, BLUE, GOLD, GREY, WHITE, MUTEDBLUE, CARD, CARD_LINE,
                CX0, CX1, CW)

OUT = os.path.join(os.path.dirname(__file__), "..", "04-information-context-data.pptx")


def batch_diagram(d, s):
    d.text(s, "100 teams  ÷  20 per loop  =  5 controlled batches  →  aggregate",
           CX0, 1.95, CW, 0.4, size=15, color=BLUE, bold=True)
    x = CX0; y = 2.6; w = 1.6; h = 0.85; gap = 0.2
    for i in range(5):
        d.box(s, f"Batch {i+1}\n20 teams", x, y, w, h, style="light", size=11)
        d.connector(s, x + w, y + h / 2, 10.7, 3.95, color=BLUE, width=1.1, arrow=(i == 2))
        x += w + gap
    d.box(s, "ERC\nAggregator", 10.7, 3.55, 2.0, 0.9, style="navy", size=13)
    d.bullets(s, [
        "Batch size is tuned to API limits, context window, memory, latency and token cost — not increased blindly.",
        "Same principle for 100+ officials. Batches parallelise only when enterprise operations are independent.",
        "Intermediate objects released after aggregation to bound memory (deck 08).",
    ], CX0, 4.8, CW, 1.8, size=14, gap=11)


def build():
    d = Deck()
    d.title_slide("Information,", "Context & Data",
                  "Four states · ERC · identifiers · state store · memory · cache  —  D4 (13 ADRs)",
                  kicker="Deck 04 · Information architecture",
                  notes="How the platform models and moves information: the four separated states, the "
                        "Enterprise Runtime Context (ERC), canonical identifiers, and the Redis-backed "
                        "state/memory/cache stores. 13 ADRs.")

    d.agenda_slide("What this deck covers", [
        "Four state concepts — kept strictly separate",
        "ERC — schema, identity, versioning, provenance & authority",
        "ERC collection planning & batching (20 per loop)",
        "ERC partial-failure semantics & event refresh",
        "Data & knowledge architecture; canonical identifiers",
        "Metadata response envelope & error codes",
        "Session/conversation state store — Azure Managed Redis",
        "Memory architecture",
        "Cache architecture & platform-global scope",
    ])

    s = d.content_slide("Four state concepts", kicker="D4-01",
                        subtitle="Kept strictly separate — never conflated in code")
    quad = [("Conversation State", "turns, messages, intent — per conversation"),
            ("Session State", "auth context, correlation, ttl — per session"),
            ("Workflow / Agent State", "graph state, steps, HIL — per workflow run"),
            ("Enterprise Business State", "system-of-record truth — owned by PFF")]
    xs = [CX0, 7.4]; ys = [1.95, 4.25]; cw = 5.25; ch = 1.95
    for i, (t, sub) in enumerate(quad):
        x = xs[i % 2]; y = ys[i // 2]; col = NAVY if i % 2 == 0 else BLUE
        d.card(s, x, y, cw, ch)
        d._rect(s, x, y + 0.32, 0.12, 0.9, col)
        d.text(s, t, x + 0.35, y + 0.32, cw - 0.6, 0.5, size=18, color=col, bold=True, font="Cambria")
        d.text(s, sub, x + 0.35, y + 1.02, cw - 0.6, 0.8, size=13, color=GREY)
    d.set_notes(s, "Enterprise business state is owned entirely by PFF; the AI holds only conversation, "
                   "session and workflow state.")

    s = d.content_slide("ERC — Enterprise Runtime Context", kicker="D4-02 / D4-03")
    d.two_col(s, "Schema, identity, versioning", [
        "ERC is the validated, typed snapshot of enterprise context for a workflow.",
        "Stable schema with identity & versioning (D4-02).",
        "Pydantic at the boundary; never raw pass-through.",
    ], "Provenance, freshness, authority", [
        "Every ERC value carries provenance & freshness (D4-03).",
        "ERC sits just below Enterprise API/Event in the precedence chain.",
        "A PARTIAL ERC is never presented as COMPLETE.",
    ])
    d.set_notes(s, "ERC is the contextual boundary between the enterprise and the AI — validated, "
                   "versioned, provenanced and freshness-tracked.")

    s = d.content_slide("ERC collection & batching", kicker="D4-04",
                        subtitle="Controlled, bounded")
    batch_diagram(d, s)
    d.set_notes(s, "Large entity sets (100+ teams/officials) are gathered in controlled batches of ~20 "
                   "and aggregated; batch size is a tuned parameter, not a blind maximum.")

    s = d.content_slide("ERC partial failure & refresh", kicker="D4-05 / D4-06")
    d.two_col(s, "Partial-failure semantics", [
        "If some entities fail, ERC is explicitly PARTIAL — never silently treated as complete.",
        "The workflow decides: retry, degrade, or surface to the user.",
        "PFF Chat AI states clearly what could not be gathered.",
    ], "Invalidation & event refresh", [
        "Enterprise events invalidate stale ERC entries (D4-06).",
        "Refresh is event-driven via Service Bus (deck 02).",
        "Freshness bounds prevent acting on outdated context.",
    ])
    d.set_notes(s, "Partial ERC is a first-class, explicit state; event-driven invalidation keeps context fresh.")

    s = d.content_slide("Data & knowledge architecture", kicker="D4-07 / D4-08")
    d.two_col(s, "Data & knowledge", [
        "Clear split: authoritative enterprise data vs. RAG knowledge corpus.",
        "Knowledge is grounding only; authority stays with the enterprise.",
    ], "Canonical identifiers & reference data", [
        "Canonical IDs (club, team, official, season) resolved consistently.",
        "Reference data is versioned and cache-eligible where safe.",
        "IDs are never invented — resolved from the enterprise.",
    ])
    d.set_notes(s, "A clean separation of authoritative data and knowledge, with canonical identifiers "
                   "resolved from the enterprise — never fabricated.")

    s = d.content_slide("Metadata envelope & error codes", kicker="D4-09")
    d.bullets(s, [
        "A consistent metadata response envelope wraps enterprise/tool responses: status, provenance, freshness, correlation, and typed error codes.",
        "Error codes map to the PlatformError hierarchy (deck 07) so failures are handled uniformly.",
        "This envelope is what lets PFF Chat AI communicate precise, factual state and next actions.",
    ], CX0, 1.95, CW, 3.2, size=16, gap=15)
    d.set_notes(s, "A uniform envelope carries status, provenance, freshness and typed error codes — "
                   "the substrate for factual communication and consistent error handling.")

    s = d.content_slide("State store — Azure Managed Redis", kicker="D4-10 · Accepted")
    d.image(s, "redis", CX0, 2.1, h=1.2)
    d.kv_panel(s, "Resolved: Azure Managed Redis", [
        ("Holds", "conversation & session state, workflow checkpoints, cache"),
        ("Why", "managed, low-latency, Azure-native, TTL & eviction"),
        ("Status", "Accepted — supersedes the earlier ADR-0004 draft"),
    ], CX0 + 2.3, 1.95, 8.35, 2.5)
    d.text(s, "Memory / session / cache store is resolved — not an open decision. Cost drivers (SKU, memory) in deck 08.",
           CX0, 4.7, CW, 0.8, size=14, color=GREY)
    d.set_notes(s, "The state/session/cache store decision is Accepted: Azure Managed Redis.")

    s = d.content_slide("Memory architecture", kicker="D4-11")
    d.bullets(s, [
        "Memory service with policy-driven retention, retrieval and ranking; summarization for long conversations.",
        "Protects important authoritative context from being summarised away.",
        "Storage-technology-agnostic interface (Redis-backed); observable read/write costs (deck 08).",
    ], CX0, 1.95, CW, 3.2, size=16, gap=15)
    d.set_notes(s, "Memory is policy-driven: retention, retrieval, ranking, summarization — with explicit "
                   "protection for authoritative context.")

    s = d.content_slide("Cache architecture & scope", kicker="D4-12 / D4-13")
    d.two_col(s, "Cache design", [
        "TTL, eviction, invalidation, serialization, protection.",
        "Cache only where freshness & authorization allow.",
        "A cache stays only when benefit > operational cost (deck 08).",
    ], "Authorization-aware & global scope", [
        "Cache keys account for access scope — never cross authorization contexts.",
        "Platform-global entries (reference data, portal metadata) scoped explicitly (D4-13).",
        "Transactional operations are not cached unless provably safe.",
    ])
    d.set_notes(s, "Caching is authorization-aware and freshness-bounded; never serve cached data across "
                   "incompatible authorization contexts.")

    d.adr_index_slides("ADR index — Information (D4)", adrs_for(4),
                       notes="All 13 information-architecture ADRs — state separation, ERC lifecycle, "
                             "identifiers, envelope, and the Redis-backed stores. None open in this domain.")

    d.final_slide("Information architecture — summary",
                  "Four separated states · validated provenanced ERC · bounded batching · authorization-aware cache",
                  notes="Information is typed, provenanced, freshness-bounded and authorization-aware "
                        "end-to-end — ERC is the disciplined enterprise-context boundary.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
