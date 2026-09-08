#!/usr/bin/env python3
"""Deck 08 — Cost & FinOps (doc 26, cross-cutting)."""
import os
from orion import (Deck, PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE,
                   PURPLE, PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2)
from common import adr_index_slides, stat_cards, two_col, pipeline, kv_panel
from pricing import SNAPSHOT, TECHS, ROLLUP, SOURCES

OUT = os.path.join(os.path.dirname(__file__), "..", "08-cost-finops.pptx")
STAMP = f"Indicative · {SNAPSHOT['region']} · {SNAPSHOT['currency']} · {SNAPSHOT['date']} · verify with FinOps"
COLS = [CYAN, GREEN, YELLOW, PINK, VIOLET, BLUE, PURPLE]


def _fit_logo(d, s, logo, right, top, maxw, maxh):
    from PIL import Image
    import os as _os
    from orion import LOGOS
    path = logo if _os.path.exists(logo) else _os.path.join(LOGOS, f"{logo}.png")
    iw, ih = Image.open(path).size
    ar = iw / ih
    h = maxh; w = h * ar
    if w > maxw:
        w = maxw; h = w / ar
    d.image(s, path, right - w, top + (maxh - h) / 2, w=w, h=h)


def cost_tech(d, key):
    e = TECHS[key]
    s = d.content_slide(e["name"], f"ADR {e['adr']}  ·  {STAMP}")
    _fit_logo(d, s, e["logo"], right=12.4, top=0.42, maxw=1.5, maxh=0.7)
    # drivers panel
    kv_panel(d, s, "Cost drivers", e["drivers"], 0.9, 1.75, 6.1, 3.2, col=CYAN, size=12)
    d.box(s, "Formula:  " + e["formula"], 0.9, 5.1, 6.1, 0.7, fill=PANEL2, line=MUTED,
          textcolor=GREY, size=12, bold=False, align=PP_ALIGN.LEFT)
    # L/E/H cards
    labels = ["Low", "Expected", "High"]
    lcol = [BLUE, GREEN, PINK]
    y = 1.75
    for i, cell in enumerate(e["leh"]):
        amount, _, sub = cell.partition("\n")
        d.box(s, "", 7.3, y, 5.1, 1.0, fill=PANEL, line=lcol[i], line_w=1.2)
        d.text(s, labels[i], 7.5, y + 0.1, 1.6, 0.8, size=13, color=lcol[i], bold=True, anchor=1)
        d.text(s, amount, 8.9, y + 0.06, 1.8, 0.9, size=22, color=WHITE, bold=True, anchor=1)
        d.text(s, sub, 10.75, y + 0.16, 1.55, 0.8, size=11, color=GREY, anchor=1)
        y += 1.1
    d.text(s, "Optimization levers", 7.3, 5.15, 5.1, 0.35, size=13, color=YELLOW, bold=True)
    d.bullets(s, e["levers"], 7.3, 5.5, 5.1, 1.4, size=11, gap=5)
    return s


def cost_bars(d, s, labels, values, y0=1.95, x0=3.6, maxlen=8.2, color=GREEN):
    vmax = max(values)
    n = len(labels)
    row_h = min(0.5, (6.8 - y0) / n)
    y = y0
    for lab, val in zip(labels, values):
        d.text(s, lab.replace("\n", " "), 0.6, y - 0.02, 2.9, row_h, size=10.5,
               color=GREY, anchor=1)
        w = maxlen * val / vmax
        d.box(s, "", x0, y + 0.04, max(w, 0.05), row_h - 0.14, fill=color, line=None,
              shape=MSO_SHAPE.RECTANGLE)
        d.text(s, f"${val:,}", x0 + max(w, 0.05) + 0.1, y - 0.02, 1.4, row_h, size=10.5,
               color=WHITE, bold=True, anchor=1)
        y += row_h


