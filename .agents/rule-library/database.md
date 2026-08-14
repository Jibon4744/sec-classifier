---
description: Database and persistence rules (adapt DB engine to the actual project)
globs: models/**, repositories/**, migrations/**, db/**, prisma/**, sql/**
activation: glob
---
<!-- Example stack shown: PostgreSQL. Swap for the project's actual database
     before copying into .agents/rules/. -->

Database rules:
- Use migrations for all schema changes.
- Design tables with clear ownership, timestamps, and constraints.
- Add indexes for common filters and joins. Use foreign keys where appropriate.
- Every core entity should have: id, created_at, updated_at.
- For multi-tenant systems, include tenant/organization isolation where relevant.
- Keep schemas normalized unless denormalization is justified by performance needs.

Preferred structure — this is a CONTRACT, not a suggestion:

```
backend/
├── models/                  # ORM model definitions — one file per entity
│                              # (user.py, organization.py), matching table names.
├── repositories/              # Query logic — one file per entity, matching
│                                # models/ 1:1 (user.py here maps to user.py there).
└── migrations/                  # Auto-generated migration files (e.g. Alembic).
                                   # Never hand-edit an already-applied migration.
```

Repository rules:
- All DB access must go through repositories/data access layer.
- Parameterize queries. Avoid N+1 query patterns.
- Use transactions when multiple writes must succeed together.

Do not:
- Write raw SQL inside controllers/routes.
- Make schema changes without migration files.
- Assume single-tenant if the product is multi-tenant.
