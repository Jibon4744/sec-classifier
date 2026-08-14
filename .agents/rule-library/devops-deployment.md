---
description: Deployment and infrastructure rules (adapt cloud/hosting target to the actual project)
globs: infra/**, docker/**, .github/**, deployment/**, terraform/**
activation: glob
---
<!-- Example shown assumes Docker + a cloud provider + CI/CD. Adapt the hosting
     target (AWS, Hugging Face Spaces, Render, etc.) before copying into
     .agents/rules/. -->

Rules:
- Applications must be container-friendly with reproducible builds.
- Use environment-driven configuration; separate build-time from runtime config.
- Add health checks. Keep services stateless unless intentional and documented.
- Ensure logs are structured and production-usable.
- Keep Dockerfiles clean and optimized; prefer multi-stage builds; avoid
  baking secrets into images; minimize image size.
- Run lint, tests, and build validation before merge/deploy.
- Use separate environments where needed (dev/staging/prod).
- Design for rollback-safe deployments.

Do not:
- Hardcode cloud-specific IDs or secrets in code.
- Mix deployment-only hacks into application logic.
- Assume local-only paths/config in production code.
