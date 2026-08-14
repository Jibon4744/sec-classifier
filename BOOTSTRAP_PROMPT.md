# BOOTSTRAP PROMPT — paste this into Antigravity / Kilo Code / OpenCode at the
# start of any new project, after copying this skeleton into the project root.
# Fill in the [BRACKETS] before pasting.

---

I'm starting a new project using this skeleton structure:

- AGENTS.md — universal engineering/security/testing/response-style rules are
  already filled in and should stay as-is. The "Project", "Tech stack", and
  "Folder conventions" sections at the top need to be filled in for this project.
- docs/PRD.md, ARCHITECTURE.md, API_SPEC.md, DB_SCHEMA.md, DEPLOYMENT.md — empty,
  need to be filled in for this project.
- .agents/rule-library/ — a reference library of domain rule patterns (backend-api,
  frontend, database, cache-queue, rag-system, ai-agents, devops-deployment).
  These are NOT auto-loaded. Do not copy the whole library.
- .agents/rules/ — currently empty. This is where ACTIVE rules for this project go.
- .agents/skills/ — currently empty.
- .agents/workflows/ — currently empty.

Project description: [describe what you're building, 2-3 sentences]

Known tech stack (or say "decide based on the description"): [e.g. FastAPI +
Postgres + React, or a completely different stack]

Please do the following:
1. Fill in docs/PRD.md, ARCHITECTURE.md, API_SPEC.md (if applicable), DB_SCHEMA.md
   (if applicable), DEPLOYMENT.md based on my project description above.
2. Fill in the "Project", "Tech stack", "Folder conventions" sections of AGENTS.md.
   Do not touch the Engineering principles / Security / Testing / Response style
   sections — those stay as-is across all projects.
3. Look through .agents/rule-library/ and identify which files are actually
   relevant to this project's stack and scope (e.g. skip cache-queue.md if there's
   no caching/queue need, skip rag-system.md and ai-agents.md if this isn't an
   AI/agent project).
4. For each relevant file, copy it into .agents/rules/ and ADAPT it — replace the
   example stack names (FastAPI, Next.js, PostgreSQL, Redis, AWS, etc.) with this
   project's actual technology choices. Do not just copy verbatim if the stack differs.
   IMPORTANT: keep the explicit folder tree (the ```code block``` showing exact
   folder names and what belongs in each) intact and specific — this is a fixed
   contract other AI tools/teammates will follow, not a rough guideline. If you
   change the stack, update the tree to match the new stack's real folder names,
   but keep it just as explicit and complete.
   ALSO IMPORTANT: adapt the SIZE/COMPLEXITY of each tree (frontend, backend,
   database, etc.) to this project's actual scope — a small single-page tool
   doesn't need the same folder depth as a multi-page team SaaS app. Remove
   folders that add no value at this project's size, keep it as simple as the
   project honestly needs. Once you decide the final tree for a given file, write
   it into .agents/rules/ as FINAL — this becomes the fixed contract every future
   session, tool, or teammate on this project follows from then on. Do not
   re-decide or resize it in later sessions; treat it as locked once set.
5. Leave .agents/rule-library/ untouched — it stays as reference material for
   future projects, not something this project's tools will read automatically.
6. Do NOT create .agents/skills/ or .agents/workflows/ content yet — only add
   those once a specific reusable, repeatable procedure emerges during development
   (e.g. a conversion pipeline, a deployment recipe, a data-processing step worth
   packaging for reuse).
7. Summarize what you created/adapted and ask me to review before writing any
   actual application code.

---
