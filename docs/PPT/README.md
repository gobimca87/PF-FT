# PFF AI — Technical ARB Presentation Suite

A suite of **10 PowerPoint decks** (~145 slides) presenting the PFF-FA Enterprise Agentic AI
platform (**PFF Chat AI**) to the **Architecture Review Board**, from a technical perspective.
Built on the organisation **Orion FA** template — **blue & white enterprise theme** (white
background, navy sidebar with the FA crest, professional blue accent, Cambria/Calibri).

> **Design intent:** short on the slide, deep in the speaker notes — the presenter narrates;
> the slides are the scaffold. Every one of the **145 ADRs** and all **29 MD spec docs** is
> covered. Cost is broken down **per technology**.

## Decks (present in this order)

| # | File | Scope | ADR domain(s) |
|---|------|-------|---------------|
| 00 | `00-overview.pptx` | Whole-system technical overview, Golden Rule, master architecture, tech & cost headlines | all |
| 01 | `01-business-architecture.pptx` | Governance, scope, PFF Chat AI persona, workflows, value | D0 · D1 · D8 |
| 02 | `02-application-orchestration.pptx` | Layering, runtime, Supervisor, LangGraph, Harness, integration, eventing | D2 |
| 03 | `03-ai-architecture.pptx` | Agents, prompts, SLM, RAG, embeddings, refinement | D3 |
| 04 | `04-information-context-data.pptx` | Four states, ERC, identifiers, Redis state/memory/cache | D4 |
| 05 | `05-technology-infrastructure.pptx` | Azure, AKS, APIM, Key Vault, vLLM/GPU, delivery + infra topology | D5 |
| 06 | `06-security-governance.pptx` | Zero-trust, masking, guardrails, GDPR, audit | D6 |
| 07 | `07-operations-quality.pptx` | Langfuse, SLI/SLO, CI/CD, testing, LLMOps, DR | D7 |
| 08 | `08-cost-finops.pptx` | Per-technology cost model, scenarios, budget controls | doc 26 (all) |
| 09 | `09-open-decisions-arb-asks.pptx` | The 5 Proposed decisions needing ARB sign-off | — |

## ADR coverage (145 across 9 domains)

Each domain deck ends with a compact **ADR index** covering every ADR in that domain
(`◆` = Proposed), plus full deep-dive slides for the architecturally significant / open ones.
`_generators/coverage.py` verifies all 145 appear in the suite.

| Domain | ADRs | Deck |
|---|---|---|
| D0 Decision Programme (4) · D1 Business (12) · D8 Business Value (10) | 26 | 01 |
| D2 Application | 21 | 02 |
| D3 AI | 28 | 03 |
| D4 Information | 13 | 04 |
| D5 Technology | 20 | 05 |
| D6 Security & Governance | 19 | 06 |
| D7 Operations | 18 | 07 |

**5 Proposed decisions (deck 09):** D3-23 embedding model · D3-24 vector store ·
D5-10 self-hosted vLLM · D3-28 refinement loop · D6-19 masking regime.

## MD spec-doc → deck map (29 docs)

| Doc(s) | Deck |
|---|---|
| 0 Affiliation E2E flow · 1–3 Foundation (Architecture, Responsibility Matrix) | 00, 01 |
| 4 Runtime · 5 State Model · 6 Conversation/Session · 7 Agentic Orchestration | 02, 04 |
| 8 ERC · 9 Memory/Cache | 04 |
| 10 Enterprise Integration · 11 Service Bus · 12 Portal Links | 02 |
| 13 RAG · 14 Embedding/Vector · 15 SLM · 16 Prompt Engineering · 18 Guardrails | 03 (18 also 06) |
| 17 Configuration/Versioning | 05 |
| 19 Security · 20 Governance | 06 |
| 21 Evaluation · 22 Testing · 23 Engineering Agents | 07 |
| 24 Observability/Resilience · 25 Infrastructure/Operations · 27 Dev Standards · 28 Ops Runbook | 07 (25 also 05) |
| 26 Performance & Cost | 08 |
| SampleWorkflowchat (PFF Chat AI persona reference) | 01 |

## Template & theme

- Org template preserved verbatim at `_TEMPLATE/Orion_FATemplate.pptx` (the earlier dark Orion
  template is kept at `_TEMPLATE/Orion_Template_V1.0.pptx` for reference only).
- Every deck is **cloned from the FA template** (white background, brand theme), the two sample
  slides stripped, and rebuilt by `_generators/fa.py` with a fixed chrome: a **navy sidebar**
  (`#011E41`) carrying the **FA crest** (recoloured white) + wordmark + page number, and a header
  band (blue eyebrow · Cambria navy title · grey subtitle) on a white canvas.
- **Palette (blue & white, enterprise):** navy headings `#13294B`, sidebar/dark-panel `#011E41`,
  professional blue accent `#2E75B6` (the FA red is deliberately not used), gold highlight
  `#FFC72C`, light cards `#F3F6FA` with a visible `#A9BACE` border, grey body `#5C6B7A`.
- **Fonts:** Cambria (titles / big numbers), Calibri (body / labels).
- Content lives in the `2.05–12.9"` band (clear of the sidebar); all cards have visible borders.
- The dark-theme builder `orion.py` and its `Orion_Template_V1.0.pptx` are retained but unused.

## Cost figures — read this

All monetary figures in deck 08 are **INDICATIVE public list prices**, USD, region **Azure UK
South**, snapshot **2026-09-08** (pricing version 1.0.0). They are **directional for ARB, not a
quote** — convert to GBP, add VAT, and apply enterprise-agreement/reservation discounts with
**FinOps**. Pricing lives in a versioned data file (`_generators/pricing.py`), never in application
code (per doc 26 §138). Sources: Azure pricing pages, Langfuse & Hugging Face pricing.

## Regenerating / re-skinning

All decks are generated programmatically (python-pptx) so the suite stays consistent and is
trivially rebuilt:

```bash
cd docs/PPT/_generators
pip install python-pptx Pillow cairosvg simpleicons markitdown[pptx]
python3 gen_logos.py            # vendor logos -> ../assets/logos
python3 extract_adrs.py         # parse ADRs -> adr_index.json
for n in 00 01 02 03 04 05 06 07 08 09; do python3 deck_$n.py; done
python3 qa.py ../*.pptx         # geometry lint
python3 coverage.py             # all 145 ADRs present
```

- `fa.py` — the shared FA light-theme builder (clones the FA template, draws the navy sidebar +
  crest chrome, palette, and all slide/diagram/table/ADR-index helpers). This is the template for
  every deck.
- `pricing.py` — versioned indicative pricing snapshot (deck 08).
- `gen_logos.py` writes white marks to `assets/logos/`; the navy marks for the white theme are in
  `assets/logos_navy/`; the FA crest variants are `assets/logos/fa_crest_{white,navy}.png`.
- `orion.py` / `common.py` — the earlier dark-theme builder, retained but no longer used.
- To update ADR/doc content, edit the relevant `deck_NN.py` and rerun; nothing is hand-edited in
  the `.pptx`.

> **Note:** in-environment slide-image rendering was unavailable (LibreOffice `soffice` conversion
> is broken in the build sandbox — it fails on any input). QA therefore used `python-pptx`
> structural validation, `markitdown` content checks and a geometry linter. Open the decks in
> PowerPoint for the final visual pass.
