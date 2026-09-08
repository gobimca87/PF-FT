#!/usr/bin/env python3
"""Deck 09 — Open Decisions & ARB sign-off asks (5 Proposed ADRs), FA light theme."""
import os
from fa import (Deck, PP_ALIGN, MSO_SHAPE, MSO_ANCHOR,
                NAVY, NAVY_DEEP, BLUE, GOLD, GREY, WHITE, MUTEDBLUE, CARD, CARD_LINE,
                CX0, CX1, CW)

OUT = os.path.join(os.path.dirname(__file__), "..", "09-open-decisions-arb-asks.pptx")

DECISIONS = [
    {"id": "ADR-D3-23", "title": "Embedding model selection",
     "rec": "HF-hosted general-purpose 768-dim (bge-base-en-v1.5 class); fallback 1024-dim",
     "why": "Chosen by PFF-FA retrieval evaluation, not reputation (doc 14 §13).",
     "await": "Recall@5 ≥ 0.90 evaluation, then ARB sign-off",
     "impact": "Dimension drives vector storage cost & recall (deck 03/08).", "phase": "8"},
    {"id": "ADR-D3-24", "title": "Vector store selection",
     "rec": "Azure AI Search (vector + hybrid); fallback pgvector on Azure Postgres",
     "why": "Managed, hybrid retrieval, Azure-native security & scaling.",
     "await": "ARB sign-off",
     "impact": "≈ $245/SU/mo; scales with replicas × partitions (deck 08).", "phase": "8"},
    {"id": "ADR-D5-10", "title": "Self-hosted SLM serving stack",
     "rec": "vLLM on AKS GPU; fallbacks Azure ML / TGI / Triton",
     "why": "Throughput & cost control for the self-hosted target phase.",
     "await": "throughput/latency/quality benchmark on chosen model + SKU, then ARB",
     "impact": "Dominant cost line — GPU-hours ÷ tokens (deck 05/08).", "phase": "20"},
    {"id": "ADR-D3-28", "title": "Quality-gated refinement loop",
     "rec": "Deterministic score → regenerate/escalate up a bounded model ladder; strict mode for governance-critical classes",
     "why": "Runtime quality control, opt-in per task class (config/base/refinement.yaml).",
     "await": "ARB sign-off (AI Governance Lead on strict-class list) + Phase 20 latency/cost benchmark",
     "impact": "Trades latency/cost for quality — needs a benchmarked budget (deck 08).", "phase": "16, 20"},
    {"id": "ADR-D6-19", "title": "SLM input masking regime",
     "rec": "External SLM: mandatory fail-closed mask/tokenise-all; self-hosted: raw or masked; reversible token vault",
     "why": "Strengthens D6-07 into a testable, binary data-protection default.",
     "await": "ARB sign-off (DPO owner, DPIA update) + Phase 20 vault sizing",
     "impact": "No raw PII/records egress; special-category & children's data hard-blocked (deck 06).", "phase": "6, 20"},
]


def decision_slide(d, dec):
    s = d.content_slide(f"{dec['id']} · {dec['title']}", kicker="Proposed · needs ARB sign-off",
                        subtitle="Build-default recommendation — status Proposed, awaiting the evidence/sign-off named")
    d.kv_panel(s, "Recommendation (working default)", [
        ("Recommendation", dec["rec"]),
        ("Why", dec["why"]),
        ("Cost / latency impact", dec["impact"]),
    ], CX0, 1.85, 7.0, 4.5, col=BLUE)
    d.card(s, 9.25, 1.85, 3.4, 2.0)
    d.text(s, "AWAITING", 9.5, 2.0, 3.0, 0.35, size=13, color=BLUE, bold=True)
    d.text(s, dec["await"], 9.5, 2.4, 3.05, 1.35, size=12.5, color=NAVY)
    d.box(s, f"Gated at\nPhase {dec['phase']}", 9.25, 3.95, 3.4, 0.9, style="navy", size=14)
    d.box(s, "THE ASK:  ratify, or direct the evidence you need to ratify",
          9.25, 4.95, 3.4, 1.4, style="accent", size=13)
    d.set_notes(s, f"{dec['id']} {dec['title']}: we build against the recommendation now. Proposed, "
                   f"not Accepted — awaiting {dec['await']} (Phase {dec['phase']}). Ask: ratify, or tell "
                   f"us what evidence you need. A deviation requires a superseding ADR.")


