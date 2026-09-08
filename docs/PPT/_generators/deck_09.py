#!/usr/bin/env python3
"""Deck 09 — Open Decisions & ARB sign-off asks (the 5 Proposed ADRs)."""
import os
from orion import (Deck, PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE,
                   PURPLE, PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2)
from common import stat_cards, two_col, pipeline, kv_panel

OUT = os.path.join(os.path.dirname(__file__), "..", "09-open-decisions-arb-asks.pptx")

DECISIONS = [
    {"id": "ADR-D3-23", "title": "Embedding model selection",
     "rec": "HF-hosted general-purpose 768-dim (bge-base-en-v1.5 class); fallback 1024-dim",
     "why": "Chosen by PFF-FA retrieval evaluation, not reputation (doc 14 §13).",
     "await": "Recall@5 ≥ 0.90 evaluation, then ARB sign-off",
     "impact": "Dimension drives vector storage cost & recall (deck 03/08).",
     "phase": "8", "col": CYAN},
    {"id": "ADR-D3-24", "title": "Vector store selection",
     "rec": "Azure AI Search (vector + hybrid); fallback pgvector on Azure Postgres",
     "why": "Managed, hybrid retrieval, Azure-native security & scaling.",
     "await": "ARB sign-off",
     "impact": "~$245/SU/mo; scales with replicas×partitions (deck 08).",
     "phase": "8", "col": GREEN},
    {"id": "ADR-D5-10", "title": "Self-hosted SLM serving stack",
     "rec": "vLLM on AKS GPU; fallbacks Azure ML / TGI / Triton",
     "why": "Throughput & cost control for the self-hosted target phase.",
     "await": "throughput/latency/quality benchmark on chosen model + SKU, then ARB",
     "impact": "Dominant cost line — GPU-hours ÷ tokens (deck 05/08).",
     "phase": "20", "col": VIOLET},
    {"id": "ADR-D3-28", "title": "Quality-gated refinement loop",
     "rec": "Deterministic score → regenerate/escalate up a bounded model ladder; strict mode for governance-critical classes",
     "why": "Runtime quality control, opt-in per task class (config/base/refinement.yaml).",
     "await": "ARB sign-off (AI Governance Lead on strict-class list) + Phase 20 latency/cost benchmark",
     "impact": "Trades latency/cost for quality — needs a benchmarked budget (deck 08).",
     "phase": "16, 20", "col": YELLOW},
    {"id": "ADR-D6-19", "title": "SLM input masking regime",
     "rec": "External SLM: mandatory fail-closed mask/tokenise-all; self-hosted: raw or masked; reversible token vault",
     "why": "Strengthens D6-07 into a testable, binary data-protection default.",
     "await": "ARB sign-off (DPO owner, DPIA update) + Phase 20 vault sizing",
     "impact": "No raw PII/records egress; special-category & children's data hard-blocked (deck 06).",
     "phase": "6, 20", "col": PINK},
]


def decision_slide(d, dec):
    s = d.content_slide(f"{dec['id']} · {dec['title']}", "PROPOSED · build-default recommendation · awaiting ARB")
    kv_panel(d, s, "Recommendation (working default)", [
        ("Recommendation", dec["rec"]),
        ("Why", dec["why"]),
        ("Cost / latency impact", dec["impact"]),
    ], 0.9, 1.8, 7.2, 4.6, col=dec["col"], size=13)
    d.box(s, "", 8.4, 1.8, 4.0, 2.0, fill=PANEL, line=YELLOW, line_w=1.3)
    d.text(s, "AWAITING", 8.65, 1.95, 3.5, 0.35, size=13, color=YELLOW, bold=True)
    d.text(s, dec["await"], 8.65, 2.35, 3.55, 1.35, size=13, color=WHITE, anchor=1)
    d.box(s, f"Gated at\nPhase {dec['phase']}", 8.4, 4.0, 4.0, 1.0, fill=PANEL2,
          line=dec["col"], textcolor=WHITE, size=14)
    d.box(s, "THE ASK:  ratify, or direct the evidence you need to ratify",
          8.4, 5.15, 4.0, 1.2, fill=PANEL2, line=PINK, textcolor=PINK, size=13)
    s.notes_slide.notes_text_frame.text = (
        f"{dec['id']} {dec['title']}: we build against the recommendation now. It is Proposed, not "
        f"Accepted — awaiting {dec['await']} (gated at Phase {dec['phase']}). Ask: ratify it, or tell "
        f"us what evidence you need. A deviation from the recommendation requires a superseding ADR.")
    return s


