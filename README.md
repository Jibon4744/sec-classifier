---
title: Sunflower Ensemble Classifier (SEC)
emoji: 🌻
colorFrom: yellow
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Reusable project skeleton — how this works

This is a generic, tool-portable starter structure, distilled from a Cursor rule
template (11 .mdc files covering an AI SaaS stack) and reorganized to:
1. Work across Antigravity, Kilo Code, and OpenCode without duplication.
2. Avoid loading irrelevant rules into every project.
3. Match the actual Rules vs Skills vs Workflows distinction these tools use.

## What changed from the original Cursor template, and why

The original had 11 rule files, all treated the same way. Reading them closely,
they split into two very different kinds of content:

**Universal, stack-agnostic principles** (used to be 4 separate always-on files:
global architect persona, security, testing, response style) — these don't
depend on file type or project stack at all. They're now merged into AGENTS.md
directly, since that's the one file every tool reads automatically, and there's
no reason to keep re-deciding whether to include them — they always apply.

**Stack-specific domain modules** (backend, frontend, database, cache, RAG,
agents, devops — used to be 7 separate files) — these only matter if a given
project actually has that concern. A CRUD app doesn't need RAG rules; a data
science script doesn't need frontend rules. These now live in
.agents/rule-library/ as reference material, NOT auto-loaded. At the start of
each new project, the agent (via BOOTSTRAP_PROMPT.md) picks only the relevant
ones, adapts the example stack names to the real stack, and copies them into
.agents/rules/ — which IS auto-loaded.

## Folder structure
```
AGENTS.md                  <- portable core (universal rules + per-project fill-in)
docs/                       <- PRD, architecture, API spec, DB schema, deployment
.agents/
  rules/                    <- ACTIVE rules for the current project (starts empty)
  rule-library/             <- REFERENCE only, not auto-loaded, pick from this per project
  skills/                   <- reusable multi-step procedures, added as they emerge
  workflows/                <- manual slash-command recipes, added as needed
BOOTSTRAP_PROMPT.md          <- paste into the agentic IDE at the start of a new project
```

## Your workflow for every new project
1. Copy this whole skeleton into the new project's root.
2. Fill in the [BRACKETS] in BOOTSTRAP_PROMPT.md with a short project description.
3. Paste BOOTSTRAP_PROMPT.md's content into Antigravity (or Kilo Code / OpenCode).
4. Let the agent fill in docs/, AGENTS.md's project section, and pull the
   relevant files from rule-library/ into rules/.
5. Review what it generated before writing actual application code.
6. As real reusable procedures emerge during development (a conversion script,
   a deployment recipe, a testing pattern you'll reuse), ask the agent to
   package them as a Skill in .agents/skills/ — don't pre-build these, let them
   emerge from actual repeated work.

## Why this survives switching tools or running out of quota
AGENTS.md and the .agents/ directory convention are read by Antigravity, Kilo
Code, and OpenCode without any reformatting needed. If a future tool only reads
its own proprietary format, the content here is already organized cleanly
enough to convert quickly — nothing here is locked to one platform's syntax.
