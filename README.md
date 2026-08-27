# SEC — Sunflower Ensemble Classifier

A deep learning system that classifies sunflower leaf disease and growth stage
from images, combining a 4-model weighted CNN ensemble with an LLM reasoning
layer — deployed as a full-stack, containerized web application.

Originally developed as a B.Sc. thesis at Daffodil International University,
then rebuilt end-to-end as a production-style application: model optimization,
REST API, containerized deployment, and automated testing.

---

## What it does

Three modes, one app:

| Mode | Input | Output |
|---|---|---|
| **Disease detection** | Leaf image | Disease class, confidence, cause & treatment (static reference data, no LLM) |
| **Growth stage detection** | Flower/plant image | Growth stage, confidence, harvest-time estimate (static reference data, no LLM) |
| **Combined analysis** | Leaf + flower image | Both classifications, plus an LLM-generated analysis of whether the growth-stage appearance is a reliable maturity signal or possibly distorted by the detected disease |

The combined mode addresses a real observation from the underlying research:
a plant can visually appear "aged" either because it's genuinely near
harvest, or because disease has impaired photosynthesis and caused premature
wilting — these look similar but mean very different things for a farmer
deciding when to harvest.

---

## Model performance

| Model | Test accuracy |
|---|---|
| MobileNet | 83.02% |
| ResNet50 | 83.77% |
| EfficientNetV2S | 81.51% |
| VGG16 | 79.62% |
| **Weighted ensemble (SEC)** | **88.68%** (F1: 88.69%) |

The ensemble outperforms every individual base model. Weights are
accuracy-proportional (`weight_i = accuracy_i / sum(accuracies)`), and the 4
base models were selected for complementary per-class strengths, not just raw
accuracy alone.

---

## Engineering highlights

**Model optimization — verified, not assumed.** The 4 base models totaled
~743MB in their original `.h5` format, too large for free-tier hosting. Each
was converted to TFLite with float16 quantization and independently verified
against its original before being trusted:

| | Before | After | Reduction |
|---|---|---|---|
| MobileNet | 38.97 MB | 6.46 MB | 83% |
| VGG16 | 176.7 MB | 29.5 MB | 83% |
| EfficientNetV2S | 244.3 MB | 40.4 MB | 83% |
| ResNet50 | 283.5 MB | 47.1 MB | 83% |
| **Total** | **~743 MB** | **~123 MB** | **83%** |

Each converted model was tested against its original `.h5` version on real
sample images before adoption — 100% prediction agreement, maximum probability
shift under 2%. Nothing was assumed to work; every optimization was measured.

**Grounded LLM design.** The LLM layer (used only in combined mode) receives
structured classification results, not raw images, and is explicitly
instructed not to invent numeric estimates from its own memory — factual data
(disease treatments, harvest-time ranges) comes from a static, human-curated
reference table, not model generation. The LLM's role is narrowly scoped to
reasoning and explanation over already-computed facts.

**Automated testing.** 26 passing tests covering the API layer, the ensemble
classifier service, and the LLM service (including error handling, malformed
responses, and edge cases).

**Containerized deployment.** FastAPI backend with a Gradio UI mounted
directly onto the same app (single process, single container) — packaged with
a hand-written `Dockerfile` and deployed via Hugging Face Spaces' Docker SDK
for full control and portability, rather than relying on an opaque
auto-generated container.

---

## Architecture

```
Gradio UI (mounted on FastAPI)
        |
        v
FastAPI backend  --->  Ensemble inference (4 TFLite models, weighted combine)
        |                       |
        |                       v
        |               Hugging Face Hub (model storage)
        v
Static JSON lookup (modes 1 & 2)   OR   LLM reasoning layer (mode 3 only)
        |
        v
   JSON response
```

## Tech stack

- **Backend:** FastAPI, Pydantic
- **Models:** TensorFlow Lite (float16), served from Hugging Face Hub
- **Frontend:** Gradio, mounted on the FastAPI app
- **LLM layer:** structured prompt over classification outputs (combined mode only)
- **Testing:** pytest (26 tests)
- **Deployment:** Docker, Hugging Face Spaces (Docker SDK)

## API

| Endpoint | Purpose |
|---|---|
| `POST /predict/disease` | Leaf image → disease classification |
| `POST /predict/growth-stage` | Flower image → growth-stage classification |
| `POST /predict/combined` | Both images → both classifications + LLM analysis |
| `GET /health` | Health check |

Full request/response contracts in [`docs/API_SPEC.md`](docs/API_SPEC.md).

## Project structure

```
app/
├── api/            # FastAPI routes and schemas
├── core/           # config, prompts
├── data/           # disease_info.json, growth_stage_info.json
├── services/       # classifier (ensemble), LLM service
├── frontend/        # Gradio UI
└── main.py
tests/               # 26 tests across API, classifier, LLM service
docs/                 # PRD, architecture, API spec, deployment notes
Dockerfile
```

## Running locally

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 7860
```
Visit `http://127.0.0.1:7860`. Disease and growth-stage modes work
immediately; combined mode requires an LLM API key set in `.env` (see
`docs/DEPLOYMENT.md`).

## Origin

Built on top of a B.Sc. thesis: *"Deep Learning-Based Analysis & Classification
of Sunflower Leaf Disease & Tracking Growth Stage Using CNN"* — Daffodil
International University. Dataset (808 real field images collected in
Bangladesh) available on Mendeley Data.

## License
[Add your chosen license]