def build():
    d = Deck()
    d.title_slide("09 · Open Decisions & ARB Asks",
                  "The 5 Proposed decisions we need the Architecture Review Board to ratify",
                  notes="This is the action deck. 145 ADRs are governed; 140 are Accepted; 5 remain "
                        "Proposed with a stated recommendation we build against. We need ARB to ratify "
                        "them or direct the evidence required.")

    s = d.content_slide("How an open decision closes", "ADR-D0-04 · the governance process")
    pipeline(d, s, [("Recommend", "ADR states default"), ("Build", "against recommendation"),
                    ("Evidence", "eval / benchmark"), ("ARB sign-off", "named approver"),
                    ("Accepted", "new version, register updated")], y=2.6, h=1.0,
             colors=[CYAN, BLUE, YELLOW, GREEN, PURPLE])
    d.bullets(s, [
        "Each Proposed ADR carries a complete CMMI-DAR evaluation and a stated recommendation.",
        "We build against the recommendation now; a deviation requires a superseding ADR — never a silent change.",
        "When the evidence lands or the approver signs off, status flips Proposed → Accepted.",
    ], 0.9, 4.2, 11.5, 1.9, size=14, gap=11)
    s.notes_slide.notes_text_frame.text = ("The process (D0-04): recommend → build → produce evidence "
        "→ ARB sign-off → Accepted. Building against a recommendation is deliberate and reversible only "
        "via a superseding ADR.")

    s = d.content_slide("Decision status board", "145 ADRs · 9 domains")
    stat_cards(d, s, [
        ("145", "total governed ADRs", CYAN),
        ("140", "Accepted", GREEN),
        ("5", "Proposed — need ARB", YELLOW),
        ("0", "rejected / blocked", MUTED),
    ], y=2.0, h=1.7)
    d.table(s, [
        ["Proposed ADR", "Decision", "Gate"],
        ["ADR-D3-23", "Embedding model (768-dim)", "Phase 8"],
        ["ADR-D3-24", "Vector store (Azure AI Search)", "Phase 8"],
        ["ADR-D5-10", "Self-hosted SLM (vLLM)", "Phase 20"],
        ["ADR-D3-28", "Quality-gated refinement loop", "Phase 16, 20"],
        ["ADR-D6-19", "SLM input masking regime", "Phase 6, 20"],
    ], 0.9, 4.0, 11.5, 2.6, col_widths=[2.4, 6.6, 2.5], font_size=13)
    s.notes_slide.notes_text_frame.text = ("Five open decisions, each gated at a build phase. Two "
        "(embedding, vector) gate at Phase 8; the rest at 16/20. None are blocked — they await evidence "
        "or sign-off.")

    for dec in DECISIONS:
        decision_slide(d, dec)

    s = d.content_slide("Sequencing — what we need, when", "align sign-off to build phases")
    d.table(s, [
        ["Phase", "Decision(s)", "What ARB is asked for"],
        ["Phase 6", "D6-19 masking regime", "DPO sign-off + DPIA update"],
        ["Phase 8", "D3-23 embedding · D3-24 vector store", "ratify after Recall@5 eval / ratify now"],
        ["Phase 16", "D3-28 refinement loop", "endorse strict-class list"],
        ["Phase 20", "D5-10 vLLM · D3-28 · D6-19", "ratify after benchmarks (latency/cost/vault)"],
    ], 0.9, 1.95, 11.5, 2.6, col_widths=[1.6, 5.0, 4.9], font_size=13)
    d.text(s, "Earliest need first: the masking regime (Phase 6) and the Phase 8 data decisions are the "
              "nearest gates — the vLLM & refinement benchmarks land at Phase 20.",
           0.9, 4.9, 11.5, 1.0, size=14, color=GREY)
    s.notes_slide.notes_text_frame.text = ("Sequenced asks: masking (DPO/DPIA) is the earliest and most "
        "sensitive; the Phase-8 data decisions next; vLLM and refinement follow their Phase-20 benchmarks.")

    d.final_slide("What we need from the ARB today",
                  "Ratify the 5 · or name the evidence · endorse the cost model (deck 08) · note the architecture",
                  notes="Close: ratify the five decisions or name the evidence you need; endorse the "
                        "cost model and budget controls; and record any challenges to the architecture "
                        "across the domain decks. Thank you.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
