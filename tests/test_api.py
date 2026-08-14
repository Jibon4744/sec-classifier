import io
import os
import unittest
from unittest.mock import patch

from PIL import Image
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Set up dummy environment variables before importing settings
os.environ["OPENAI_API_KEY"] = "fake-key-for-testing"

# Build a lightweight app from the router so tests stay hermetic:
# importing app.main would pull in Gradio and trigger model preload on startup.
from app.api.routes import router
from app.services.classifier import classifier_service
from app.services.llm_service import llm_service

app = FastAPI()
app.include_router(router)
client = TestClient(app)

DISEASE_RESULT = ("Downy Mildew", 0.9425, {
    "cause": "Oomycete pathogen (Plasmopara halstedii)",
    "treatment": "Use resistant seeds and apply metalaxyl seed treatment.",
    "severity": "high - can cause systemic infection"
})

STAGE_RESULT = ("Wilted", 0.8912, {
    "description": "Petals have dried and dropped.",
    "typical_days_to_harvest": "approximately 0-10 days remaining"
})

ANALYSIS_RESULT = {
    "reliability_rating": "DISTORTED",
    "scientific_rationale": "The wilted head is likely pathological rather than natural maturity.",
    "harvest_implications": "Do not trust the harvest estimate; salvage seeds early.",
    "actionable_recommendations": "Quarantine the zone and avoid seed-saving."
}

def _png_bytes(color: str = "yellow", size: int = 100) -> bytes:
    """Builds an in-memory PNG file payload."""
    image = Image.new("RGB", (size, size), color=color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

class TestApiPredictDisease(unittest.TestCase):
    @patch.object(classifier_service, "predict_disease", return_value=DISEASE_RESULT)
    def test_predict_disease_success(self, _mock):
        """Verifies a valid leaf upload returns a DiseaseResponse."""
        files = {"file": ("leaf.png", _png_bytes(), "image/png")}
        response = client.post("/api/v1/predict/disease", files=files)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["class_name"], "Downy Mildew")
        self.assertEqual(body["confidence"], 0.9425)
        self.assertEqual(body["info"]["severity"], "high - can cause systemic infection")
        self.assertEqual(body["info"]["cause"], DISEASE_RESULT[2]["cause"])
        self.assertEqual(body["info"]["treatment"], DISEASE_RESULT[2]["treatment"])

    def test_predict_disease_invalid_file(self):
        """Verifies a non-image upload is rejected with 400."""
        files = {"file": ("leaf.txt", b"this is not an image", "text/plain")}
        response = client.post("/api/v1/predict/disease", files=files)

        self.assertEqual(response.status_code, 400)
        self.assertIn("not a valid or readable image", response.json()["detail"])

    def test_predict_disease_missing_file(self):
        """Verifies a missing file is rejected with 422."""
        response = client.post("/api/v1/predict/disease")
        self.assertEqual(response.status_code, 422)

    @patch.object(classifier_service, "predict_disease", side_effect=RuntimeError("model load failed"))
    def test_predict_disease_classifier_error_returns_500(self, _mock):
        """Verifies internal classifier failures surface as 500 without leaking tracebacks."""
        files = {"file": ("leaf.png", _png_bytes(), "image/png")}
        response = client.post("/api/v1/predict/disease", files=files)

        self.assertEqual(response.status_code, 500)

class TestApiPredictGrowth(unittest.TestCase):
    @patch.object(classifier_service, "predict_growth_stage", return_value=STAGE_RESULT)
    def test_predict_growth_success(self, _mock):
        """Verifies a valid flower upload returns a StageResponse."""
        files = {"file": ("flower.png", _png_bytes("orange"), "image/png")}
        response = client.post("/api/v1/predict/growth", files=files)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["class_name"], "Wilted")
        self.assertEqual(body["confidence"], 0.8912)
        self.assertEqual(body["info"]["typical_days_to_harvest"], "approximately 0-10 days remaining")
        self.assertEqual(body["info"]["description"], STAGE_RESULT[2]["description"])

    def test_predict_growth_invalid_file(self):
        """Verifies a non-image upload is rejected with 400."""
        files = {"file": ("flower.txt", b"not an image", "text/plain")}
        response = client.post("/api/v1/predict/growth", files=files)

        self.assertEqual(response.status_code, 400)

