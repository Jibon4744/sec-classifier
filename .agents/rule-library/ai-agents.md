---
description: AI agent/tool orchestration rules — only relevant if the project builds autonomous agents
globs: ai/**, agents/**, tools/**, workflows/**, orchestration/**
activation: glob
---

Agent system architecture:
- Separate planner, executor, tools, memory, state, and evaluation logic.
- Agents must be modular and role-specific where possible.
- Tool calls must be explicit, validated, and logged.

Rules:
- Agents must not directly access databases or external APIs unless explicitly
  designed through a tool layer.
- Prompts must be templated and stored separately from orchestration logic.
- Keep critical business workflows deterministic where possible.
- Add output validation and fallback behavior; use structured schemas for
  agent outputs in production paths.
- Every tool needs: a clear purpose, input schema, output schema, failure behavior.
- Sensitive tools must enforce auth and authorization checks.
- Separate short-term conversational state from long-term memory.

Do not:
- Let agents perform unrestricted actions.
- Hide tool errors.
- Mix prompt text deeply into service/business code.
