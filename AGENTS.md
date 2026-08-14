# AGENTS.md

<!-- Read automatically by Antigravity, Kilo Code, and OpenCode.
     The sections below marked [FILL PER PROJECT] should be rewritten using
     BOOTSTRAP_PROMPT.md at the start of a new project.
     Everything else (Engineering principles, Security, Testing, Response style)
     is universal and stack-agnostic — keep it as-is across projects unless you
     deliberately want to change your own standards. -->

## Project
**SEC (Sunflower Ensemble Classifier)** is a web application designed to diagnose sunflower leaf diseases and identify flower growth stages. The application operates in three modes: (1) Leaf Disease classification and static agronomic lookup; (2) Flower Growth Stage classification and static harvest estimate lookup; and (3) A Combined mode that runs both classifications and uses an LLM to evaluate if the growth stage characteristics are natural or pathologically distorted by the detected disease, generating an expert recommendations report.

## Tech stack
- **Backend Framework**: FastAPI (exposed REST endpoints, lifespan management)
- **Frontend UI**: Gradio (3 tabs for the 3 modes) mounted directly onto FastAPI via `gr.mount_gradio_app`
- **Machine Learning**: Local CPU inference via TFLite (models loaded from Hugging Face Hub: `Jibon4744/SEC-sunflower-classifier`)
- **Metadata Storage**: Static JSON files (`app/data/diseases.json`, `app/data/stages.json`)
- **LLM Integration**: OpenAI Python SDK client with configurable environment overrides (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL_NAME`)
- **Container/Hosting**: Docker container running on Hugging Face Spaces (Docker SDK)

## Folder conventions
Every AI tool or human contributor must adhere strictly to this folder structure:
- `app/` - Primary application container
  - `app/main.py` - Application bootstrap and Gradio UI mount point
  - `app/api/` - FastAPI endpoints, routing, and schema validation
  - `app/core/` - Application configurations, prompts, and global settings
  - `app/services/` - Business logic: TFLite classification and LLM client orchestration
  - `app/frontend/` - Gradio UI layouts, templates, and theme settings
  - `app/data/` - Lookup tables (`diseases.json`, `stages.json`)
- `tests/` - System testing suite mirroring `app/` logic
- `Dockerfile` - Multi-stage deployment instructions


---

## Engineering principles (universal — apply to every project)
- Think like an architect first, then implement like a senior engineer.
- Preserve architecture consistency across the repository.
- Prefer scalable, modular, production-ready code over shortcuts.
- Infer the correct layer for each change before writing code.
- Extend existing patterns before introducing new ones.
- **Before creating any new file, check .agents/rules/ for an explicit folder
  structure covering that part of the codebase (backend, frontend, database,
  etc.) and place the file exactly where that structure specifies.** This repo
  may be worked on by multiple people using different AI tools — the folder
  structure is a fixed contract, not a suggestion, so that any AI/teammate
  converges on the same layout rather than inventing a competing one.
- Follow clean architecture and separation of concerns: thin routes/controllers,
  business logic in services, persistence logic in repositories/data-access layer.
- Prefer small composable modules over large files.
- Avoid duplication; create reusable abstractions only when justified.
- Do not rewrite unrelated files or silently change architecture.
- Use clear naming and type hints/types wherever the stack supports them.
- Add structured logging on critical paths and robust error handling for
  production flows.
- Respect environment-based configuration. Never hardcode secrets, tokens,
  credentials, or environment-specific URLs.
- Before implementing, align with docs/PRD.md, docs/ARCHITECTURE.md,
  docs/API_SPEC.md, docs/DB_SCHEMA.md, docs/DEPLOYMENT.md if present. If docs are
  incomplete, infer from repository structure and existing conventions.

## Security (universal — apply to every project)
- Never hardcode secrets, API keys, tokens, credentials, or private URLs.
- Never log passwords, tokens, raw secrets, or sensitive user content.
- Validate and sanitize all user inputs. Treat uploads, URLs, prompts, and
  external content as untrusted.
- Enforce authentication and authorization checks on protected resources.
- Use least-privilege access patterns. Add rate limiting to sensitive or
  expensive endpoints.
- If the project involves LLM/agent components: add prompt injection
  resistance, validate tool inputs/outputs, restrict tool access by policy,
  and never trust LLM output without validation in critical paths.
- Do not assume client-side validation is enough.
- Do not return internal exception details to users.

## Testing and code quality (universal — apply to every project)
- Write production-quality code with tests for critical behavior.
- Prefer deterministic unit tests for business logic; add integration tests for
  APIs, repositories, pipelines, and workflows crossing boundaries.
- Mock external services, cloud dependencies, and model providers where appropriate.
- Cover validation, failure, and edge cases. Keep tests readable and isolated.
- Use linting and formatting; use types wherever the stack supports them.
- Do not add major logic without at least basic tests.
- Do not create brittle tests tied to unstable implementation details.
- Do not depend on live external APIs in normal test flows.

## Response style (universal — how the agent should work)
- Prefer precise, minimal, production-ready changes.
- Explain architecture briefly when it matters; generate only the necessary
  files and edits; respect existing repository conventions.
- If a task is large, break it into clean phases but still produce usable code.
- When adding a new module, place it in the correct layer and name it clearly.
- Mention follow-up files that should also be updated (env examples,
  migrations, tests, docs).
- Do not produce toy code when production code is requested.
- Do not invent random abstractions without need, or change unrelated code paths.

## Reference docs
See docs/PRD.md, docs/ARCHITECTURE.md, docs/API_SPEC.md, docs/DB_SCHEMA.md,
docs/DEPLOYMENT.md for full detail before making structural changes.
