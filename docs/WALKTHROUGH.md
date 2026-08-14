# Final Walkthrough & Verification

This document captures the end-to-end verification of the Sunflower Ensemble
Classifier (SEC) after the build completed. It covers the test suite and a live
server walkthrough of all three modes.

---

## 1. Test Suite

The suite lives in `tests/` and mirrors the application layers. It does not
touch the network or the LLM API — external dependencies are mocked.

| File | Coverage |
| --- | --- |
| `tests/test_classifier.py` | TFLite `ClassifierService`: lookup-table loading, image preprocessing, softmax, and subset prediction for disease and growth-stage modes |
| `tests/test_llm.py` | `LLMService`: JSON parsing/cleanup, API-key validation, prompt interpolation, missing-key defaults, and error translation (ValueError/RuntimeError) |
| `tests/test_api.py` | FastAPI routes: success responses, invalid-file (400), missing-file (422), classifier failure (500), LLM validation error (400), and LLM transport error (502) for all three endpoints |

### Run

```powershell
python -m pytest tests -v
```

### Result (verified)

```
26 passed, 1 warning
```

The only warning is a Pydantic V2 deprecation notice for the class-based
`Settings.Config` in `app/core/config.py` — non-fatal, upgrade to `ConfigDict`
when convenient.

---

## 2. Starting the Server

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 7860
```

On startup the FastAPI lifespan hook downloads and allocates the four TFLite
ensemble models from the Hugging Face Hub (`Jibon4744/SEC-sunflower-classifier`)
into the local cache. If the download fails the server still boots (failure is
logged, not fatal) and models are retried on first inference.

---

## 3. Live Verification (performed against a running server)

| Request | Expected | Observed |
| --- | --- | --- |
| `GET /` | 200 (Gradio UI) | 200 |
| `POST /api/v1/predict/disease` + valid image | 200 | 200 |
| `POST /api/v1/predict/disease` + non-image | 400 | 400 |
| `POST /api/v1/predict/disease` + no file | 422 | 422 |
| `POST /api/v1/predict/growth` + valid image | 200 | 200 |
| `POST /api/v1/predict/combined` + one file only | 422 | 422 |

### Sample real prediction (Mode 1)

```json
POST /api/v1/predict/disease  file=leaf.png
{
  "class_name": "Healthy",
  "confidence": 0.2603801466061441,
  "info": {
    "cause": "No disease detected",
    "treatment": "No action needed - continue standard monitoring and care",
    "severity": "none"
  }
}
```

The combined endpoint (Mode 3) runs both classifiers and then calls the LLM. It
returns `400` when the LLM API key is missing (clear `ValueError`), which is the
expected behavior before `OPENAI_API_KEY` is configured.

---

## 4. Configuration Notes

- `OPENAI_API_KEY` — required for Mode 3 (Combined Report). Supply as an env var
  or in a `.env` file.
- `OPENAI_BASE_URL` — optional, redirects LLM calls to compatible gateways.
- `OPENAI_MODEL_NAME` — optional, default `gpt-4o-mini`.

No secrets are hardcoded; the Docker image reads them from the runtime
environment (Hugging Face Spaces Secrets).
