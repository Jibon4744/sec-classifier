# Deployment Specification

The Sunflower Ensemble Classifier (SEC) is built to be run inside a single Docker container. It is designed to be deployed to **Hugging Face Spaces** using the **Docker SDK**.

---

## 1. Hugging Face Spaces Configuration

Spaces requires metadata defined in the repository's main `README.md` at the root, using a YAML frontmatter block. The spaces environment will read this and compile the Dockerfile automatically.

> **Note (2026):** Hugging Face now only allows hosting Docker/Gradio Spaces on
> compute (including the free CPU Basic tier) with a paid **PRO** subscription.
> Static Spaces remain free. If PRO is not available, deploy the same image to
> any Docker-capable host (e.g. Render, Railway) instead — see §5.

### Root `README.md` Frontmatter
```yaml
---
title: Sunflower Ensemble Classifier (SEC)
emoji: 🌻
colorFrom: yellow
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---
```

---

## 2. Dockerfile Design

Hugging Face Spaces runs Docker containers under strict guidelines:
1.  **Port**: The container must listen on port `7860`.
2.  **Permissions**: The container runs under user ID `1000` (non-root). Any folders that require write permissions (like Hugging Face cache folders) must be owned/writable by user ID `1000`.

### Proposed `Dockerfile`
```dockerfile
# Use an official, lightweight Python image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user with UID 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user/app \
    HF_HOME=/home/user/.cache/huggingface

# Set the working directory
WORKDIR $HOME/app

# Copy dependency specifications and install them
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application files
COPY --chown=user:user . .

# Expose the default Gradio / Spaces port
EXPOSE 7860

# Run uvicorn server, binding to all interfaces on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## 3. Environment Variables

To run the application, the following environment variable must be set in the Hugging Face Spaces Settings interface as a **Secret**:
*   `OPENAI_API_KEY`: API key used to authenticate with the LLM API.

The following environment variables can be set as **Variables** to customize target models:
*   `OPENAI_BASE_URL`: (Optional) Redirects LLM API calls to alternative gateways.
*   `OPENAI_MODEL_NAME`: (Optional) Swaps the model used (default: `gpt-4o-mini`).

---

## 4. Model Pre-caching (Optimization)

To prevent slow response times on the first request, the TFLite models should be downloaded from the HF Hub during container startup.
This is accomplished by adding a python script run during build-time (or in a lifespan startup hook in FastAPI) that triggers:
```python
from huggingface_hub import hf_hub_download
# Pre-download models on startup
hf_hub_download(repo_id="Jibon4744/SEC-sunflower-classifier", filename="leaf_classifier.tflite")
hf_hub_download(repo_id="Jibon4744/SEC-sunflower-classifier", filename="growth_classifier.tflite")
```
This ensures they are cached inside the container image or downloaded before the server begins serving traffic.

---

## 5. Alternative host: Render (Docker)

Hugging Face Spaces Docker hosting now requires PRO (see §1). A free fallback is
Render's Web Service with the same Dockerfile:

1. Push this repo to GitHub/GitLab.
2. Render → **New → Web Service** → connect the repo → **Environment: Docker**.
   Render auto-detects the `Dockerfile` and runs `uvicorn app.main:app --host 0.0.0.0 --port 7860`.
3. Set the env vars in the Render dashboard (same as HF): `OPENAI_API_KEY`
   (secret), optional `OPENAI_BASE_URL` / `OPENAI_MODEL_NAME`. The `.env` file is
   git-ignored and NOT uploaded, so secrets must be set in the dashboard.
4. Health check: `GET /` (path `/`).
5. Public URL is HTTPS by default, so the mobile camera works out of the box.

**Resource sizing**: the image includes TensorFlow (~2.5 GB) and decodes
high-resolution photos (up to `MAX_IMAGE_PIXELS`). Use **at least 2 GB RAM**:
the inference server holds ~1 GB committed, and decoding a 200 MP photo spikes
~600 MB on top. On hosts with too little RAM the OS pages the process out and
response times balloon to minutes (seen locally on a 7.7 GB machine with ~0.4 GB
free). Cold start preloads the 4 TFLite models from the HF Hub (several minutes);
model files are cached under `HF_HOME` (`/home/user/.cache/huggingface`).
Prefer normal-resolution (≤50 MP) photos on constrained instances.
