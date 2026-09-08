#!/usr/bin/env python3
"""Deck 04 — Information, Context & Data (D4)."""
import os
from orion import (Deck, PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE,
                   PURPLE, PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2)
from common import adrs_for, adr_index_slides, stat_cards, two_col, pipeline, kv_panel

OUT = os.path.join(os.path.dirname(__file__), "..", "04-information-context-data.pptx")


def batch_diagram(d, s):
    d.text(s, "100 teams  ÷  20 per loop  =  5 controlled batches  →  aggregate",
           0.9, 1.95, 11.5, 0.4, size=15, color=CYAN, bold=True)
    x = 0.9; y = 2.6; w = 1.75; h = 0.85; gap = 0.28
    for i in range(5):
        d.box(s, f"Batch {i+1}\n20 teams", x, y, w, h, fill=PANEL2, line=BLUE, size=12)
        d.connector(s, x + w, y + h/2, 10.2, 3.9, color=GREY, width=1.1, arrow=(i == 2))
        x += w + gap
    d.box(s, "ERC\nAggregator", 10.2, 3.55, 2.1, 0.9, fill=PANEL, line=GREEN, size=13)
    d.bullets(s, [
        "Batch size is tuned to API limits, context window, memory, latency and token cost — not increased blindly.",
        "Same principle for 100+ officials. Batches parallelise only when enterprise operations are independent.",
        "Intermediate objects released after aggregation to bound memory (deck 08).",
    ], 0.9, 4.8, 11.5, 1.8, size=14, gap=11)


