#!/usr/bin/env python3
"""Indicative pricing snapshot for the PFF AI Cost & FinOps deck.

VERSIONED DATA — not application logic (per doc 26 §138: pricing is maintained
outside application code and versioned separately). All figures are INDICATIVE
public list prices, USD, region Azure UK South (nearest published anchors),
captured 2026-09-08. Verify with FinOps/procurement; convert to GBP + add VAT.
"""

SNAPSHOT = {
    "version": "1.0.0",
    "date": "2026-09-08",
    "region": "Azure UK South (indicative)",
    "currency": "USD (indicative list price, ex-VAT)",
}

# Each entry: drivers, formula, monthly Low/Expected/High (USD), optimization levers.
TECHS = {
    "slm": {
        "name": "SLM inference",
        "logo": "huggingface",
        "adr": "D3-13 / D5-10",
        "drivers": [
            ("Hosted phase", "HF Inference — per-token or dedicated endpoint-hours"),
            ("Self-host target", "vLLM on NC24ads_A100_v4 GPU @ ≈$3.67/hr on-demand"),
            ("Key variables", "tokens/workflow, GPU count, utilisation, quantisation"),
        ],
        "formula": "hosted: tokens×rate   |   self-host: GPU-hr ÷ tokens-per-hr",
        "leh": ("$300\nhosted, pilot", "$2,680\n1×A100 24×7", "$5,360\n2×A100 HA"),
        "levers": ["Continuous batching & quantisation (quality-validated)",
                   "Right-size GPU SKU; spot for non-critical (~$0.68/hr)",
                   "Model routing: small model for simple tasks (deck 03)"],
    },
    "embedding": {
        "name": "Embedding", "logo": "huggingface", "adr": "D3-23",
        "drivers": [("Volume", "docs × chunks × tokens"),
                    ("Re-index", "frequency on model/version change"),
                    ("Model", "768-dim general-purpose (recommended)")],
        "formula": "embedding-tokens × rate + re-index passes",
        "leh": ("$50\nsmall corpus", "$200\nsteady", "$600\nfrequent re-index"),
        "levers": ["Embed only changed documents (incremental)",
                   "Cache embeddings; avoid needless re-embedding",
                   "Don't reduce dimensions without evaluation"],
    },
    "vector": {
        "name": "Vector store — Azure AI Search", "logo": "aisearch", "adr": "D3-24",
        "drivers": [("Tier", "Standard S1 ≈ $245 / search-unit / month"),
                    ("Scale", "search units = replicas × partitions"),
                    ("Load", "index size, query volume, hybrid retrieval")],
        "formula": "search-units × tier-rate  (replicas×partitions)",
        "leh": ("$245\n1 SU (S1)", "$490\n2 SU", "$735\n3 SU"),
        "levers": ["Right-size partitions to index size",
                   "Replicas for QPS/HA only when needed",
                   "Hybrid retrieval tuned; top-K controlled (deck 03)"],
    },
    "observability": {
        "name": "Observability — Langfuse + Azure Monitor", "logo": "langfuse", "adr": "D7-02 / D7-01",
        "drivers": [("Langfuse", "Core $29 / Pro $199 (100k units incl.); overage ~$8/100k"),
                    ("Azure logs", "Log Analytics $2.30/GB after 5 GB free/mo"),
                    ("Volume", "trace/observation count + log GB + retention")],
        "formula": "Langfuse plan + overage  +  log-GB × $2.30",
        "leh": ("$80\nCore + light logs", "$450\nPro + logs", "$1,100\nPro overage + logs"),
        "levers": ["Sample/route high-volume traces",
                   "Tier logs (Basic $0.50/GB) & tune retention",
                   "Avoid excessive logging (perf + cost anti-pattern)"],
    },
    "compute": {
        "name": "Compute — AKS (CPU node pool)", "logo": "aks", "adr": "D5-08 / D5-17",
        "drivers": [("Nodes", "VM SKU × count × hours"),
                    ("Control plane", "AKS Standard ≈ $73/mo"),
                    ("Scaling", "autoscale on CPU/mem/queue; warm minimum")],
        "formula": "node-VM-hours + control-plane + load-balancing",
        "leh": ("$300\nminimal", "$700\nsteady HA", "$1,600\npeak"),
        "levers": ["Autoscale down off-peak (avoid cold starts)",
                   "Right-size node SKUs; bin-pack pods",
                   "Reserved instances for steady baseline"],
    },
    "eventing": {
        "name": "Eventing — Azure Service Bus", "logo": "servicebus", "adr": "D2-16",
        "drivers": [("Standard", "$10/mo base + $0.01 / M operations"),
                    ("Premium", "$677 / messaging-unit / month (dedicated, isolation)"),
                    ("Load", "message volume, MU count")],
        "formula": "Standard base+ops   OR   Premium MU × rate",
        "leh": ("$15\nStandard", "$30\nStandard heavy", "$677\nPremium 1 MU"),
        "levers": ["Standard tier for affiliation volumes",
                   "Batch receive, prefetch, tune concurrency",
                   "Premium only when isolation/latency demands"],
    },
    "cache": {
        "name": "Cache / state — Azure Managed Redis", "logo": "redis", "adr": "D4-10 / D4-12",
        "drivers": [("SKU", "Balanced tier B0 (1 GB) ≈ $13/mo → scales with memory"),
                    ("Memory", "state + session + cache footprint"),
                    ("HA", "replication / zones")],
        "formula": "SKU (memory tier) × HA factor",
        "leh": ("$130\nsmall B-tier", "$300\nmid + HA", "$650\nlarger + zones"),
        "levers": ["TTL & eviction tuned; cache only when benefit > cost",
                   "Authorization-aware keys (no cross-scope reuse)",
                   "Right-size memory to working set"],
    },
    "platform": {
        "name": "Platform — APIM · ACR · Key Vault · Storage/Net", "logo": "apim", "adr": "D5-15 / D5-09 / D5-07",
        "drivers": [("APIM", "Standard v2 ≈ $700/mo (~50M calls incl.) — may be shared enterprise"),
                    ("ACR", "Standard ≈ $20 / Premium ≈ $50 per month"),
                    ("Key Vault + Storage/Net", "per-operation + blob GB + egress")],
        "formula": "APIM tier + ACR tier + KV ops + storage/egress",
        "leh": ("$205\nBasic v2 + small", "$820\nStd v2 + std", "$2,050\n2×APIM + premium"),
        "levers": ["Use shared enterprise APIM allocation where possible",
                   "ACR retention policies; prune images",
                   "Minimise cross-region egress"],
    },
    "aiops": {
        "name": "Evaluation + Engineering-agent spend", "logo": "openai", "adr": "D7-13 / D7-15",
        "drivers": [("Evaluation", "judge/model calls × dataset size × frequency"),
                    ("Engineering agents", "code review, test-gen, security, docs + CI runtime"),
                    ("Refinement", "runtime quality loop escalations (D3-28)")],
        "formula": "eval model-tokens + eng-agent model-tokens + CI minutes",
        "leh": ("$150\nlight", "$700\nsteady", "$1,900\nheavy regression"),
        "levers": ["Cache eval results; run judges only on changes",
                   "Bound refinement escalations (deck 03/09)",
                   "Right-size CI concurrency"],
    },
}

# Rollup monthly totals (USD, indicative) — derived from the Expected-path assumptions.
ROLLUP = {
    "labels": ["SLM", "Embedding", "Vector\n(AI Search)", "Observability\n(Langfuse+Azure)",
               "Compute\n(AKS)", "Eventing\n(Svc Bus)", "Cache\n(Redis)",
               "Platform\n(APIM+)", "Eval+EngAgent"],
    "low":      [300,  50, 245,   80,  300,  15, 130,  205, 150],
    "expected": [2680, 200, 490,  450,  700,  30, 300,  820, 700],
    "high":     [5360, 600, 735, 1100, 1600, 677, 650, 2050, 1900],
}

SOURCES = [
    "azure.microsoft.com/pricing (AI Search, Service Bus, Managed Redis, APIM, Monitor, ACR)",
    "learn.microsoft.com — Azure NC A100 v4 VM sizes & pricing",
    "langfuse.com/pricing (Core $29 / Pro $199; overage tiers)",
    "huggingface.co/pricing (Inference Endpoints / serverless)",
]