def build():
    d = Deck()
    d.title_slide("Open Decisions", "& ARB Asks",
                  "The 5 Proposed decisions we need the Architecture Review Board to ratify",
                  kicker="Deck 09 · Decisions",
                  notes="The action deck. 145 ADRs are governed; 140 Accepted; 5 remain Proposed with a "
                        "stated recommendation we build against. We need ARB to ratify them or direct the "
                        "evidence required.")

    s = d.content_slide("How an open decision closes", kicker="ADR-D0-04",
                        subtitle="The governance process")
    d.pipeline(s, [("Recommend", "ADR states default"), ("Build", "against recommendation"),
                   ("Evidence", "eval / benchmark"), ("ARB sign-off", "named approver"),
                   ("Accepted", "new version, register")], y=2.7, h=1.05)
    d.bullets(s, [
        "Each Proposed ADR carries a complete CMMI-DAR evaluation and a stated recommendation.",
        "We build against the recommendation now; a deviation requires a superseding ADR — never a silent change.",
        "When the evidence lands or the approver signs off, status flips Proposed → Accepted.",
    ], CX0, 4.3, CW, 1.8, size=14, gap=11)
    d.set_notes(s, "The process (D0-04): recommend → build → produce evidence → ARB sign-off → Accepted.")

    s = d.content_slide("Decision status board", kicker="145 ADRs · 9 domains")
    d.stat_cards(s, [("145", "total governed ADRs"), ("140", "Accepted"),
                     ("5", "Proposed — need ARB"), ("0", "rejected / blocked")], y=1.95, h=1.55)
    d.table(s, [
        ["Proposed ADR", "Decision", "Gate"],
        ["ADR-D3-23", "Embedding model (768-dim)", "Phase 8"],
        ["ADR-D3-24", "Vector store (Azure AI Search)", "Phase 8"],
        ["ADR-D5-10", "Self-hosted SLM (vLLM)", "Phase 20"],
        ["ADR-D3-28", "Quality-gated refinement loop", "Phase 16, 20"],
        ["ADR-D6-19", "SLM input masking regime", "Phase 6, 20"],
    ], CX0, 3.9, CW, 2.6, col_widths=[2.4, 6.4, 2.5], font_size=12.5)
    d.set_notes(s, "Five open decisions, each gated at a build phase; two gate at Phase 8, the rest at "
                   "16/20; none are blocked.")

    for dec in DECISIONS:
        decision_slide(d, dec)

    s = d.content_slide("Sequencing — what we need, when", kicker="Align sign-off to build phases")
    d.table(s, [
        ["Phase", "Decision(s)", "What ARB is asked for"],
        ["Phase 6", "D6-19 masking regime", "DPO sign-off + DPIA update"],
        ["Phase 8", "D3-23 embedding · D3-24 vector store", "ratify after Recall@5 eval / ratify now"],
        ["Phase 16", "D3-28 refinement loop", "endorse strict-class list"],
        ["Phase 20", "D5-10 vLLM · D3-28 · D6-19", "ratify after benchmarks (latency/cost/vault)"],
    ], CX0, 1.95, CW, 2.6, col_widths=[1.5, 5.0, 4.35], font_size=13)
    d.text(s, "Earliest need first: the masking regime (Phase 6) and the Phase 8 data decisions are the "
              "nearest gates — the vLLM & refinement benchmarks land at Phase 20.",
           CX0, 4.9, CW, 1.0, size=14, color=GREY)
    d.set_notes(s, "Sequenced asks: masking (DPO/DPIA) earliest and most sensitive; the Phase-8 data "
                   "decisions next; vLLM and refinement follow their Phase-20 benchmarks.")

    d.final_slide("What we need from the ARB today",
                  "Ratify the 5 · or name the evidence · endorse the cost model (deck 08) · note the architecture",
                  notes="Close: ratify the five decisions or name the evidence needed; endorse the cost "
                        "model and budget controls; record any challenges to the architecture. Thank you.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
