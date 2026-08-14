---
description: Backend API rules (adapt stack names to the actual project)
globs: backend/**, api/**, server/**, app/**.py
activation: glob
---
<!-- Example stack shown: FastAPI + Pydantic + SQLAlchemy + PostgreSQL + Redis.
     Swap for the project's actual backend stack before copying into .agents/rules/. -->

Backend rules:
- Use clean architecture. Routes/controllers only handle HTTP concerns.
- Business logic lives in services. Database access lives in repositories.
- Validation done using schemas/models. Use dependency injection where appropriate.
- Use async I/O where supported and beneficial. Paginate list endpoints.
- Use consistent response models and centralized exception handling.

API conventions:
- Follow RESTful naming. Version APIs when needed (e.g. /api/v1/).
- Use proper status codes. Return predictable response structure.
- Do not leak internal stack traces or raw database errors.

Preferred structure — this is a CONTRACT, not a suggestion. Every AI tool working
on this repo (any teammate, any model) must place new files according to this
exact tree, and must read this tree before creating anything new rather than
inventing an alternative layout:

```
backend/
├── api/
│   ├── routes/            # HTTP layer ONLY: parse request, call a service,
│   │                       # return response. No business logic, no DB queries,
│   │                       # no raw SQL/ORM code here.
│   └── dependencies/       # FastAPI-style dependency injection providers
│                            # (auth checks, DB session providers, etc.)
├── services/                # Business logic lives HERE. Services call
│   │                          # repositories, never the DB directly. Each
│   │                          # service file = one domain (e.g. user_service.py,
│   │                          # not a catch-all "logic.py").
├── repositories/             # ALL database access lives HERE, nowhere else.
│                              # One repository file per entity/table.
├── models/                    # ORM/DB models (e.g. SQLAlchemy models)
├── schemas/                    # Request/response validation models (Pydantic).
│                                 # No business logic inside schema files.
├── core/                        # App config, startup/lifespan, shared settings,
│                                 # centralized env var loading.
├── utils/                        # Small stateless helper functions only.
│                                  # Not a dumping ground — if it's domain logic,
│                                  # it belongs in services/, not here.
└── tests/                          # Mirrors the structure above:
    ├── test_services/
    └── test_repositories/
```

Naming rule: a route file, service file, and repository file for the same domain
share a base name (users.py in routes/, user_service.py in services/,
user_repository.py in repositories/) — this makes it obvious across tools/people
where the matching piece lives.

Do not:
- Put SQL/ORM-heavy logic inside route files.
- Put business logic inside request/response schemas.
- Scatter environment variables across many files; centralize config.
- Mix unrelated domains in the same service file.
