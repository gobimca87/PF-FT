# Enterprise API Runbook

**Owner:** Enterprise Integration Team (doc 28 §4) · **Severity:** P1 if a critical
integration is down platform-wide, otherwise P2/P3 (doc 28 §9-11).

## Symptoms (doc 28 §52-55)

4xx, 5xx, 429, timeout, connection failure, schema mismatch.

## Diagnostic steps

1. Identify the failing `api_id` from `src/pf_ft_ai/integration/api/catalog.py`'s
   `ApiCatalog` and the calling tool from `integration/tools/registry.py`.
2. Check the classification: `classify_http_status()` /
   `IntegrationErrorCode` (`integration/errors/codes.py`) — this is what
   `ToolExecutor` (`integration/tools/executor.py`) uses to decide retry eligibility
   (`is_retryable()`).
3. Check the per-`api_id` circuit breaker inside `ToolExecutor._circuit_breakers` —
   if `CircuitBreaker.allow_request()` is `False`, calls are being rejected before
   ever reaching the network (`ToolResult.error.message` contains `"Circuit open"`).
4. For 429: confirm `ConcurrencyLimiter` (`integration/execution/concurrency.py`)
   pool settings aren't themselves causing excess concurrent calls
   (`config/base/*.yaml` `concurrency.enterprise.max_parallel`).
5. For schema mismatch (`API Contract Failure`, doc 28 §56): capture the actual
   response body — `HttpxEnterpriseHttpClient` (`integration/api/client.py`) forwards
   it unchanged (never invents missing fields, see `tests/contract/`), so what you see
   in the trace is exactly what the enterprise API returned.

## Recovery

- Transient (429/5xx/timeout): let `execute_with_retry` (`integration/execution/retry.py`)
  handle it within its configured backoff; do not manually hammer retries.
- Non-retryable (4xx other than 429): this is a request-shape or authorization problem,
  not a dependency outage — check the propagated `Authorization` header
  (`ToolExecutor.execute()`'s `propagated_headers`, doc 10 §72-74) before assuming the
  enterprise API is broken.
- Never bypass the enterprise API's rate limits or authorization to "unblock" a workflow
  (doc 28 §53, §89).

## Escalation

Enterprise Integration Team, with the `api_id`, correlation ID, status code, and
whether the circuit is open.
