---
description: Caching and background job/queue rules — only relevant if the project uses them
globs: backend/**, workers/**, jobs/**, queue/**, cache/**
activation: glob
---
<!-- Only copy this into .agents/rules/ if the project actually needs caching
     or background jobs. Example shown: Redis. -->

Rules:
- Use caching/queues for expensive reads, rate limiting, ephemeral state,
  and short-lived coordination — not as the only source of truth for critical
  persistent state.
- Choose TTLs intentionally. Make cache invalidation explicit.
- Wrap cache/queue access in dedicated utilities/services, not scattered raw calls.
- Use stable key naming conventions. Prefer idempotent worker/job behavior.
- Use retries carefully and avoid infinite retry loops.

Do not:
- Cache highly sensitive data unless encrypted and justified.
- Store large unbounded payloads without TTL or cleanup strategy.
- Mix queue semantics and cache semantics without clarity.