class TestApiPredictCombined(unittest.TestCase):
    @patch.object(llm_service, "analyze_combined_specimen", return_value=ANALYSIS_RESULT)
    @patch.object(classifier_service, "predict_growth_stage", return_value=STAGE_RESULT)
    @patch.object(classifier_service, "predict_disease", return_value=DISEASE_RESULT)
    def test_predict_combined_success(self, _d, _g, _llm):
        """Verifies a dual upload returns nested leaf, flower, and analysis objects."""
        files = {
            "leaf_file": ("leaf.png", _png_bytes("green"), "image/png"),
            "flower_file": ("flower.png", _png_bytes("yellow"), "image/png")
        }
        response = client.post("/api/v1/predict/combined", files=files)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["leaf_result"]["class_name"], "Downy Mildew")
        self.assertEqual(body["flower_result"]["class_name"], "Wilted")
        self.assertEqual(body["combined_analysis"]["reliability_rating"], "DISTORTED")
        self.assertEqual(body["combined_analysis"]["actionable_recommendations"], "Quarantine the zone and avoid seed-saving.")

    def test_predict_combined_missing_flower_file(self):
        """Verifies a combined request missing one file is rejected with 422."""
        files = {"leaf_file": ("leaf.png", _png_bytes(), "image/png")}
        response = client.post("/api/v1/predict/combined", files=files)

        self.assertEqual(response.status_code, 422)

    @patch.object(classifier_service, "predict_disease", side_effect=Exception("classifier failed"))
    def test_predict_combined_classifier_error_returns_500(self, _mock):
        """Verifies unexpected errors in the combined flow return a generic 500."""
        files = {
            "leaf_file": ("leaf.png", _png_bytes(), "image/png"),
            "flower_file": ("flower.png", _png_bytes(), "image/png")
        }
        response = client.post("/api/v1/predict/combined", files=files)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Internal server error occurred.")

    @patch.object(llm_service, "analyze_combined_specimen", side_effect=ValueError("LLM returned invalid JSON"))
    @patch.object(classifier_service, "predict_growth_stage", return_value=STAGE_RESULT)
    @patch.object(classifier_service, "predict_disease", return_value=DISEASE_RESULT)
    def test_predict_combined_llm_validation_error_returns_400(self, _d, _g, _llm):
        """Verifies LLM validation errors surface as a 400 Bad Request."""
        files = {
            "leaf_file": ("leaf.png", _png_bytes(), "image/png"),
            "flower_file": ("flower.png", _png_bytes(), "image/png")
        }
        response = client.post("/api/v1/predict/combined", files=files)

        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid JSON", response.json()["detail"])

    @patch.object(llm_service, "analyze_combined_specimen", side_effect=RuntimeError("LLM API unreachable"))
    @patch.object(classifier_service, "predict_growth_stage", return_value=STAGE_RESULT)
    @patch.object(classifier_service, "predict_disease", return_value=DISEASE_RESULT)
    def test_predict_combined_llm_server_error_returns_502(self, _d, _g, _llm):
        """Verifies LLM transport failures surface as a 502 Bad Gateway."""
        files = {
            "leaf_file": ("leaf.png", _png_bytes(), "image/png"),
            "flower_file": ("flower.png", _png_bytes(), "image/png")
        }
        response = client.post("/api/v1/predict/combined", files=files)

        self.assertEqual(response.status_code, 502)
        self.assertIn("LLM API", response.json()["detail"])

if __name__ == '__main__':
    unittest.main()
