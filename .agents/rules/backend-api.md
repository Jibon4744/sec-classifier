---
description: Backend API rules for SEC (FastAPI + TFLite Models + OpenAI SDK + JSON Lookups)
globs: app/api/**, app/core/**, app/services/**, app/main.py, app/**.py
activation: glob
---

Backend rules:
- Use clean architecture. Routes/controllers in `app/api` only handle HTTP concerns (parsing input, calling services, returning responses, exception translation).
- Business logic lives in services (`app/services`). There is no database. Data access is represented by local memory loads of static JSON files inside a lookup/data service.
- Local ML inference runs in the `ClassifierService` using TFLite. Models are loaded dynamically from HF Hub. Preprocessing and inference parameters must be isolated.
- The LLM service client (`LLMService`) is isolated and acts as the single gateway for prompt evaluation.
- Validation is done using Pydantic schemas in `app/api/schemas.py`.

API conventions:
- Follow RESTful naming under `/api/v1/predict`.
- Return structured error details (e.g., standard FastAPI HTTPExceptions).
- Do not leak internal python traceback messages to the API client.

Preferred structure — this is a CONTRACT, not a suggestion. Every AI tool working on this repo (any teammate, any model) must place new files according to this exact tree, and must read this tree before creating anything new rather than inventing an alternative layout:

```
app/
├── main.py              # Application entry point: FastAPI app + mounts Gradio app
├── api/
│   ├── routes.py        # HTTP routes layer: POST /disease, /growth, /combined
│   └── schemas.py       # Input/Output validation schemas (Pydantic)
├── core/
│   ├── config.py        # Configuration settings (API keys, ports)
│   └── prompts.py       # Prompt templates for the LLM correlation analysis
└── services/
    ├── classifier.py    # Local TFLite classifier service (downloads and runs inference)
    └── llm_service.py   # LLM orchestration service utilizing the OpenAI client
```

Naming rule:
- Keep filenames descriptive and mapped to their service domain:
  - Route functions and payload configurations inside `app/api/routes.py` and `app/api/schemas.py`.
  - ML execution logic inside `app/services/classifier.py`.
  - LLM client calls inside `app/services/llm_service.py`.

Do not:
- Perform model file loading or TFLite inference inside route functions.
- Embed OpenAI API prompts inside route controllers; keep them in `app/core/prompts.py`.
- Write hardcoded absolute paths inside files; use path functions relative to the app base directory.
