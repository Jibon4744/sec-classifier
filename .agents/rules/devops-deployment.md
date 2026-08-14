---
description: Deployment and DevOps rules for SEC (Docker on Hugging Face Spaces)
globs: Dockerfile, requirements.txt, .dockerignore, README.md, docs/DEPLOYMENT.md
activation: glob
---

Deployment rules:
- Docker configuration must remain explicit, visible, and optimized for Hugging Face Spaces.
- The base image must be lightweight (e.g. `python:3.10-slim`).
- Do not bake credentials or API keys (`OPENAI_API_KEY`) into the image. Fetch them at runtime from the environment.
- Cache Hugging Face Hub models inside a directory that UID `1000` has write permissions to (e.g., `/home/user/.cache`).
- Run a non-root container configuration using user ID `1000` (which is standard for Hugging Face Spaces Docker SDK).
- Bind the web server (uvicorn) to host `0.0.0.0` and port `7860`.

File guidelines:
- **Dockerfile**: Located in the project root. Keeps instructions ordered (system dependencies -> Python package install -> Source code copy) to optimize Docker layer caching.
- **requirements.txt**: Lists explicit pinned versions where necessary to avoid build breakages (e.g. `fastapi`, `uvicorn`, `gradio`, `openai`, `tflite-runtime` or `tensorflow-cpu`).
- **.dockerignore**: Excludes large or sensitive directories:
  ```
  .git/
  .agents/
  .github/
  tests/
  venv/
  *.pyc
  __pycache__/
  ```

Do not:
- Hardcode the API port; always use port `7860` as required by Spaces.
- Run the container as root; this will cause execution failures on Hugging Face Spaces.
- Include unit/integration test dependencies in production builds if they significantly balloon the image size.
