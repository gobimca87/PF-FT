# 4. Memory / session / cache store: Azure Managed Redis

Date: 2026-08-16

## Status

Accepted

## Context

`DEVELOPMENT-GUIDE.md` §2 and doc 9 (`MD files/3 Context & Integration/9 PF-FT-AI-MEMORY-CACHE.md`
§21, §137-139) deliberately left the memory/session/cache backing store open, to be
resolved via ADR rather than guessed. Doc 9 explicitly requires the choice stay behind
`MemoryStore`/`CacheStore` interfaces regardless of which technology is picked (§137-138,
"Provider Independence").

## Decision

Use **Azure Managed Redis** as the backing store for both the memory subsystem
(`src/pf_ft_ai/memory/`) and the cache subsystem (`src/pf_ft_ai/cache/`), built in
Phase 7. Azure Managed Redis speaks the standard Redis (RESP) protocol, so `redis-py`'s
`redis.asyncio.Redis` client is used unmodified — no Azure-specific SDK is needed at the
application layer.

Memory and cache share one Redis instance but are logically separated by key namespace
(`pf-ft:<environment>:memory:...` / `pf-ft:<environment>:cache:...`), per doc 9 §99-100,
§140 ("logically separated by namespace... even if the same physical technology is used").

Connection configuration (`config/base/redis.yaml`) follows the project's established
`*_secret_ref` pattern (`CLAUDE.md` Secrets, doc 17 §7): host/port/ssl/db are plain
config; the access key is referenced as `password_secret_ref`, resolved at runtime by the
existing `SecretResolver` (env var locally; Azure Key Vault in deployed environments,
populated by the user's own Key Vault + AKS wiring — no code change required to switch
resolvers, per the interface already built in Phase 1).

## Consequences

- `src/pf_ft_ai/memory/` and `src/pf_ft_ai/cache/` get concrete `RedisMemoryStore` /
  `RedisCacheStore` implementations in Phase 7, not another in-memory placeholder — this
  decision is resolved, unlike the still-open items in
  [`0003-deferred-decisions-log.md`](0003-deferred-decisions-log.md).
- Tests use `fakeredis`'s async client (`fakeredis.FakeAsyncRedis`), which speaks the same
  RESP protocol, so the store implementations are tested against real Redis semantics
  (TTL, key expiry, deletion) without requiring a live Redis server in CI or local dev.
- `docs/adr/0003-deferred-decisions-log.md`'s "Memory / session / cache store" row is
  updated to point here.
