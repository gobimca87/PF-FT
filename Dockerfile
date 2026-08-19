# doc 25 (Infrastructure & Operations) / DEVELOPMENT-GUIDE Phase 19.
# Image name/tag convention per DEVELOPMENT-GUIDE Phase 19: `FA-PFF-ai-runtime:<semver>`,
# built and tagged by CI — never `latest` in a deployed environment. This Dockerfile is
# intentionally tool-agnostic: it doesn't assume Terraform/Bicep or Kustomize/Helm, both
# still open ADR decisions (docs/adr/0003-deferred-decisions-log.md) — it only builds and
# packages the runtime image, which every deployment path needs regardless of how the
# cluster/infra around it ends up provisioned.

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

FROM base AS builder

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir .

FROM base AS runtime

# doc 22 §117 "Container Testing: Non-root execution" — run as an unprivileged user.
RUN groupadd --gid 1000 pfft && \
    useradd --uid 1000 --gid pfft --shell /usr/sbin/nologin --no-create-home pfft

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY config/ config/
COPY prompts/ prompts/
COPY VERSION.yaml ./

USER pfft

EXPOSE 8000

# doc 22 §137 "Smoke Tests": /api/v1/health must respond before traffic is routed —
# this container-level healthcheck is a local safety net, not a substitute for the
# real readiness probe an eventual Kubernetes manifest configures.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/api/v1/health').raise_for_status()"

ENTRYPOINT ["uvicorn", "pf_ft_ai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