def build():
    d = Deck()
    d.title_slide("08 · Cost & FinOps",
                  "Per-technology cost model · scenarios · budget controls  (doc 26)",
                  notes="The cost story per technology. Every figure is an indicative public list "
                        "price, USD, Azure UK South, captured 2026-09-08 — directional for ARB, to be "
                        "confirmed by FinOps and converted to GBP + VAT. Pricing lives in a versioned "
                        "data file, never in application code (doc 26 §138).")

    s = d.content_slide("The cost model", "doc 26 §74 · total cost decomposition")
    d.box(s, "Total = Infrastructure + Model/SLM + Embedding + RAG/Vector + API/Integration\n"
             "+ Service Bus + Storage + Network + Observability + Engineering-AI",
          0.9, 1.9, 11.5, 1.3, fill=PANEL, line=YELLOW, size=15)
    d.bullets(s, [
        "Cost is measured per workflow and per successful outcome — not only per request.",
        "Allocation dimensions: environment · component · workflow · agent · model · team · capability.",
        "Cost tags: application=pff-fa-ai · environment=prod · component=ai-runtime · workflow=affiliation.",
        "Optimize without weakening security, authorization, correctness, AI quality or guardrails.",
    ], 0.9, 3.5, 11.5, 2.8, size=15, gap=13)
    s.notes_slide.notes_text_frame.text = ("The cost model decomposes into ten categories. The "
        "meaningful unit for agentic work is cost-per-workflow / per-successful-affiliation. Everything "
        "is tagged and allocable. Optimization never trades away security or quality.")

    s = d.content_slide("Cost drivers & allocation", "what actually moves the bill")
    two_col(d, s,
            "Highest-impact variables", [
                "SLM tokens & GPU hours (dominant lever).",
                "RAG/embedding volume & re-index frequency.",
                "Vector search units; observability trace/log volume.",
                "Retry amplification & agent loops (bounded — deck 02).",
            ],
            "Allocation & tags", [
                "Per environment / workflow / agent / model.",
                "Cost tags on every resource.",
                "Langfuse gives per-trace token & cost telemetry.",
                "Enables cost-per-successful-affiliation.",
            ])
    s.notes_slide.notes_text_frame.text = ("SLM and GPU dominate; RAG, vector and observability "
        "volume follow. Bounded retries/loops keep cost predictable. Tagging + Langfuse make cost "
        "allocable to workflow and outcome.")

    # per-technology slides (user asked for each: vector→AI Search, observability→Langfuse, etc.)
    for key in ["slm", "embedding", "vector", "observability", "compute",
                "eventing", "cache", "platform", "aiops"]:
        s = cost_tech(d, key)
        s.notes_slide.notes_text_frame.text = (
            f"{TECHS[key]['name']}: drivers and formula on the left; Low/Expected/High indicative "
            f"monthly on the right; optimization levers below. Figures indicative ({SNAPSHOT['region']}, "
            f"{SNAPSHOT['date']}) — confirm with FinOps.")

    s = d.content_slide("Cost per request / workflow / outcome", "doc 26 §76–79")
    stat_cards(d, s, [
        ("Per request", "narrow view — misleading for agents", MUTED),
        ("Per workflow", "multi-agent, multi-API, RAG, SLM", CYAN),
        ("Per outcome", "per successful affiliation — the true unit", GREEN),
        ("Per club/org", "where permitted, access-controlled", BLUE),
    ], y=2.1, h=2.0)
    d.text(s, "A single affiliation workflow may span multiple agents, enterprise API calls, RAG "
              "queries and model calls — so cost-per-successful-affiliation is the metric that matters.",
           0.9, 4.5, 11.5, 1.0, size=15, color=GREY)
    s.notes_slide.notes_text_frame.text = ("Report cost per workflow and per successful outcome. "
        "Per-request cost understates agentic workloads that fan out across agents/APIs/RAG/SLM.")

    s = d.content_slide("Budget controls & guardrails", "doc 26 §90–98")
    two_col(d, s,
            "Budgets & alerts", [
                "Budgets per month / environment / workflow / model / evaluation.",
                "Alerts at 50 / 75 / 90 / 100 %.",
                "Cost anomaly detection (token/GPU/API spikes).",
            ],
            "Cost guardrails & routing", [
                "Max tokens/model-calls/tool-calls/retries per workflow.",
                "On budget breach: stop · degrade · route to cheaper approved model.",
                "Model routing optimises cost, latency & quality together.",
            ])
    s.notes_slide.notes_text_frame.text = ("Budgets and alerts at 50/75/90/100%, anomaly detection, "
        "and configurable cost guardrails. On breach we degrade or route to a cheaper approved model — "
        "never compromise business-critical correctness.")

    s = d.content_slide("Scenario rollup — indicative monthly", STAMP)
    d.table(s, [
        ["Scenario", "Profile", "Indicative total / month"],
        ["Low", "pilot · hosted SLM · minimal infra", f"${sum(ROLLUP['low']):,}"],
        ["Expected", "production season · self-hosted SLM", f"${sum(ROLLUP['expected']):,}"],
        ["High", "peak window · GPU HA · full observability", f"${sum(ROLLUP['high']):,}"],
    ], 0.9, 1.95, 11.5, 2.0, col_widths=[2.0, 6.0, 3.5], font_size=14)
    d.text(s, "Totals are the sum of the per-technology lines. SLM/GPU dominates the Expected and High "
              "scenarios — the single biggest lever, and the reason the vLLM decision (deck 09) matters for cost.",
           0.9, 4.2, 11.5, 1.2, size=14, color=GREY)
    d.text(s, "Not a quote. USD indicative list, ex-VAT — convert to GBP and add VAT with FinOps.",
           0.9, 6.7, 11.5, 0.4, size=12, color=YELLOW, bold=True)
    s.notes_slide.notes_text_frame.text = ("Three scenarios. Expected ≈ ${:,}/mo, dominated by "
        "self-hosted GPU. Low uses hosted HF and minimal infra; High assumes GPU HA at peak. Directional "
        "only.".format(sum(ROLLUP['expected'])))

    s = d.content_slide("Expected monthly cost by technology", STAMP)
    cost_bars(d, s, ROLLUP["labels"], ROLLUP["expected"], color=GREEN)
    s.notes_slide.notes_text_frame.text = ("Expected-scenario breakdown. The SLM/GPU bar dwarfs the "
        "rest — optimisation effort (batching, right-sizing, routing) targets it first. Everything else "
        "is comparatively small and stable.")

    s = d.content_slide("Pricing sources & caveats", SNAPSHOT["date"])
    d.bullets(s, [
        f"Region: {SNAPSHOT['region']}   ·   Currency: {SNAPSHOT['currency']}   ·   Snapshot: {SNAPSHOT['date']}   ·   Pricing version {SNAPSHOT['version']}",
        "All figures are INDICATIVE public list prices for directional planning — not a quote or commitment.",
        "Convert to GBP and add VAT; apply enterprise agreement / reservation discounts with FinOps.",
        "Pricing is maintained in a versioned data file (pricing.py), never hard-coded in application logic (doc 26 §138).",
    ], 0.9, 1.95, 11.5, 2.6, size=14, gap=12)
    d.text(s, "Anchored to:", 0.9, 4.8, 11.5, 0.35, size=13, color=YELLOW, bold=True)
    d.bullets(s, SOURCES, 0.9, 5.2, 11.5, 1.6, size=12, gap=6)
    s.notes_slide.notes_text_frame.text = ("Transparency slide: region, currency, date, version and "
        "the public sources each figure is anchored to. FinOps confirms with our enterprise agreement.")

    d.final_slide("Cost & FinOps — summary",
                  "SLM/GPU dominates · measure per outcome · budgets + guardrails + routing · verify with FinOps",
                  notes="Takeaway: cost is dominated by the SLM/GPU choice, measured per successful "
                        "outcome, and controlled by budgets, guardrails and model routing. Figures are "
                        "indicative pending FinOps confirmation.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
