# API Specification

The Sunflower Ensemble Classifier (SEC) API is built using REST conventions on FastAPI. It exposes programmatic endpoints for crop classification under `/api/v1`.

**Confidence semantics**: each `confidence` value is the weighted **geometric-mean**
fusion of the four backbone models' softmax outputs (`ENSEMBLE_FUSION=geometric`
in `app/core/config.py`). The score reflects agreement across the ensemble —
crisp when the models converge, muted when they disagree. Set `ENSEMBLE_FUSION=mean`
to restore a plain weighted average.

---

## 1. Endpoints

### 1.1 Predict Leaf Disease (Mode 1)
Diagnoses leaf diseases from an uploaded leaf image.

*   **HTTP Method**: `POST`
*   **Path**: `/api/v1/predict/disease`
*   **Request Headers**: `Content-Type: multipart/form-data`
*   **Request Payload**:
    *   `file`: Binary file (image format: PNG, JPG, or JPEG)
*   **Image Limits**: Uploads up to `MAX_IMAGE_PIXELS` (default 300 megapixels)
    are accepted and resized to 224×224 before inference. Very high-resolution
    camera photos (e.g. 200 MP) are supported.

#### Response Example (`200 OK`)
```json
{
  "class_name": "Downy Mildew",
  "confidence": 0.9425,
  "info": {
    "cause": "Oomycete pathogen (Plasmopara halstedii), favored by cool wet conditions, often soil-borne or seed-borne",
    "treatment": "Use disease-resistant seed varieties where possible; apply metalaxyl-based seed treatment preventively; improve field drainage; remove infected seedlings early",
    "severity": "high - can cause systemic infection and significant stand loss if it strikes early"
  }
}
```

---

### 1.2 Predict Flower Growth Stage (Mode 2)
Analyzes flower growth stage and estimates harvest timeline from an uploaded flower head image.

*   **HTTP Method**: `POST`
*   **Path**: `/api/v1/predict/growth`
*   **Request Headers**: `Content-Type: multipart/form-data`
*   **Request Payload**:
    *   `file`: Binary file (image format: PNG, JPG, or JPEG)

*   **Image Limits**: Uploads up to `MAX_IMAGE_PIXELS` (default 300 megapixels)
    are accepted and resized to 224×224 before inference. Very high-resolution
    camera photos (e.g. 200 MP) are supported.

#### Response Example (`200 OK`)
```json
{
  "class_name": "Wilted",
  "confidence": 0.8912,
  "info": {
    "description": "Petals have dried and dropped, flower head is drooping and turning brown/yellow - this is the natural late-stage appearance when seeds are approaching maturity",
    "typical_days_to_harvest": "approximately 0-10 days remaining if this stage is due to natural maturity",
    "verify_note": "IMPORTANT: this stage can also be caused prematurely by disease stress rather than true maturity - in the combined mode, cross-check against disease detection before trusting this harvest estimate"
  }
}
```

---

### 1.3 Combined Diagnostic & LLM Analysis (Mode 3)
Performs dual TFLite classification and executes an LLM correlation analysis using both a leaf image and a flower image.

*   **HTTP Method**: `POST`
*   **Path**: `/api/v1/predict/combined`
*   **Request Headers**: `Content-Type: multipart/form-data`
*   **Request Payload**:
    *   `leaf_file`: Binary file (leaf image: PNG, JPG, or JPEG)
    *   `flower_file`: Binary file (flower image: PNG, JPG, or JPEG)

#### Response Example (`200 OK`)
```json
{
  "leaf_result": {
    "class_name": "Downy Mildew",
    "confidence": 0.9425,
    "info": {
      "cause": "Oomycete pathogen (Plasmopara halstedii)...",
      "treatment": "Use disease-resistant seed varieties...",
      "severity": "high - can cause systemic infection..."
    }
  },
  "flower_result": {
    "class_name": "Wilted",
    "confidence": 0.8912,
    "info": {
      "description": "Petals have dried and dropped...",
      "typical_days_to_harvest": "approximately 0-10 days remaining..."
    }
  },
  "combined_analysis": {
    "reliability_rating": "DISTORTED",
    "scientific_rationale": "The flower is classified as 'Wilted', which normally indicates a crop ready for harvest within 0-10 days. However, Downy Mildew is present on the leaves with high confidence (94%). Downy Mildew causes severe systemic chlorosis, stunting, and premature drying of tissues. The drooping and wilting of the head is highly likely a symptom of pathological water stress and vascular disruption caused by the pathogen, rather than natural developmental maturation.",
    "harvest_implications": "Do not trust the 0-10 days harvest estimate. The crop is suffering from a systemic oomycete infection. Early harvest may be necessary to salvage seeds, but quality and yield will be significantly reduced.",
    "actionable_recommendations": "1. Inspect stems and roots for sign of white downy growth. 2. Quarantine the affected zone. 3. Avoid seed-saving from this crop as Downy Mildew is seed-borne. 4. Plan for crop rotation and metalaxyl seed treatments for the next season."
  }
}
```

---

## 2. Error Response Models

For any failures (invalid file types, missing keys, ML model errors, LLM timeouts), the API returns a standard RFC-7807 problem details structure.

### Validation Error (`422 Unprocessable Entity`)
```json
{
  "detail": [
    {
      "loc": ["body", "leaf_file"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Application/LLM Error (`502 Bad Gateway`)
```json
{
  "detail": "Failed to communicate with LLM API. Please check configuration and try again."
}
```