def build():
    d = Deck()
    d.title_slide("04 · Information, Context & Data",
                  "Four states · ERC · identifiers · state store · memory · cache  (D4, 13 ADRs)",
                  notes="How the platform models and moves information: the four separated states, the "
                        "Enterprise Runtime Context (ERC), canonical identifiers, and the Redis-backed "
                        "state/memory/cache stores. 13 ADRs in D4.")

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

    s = d.content_slide("Four state concepts — strictly separate", "D4-01")
    quad = [("Conversation State", "turns, messages, intent", CYAN),
            ("Session State", "auth context, correlation, TTL", BLUE),
            ("Workflow / Agent State", "graph state, steps, HIL, checkpoints", GREEN),
            ("Enterprise Business State", "system-of-record truth — owned by PFF", PINK)]
    xs = [0.9, 6.85]; ys = [2.0, 4.35]
    for i, (t, sub, col) in enumerate(quad):
        x = xs[i % 2]; y = ys[i // 2]
        d.box(s, "", x, y, 5.55, 2.05, fill=PANEL, line=col, line_w=1.25)
        d.text(s, t, x + 0.3, y + 0.25, 5.0, 0.5, size=18, color=col, bold=True)
        d.text(s, sub, x + 0.3, y + 0.95, 5.0, 0.9, size=13, color=GREY)
    s.notes_slide.notes_text_frame.text = ("Never conflated in code. Enterprise business state is "
        "owned entirely by PFF; the AI holds only conversation, session and workflow state.")

    s = d.content_slide("ERC — Enterprise Runtime Context", "D4-02 / D4-03")
    two_col(d, s,
            "Schema, identity, versioning", [
                "ERC is the validated, typed snapshot of enterprise context for a workflow.",
                "Stable schema with identity & versioning (D4-02).",
                "Pydantic at the boundary; never raw pass-through.",
            ],
            "Provenance, freshness, authority", [
                "Every ERC value carries provenance & freshness (D4-03).",
                "ERC sits just below Enterprise API/Event in the precedence chain.",
                "A PARTIAL ERC is never presented as COMPLETE.",
            ])
    s.notes_slide.notes_text_frame.text = ("ERC is the contextual boundary between the enterprise and "
        "the AI. It is validated, versioned, provenanced and freshness-tracked — the second-highest "
        "trust source after live enterprise APIs/events.")

    s = d.content_slide("ERC collection & batching", "D4-04 · controlled, bounded")
    batch_diagram(d, s)
    s.notes_slide.notes_text_frame.text = ("Large entity sets (100+ teams/officials) are gathered in "
        "controlled batches of ~20 and aggregated. Batch size is a tuned parameter (config/base/batching.yaml), "
        "not a blind maximum. This is core to both performance and cost (deck 08).")

    s = d.content_slide("ERC partial failure & refresh", "D4-05 / D4-06")
    two_col(d, s,
            "Partial-failure semantics", [
                "If some entities fail, ERC is explicitly PARTIAL — never silently treated as complete.",
                "The workflow decides: retry, degrade, or surface to the user.",
                "Adam states clearly what could not be gathered.",
            ],
            "Invalidation & event refresh", [
                "Enterprise events invalidate stale ERC entries (D4-06).",
                "Refresh is event-driven via Service Bus (deck 02).",
                "Freshness bounds prevent acting on outdated context.",
            ])
    s.notes_slide.notes_text_frame.text = ("Partial ERC is a first-class, explicit state. Event-driven "
        "invalidation keeps context fresh without polling.")

    s = d.content_slide("Data & knowledge architecture", "D4-07 / D4-08")
    two_col(d, s,
            "Data & knowledge", [
                "Clear split: authoritative enterprise data vs. RAG knowledge corpus.",
                "Knowledge is grounding only; authority stays with the enterprise.",
            ],
            "Canonical identifiers & reference data", [
                "Canonical IDs (club, team, official, season) resolved consistently.",
                "Reference data is versioned and cache-eligible where safe.",
                "IDs are never invented — resolved from the enterprise.",
            ])
    s.notes_slide.notes_text_frame.text = ("A clean separation of authoritative data and knowledge, "
        "with canonical identifiers resolved from the enterprise — never fabricated.")

    s = d.content_slide("Metadata envelope & error codes", "D4-09")
    d.bullets(s, [
        "A consistent metadata response envelope wraps enterprise/tool responses: status, provenance, freshness, correlation, and typed error codes.",
        "Error codes map to the PlatformError hierarchy (deck 07) so failures are handled uniformly.",
        "This envelope is what lets Adam communicate precise, factual state and next actions.",
    ], 0.9, 2.0, 11.5, 3.2, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("A uniform envelope carries status, provenance, freshness "
        "and typed error codes — the substrate for factual communication and consistent error handling.")

    s = d.content_slide("State store — Azure Managed Redis", "D4-10 · Accepted")
    d.image(s, "redis", 0.95, 2.1, h=1.3)
    kv_panel(d, s, "Resolved: Azure Managed Redis", [
        ("Holds", "conversation & session state, workflow checkpoints, cache"),
        ("Why", "managed, low-latency, Azure-native, TTL & eviction"),
        ("Status", "Accepted — supersedes the earlier ADR-0004 draft"),
    ], 3.3, 1.95, 9.0, 2.5, col=PINK)
    d.text(s, "Memory / session / cache store is resolved — not an open decision. Cost drivers (SKU, memory) in deck 08.",
           0.9, 4.7, 11.5, 0.8, size=14, color=GREY)
    s.notes_slide.notes_text_frame.text = ("The state/session/cache store decision is Accepted: Azure "
        "Managed Redis. It backs conversation/session state, workflow checkpoints and cache.")

    s = d.content_slide("Memory architecture", "D4-11")
    d.bullets(s, [
        "Memory service with policy-driven retention, retrieval and ranking; summarization for long conversations.",
        "Protects important authoritative context from being summarised away.",
        "Storage-technology-agnostic interface (Redis-backed); observable read/write costs (deck 08).",
    ], 0.9, 2.0, 11.5, 3.2, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("Memory is policy-driven: retention, retrieval, ranking, "
        "summarization — with explicit protection for authoritative context.")

    s = d.content_slide("Cache architecture & scope", "D4-12 / D4-13")
    two_col(d, s,
            "Cache design", [
                "TTL, eviction, invalidation, serialization, protection.",
                "Cache only where freshness & authorization allow.",
                "A cache stays only when benefit > operational cost (deck 08).",
            ],
            "Authorization-aware & global scope", [
                "Cache keys account for access scope — never cross authorization contexts.",
                "Platform-global entries (reference data, portal metadata) scoped explicitly (D4-13).",
                "Transactional operations are not cached unless provably safe.",
            ])
    s.notes_slide.notes_text_frame.text = ("Caching is authorization-aware and freshness-bounded. "
        "Global entries (reference/portal metadata) have an explicit scope. Never serve cached data "
        "across incompatible authorization contexts.")

    adr_index_slides(d, "ADR index — Information (D4)", adrs_for(4),
                     notes="All 13 information-architecture ADRs — state separation, ERC lifecycle, "
                           "identifiers, envelope, and the Redis-backed stores. None open in this domain.")

    d.final_slide("Information architecture — summary",
                  "Four separated states · validated provenanced ERC · bounded batching · authorization-aware cache",
                  notes="Takeaway: information is typed, provenanced, freshness-bounded and "
                        "authorization-aware end-to-end — ERC is the disciplined enterprise-context boundary.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
