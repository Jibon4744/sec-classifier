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
| `tests/test_config.py` | `config.py`: PIL decompression-bomb guard raised above its default |

### Run

```powershell
python -m pytest tests -v
```

### Result (verified)

```
27 passed, 1 warning
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
POST /api/v1/predict/disease  file=leaf.png  (100×100 solid-color test image)
{
  "class_name": "Healthy",
  "confidence": 0.248,
  "info": {
    "cause": "No disease detected",
    "treatment": "No action needed - continue standard monitoring and care",
    "severity": "none"
  }
}
```

The confidence here is low because the sample input is a tiny solid-colour
square (no meaningful content). On realistic high-resolution photos the
geometric-mean fusion reports crisp values — measured **0.50 → 0.81** on the
same prediction (see §6).

The combined endpoint (Mode 3) runs both classifiers and then calls the LLM. It
returns `400` when the LLM API key is missing (clear `ValueError`), which is the
expected behavior before `OPENAI_API_KEY` is configured.

---

## 4. Configuration Notes

- `OPENAI_API_KEY` — required for Mode 3 (Combined Report). Supply as an env var
  or in a `.env` file.
- `OPENAI_BASE_URL` — optional, redirects LLM calls to compatible gateways
  (e.g. `https://api.euron.one/api/v1/euri` for the Euron provider used in this
  deployment).
- `OPENAI_MODEL_NAME` — optional, default `gpt-4o-mini`.
- `MAX_IMAGE_PIXELS` — optional, default 300,000,000. Raised from PIL's default
  (178,956,970) so high-resolution mobile photos decode without
  `DecompressionBombError`.
- `ENSEMBLE_FUSION` — optional, default `geometric`. Weighted geometric-mean
  fusion of the four models (alternative: `mean`). See §6.

## 5. Troubleshooting

- **`DecompressionBombError: Image size (N pixels) exceeds limit`** — the upload
  exceeded PIL's pixel guard. Bump `MAX_IMAGE_PIXELS` in `app/core/config.py`
  (or `.env`) above the photo's resolution, then restart the server.
- Notice how the reader must keep this in sync with any failure logged as
  *"Could not preprocess input component ... (a `Image` component)"* — that
  Gradio wrapper error is always caused by the underlying PIL decode failure
  above.
- **Slow prediction (1–2 min)** — inference is actually ≈1 s per image
  (measured: ensemble 1.2 s, full disease prediction 0.8 s). Two real causes were
  found and fixed:
  1. The O(input-pixels) cost of resizing ~200 MP photos → fixed with
     `reducing_gap=3.0` in `ClassifierService._preprocess_image` (~7× faster).
  2. **The machine was memory-starved** (7.7 GB total, ~0.4 GB free): the
     ~1 GB TensorFlow server process had been paged out to disk (working set
     dropped to 14 MB), so every request forced a huge swap-in. Restarting the
     server on a machine with free RAM restored ~1 s responses. On low-RAM hosts,
     close heavy apps while testing and prefer normal-resolution photos.
- **`Failed to communicate with LLM API: Error code: 401 ... invalid_api_key`**
  (Mode 3) — `OPENAI_API_KEY` in `.env` is wrong or belongs to another provider.
  OpenAI keys start with `sk-`/`sk-proj-`. If you use a different provider, set
  `OPENAI_BASE_URL` to that provider's OpenAI-compatible endpoint too.

---

## 6. Performance & Confidence (measured)

| Metric | Before | After |
| --- | --- | --- |
| Ensemble inference (4 models, CPU) | 1.2 s | 1.2 s |
| Full disease prediction (12 MP) | 0.8 s | 0.8 s |
| Resize of ~200 MP photo | 2.67 s | 0.37 s |
| Confidence (geometric fusion, same class) | 0.50 | 0.81 |
| Cold start (models cached) | ~20 s | ~20 s |
| Cold start (first-ever download, ~600 MB) | several minutes | several minutes |

Changes that produced these numbers are recorded in `opencode_complete.md` and
in `app/core/config.py` (`ENSEMBLE_FUSION`, `MAX_IMAGE_PIXELS`) plus
`app/services/classifier.py` (`_preprocess_image` with `reducing_gap`, and
geometric-mean fusion in `_run_ensemble_inference`).

No secrets are hardcoded; the Docker image reads them from the runtime
environment.
