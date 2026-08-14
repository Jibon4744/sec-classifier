import json
import unittest
from unittest.mock import patch, MagicMock

# Set up dummy environment variables before importing settings
import os
os.environ["OPENAI_API_KEY"] = "fake-key-for-testing"

from app.services.llm_service import LLMService

REQUIRED_KEYS = ["reliability_rating", "scientific_rationale", "harvest_implications", "actionable_recommendations"]

def _valid_analysis_dict():
    return {
        "reliability_rating": "DISTORTED",
        "scientific_rationale": "Downy Mildew causes systemic stress that prematurely ages the head.",
        "harvest_implications": "Harvest immediately to salvage seeds.",
        "actionable_recommendations": "Quarantine the affected zone and avoid seed-saving."
    }

def _mock_chat_response(content: str):
    """Builds a mock OpenAI chat completion whose message content is the given string."""
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response

class TestLLMService(unittest.TestCase):
    def setUp(self):
        self.service = LLMService()
        self.disease_info = {
            "cause": "Oomycete pathogen (Plasmopara halstedii)",
            "treatment": "Use resistant seeds and apply metalaxyl seed treatment.",
            "severity": "high - can cause systemic infection"
        }
        self.stage_info = {
            "description": "Petals have dried and dropped.",
            "typical_days_to_harvest": "approximately 0-10 days remaining"
        }

    def test_clean_json_response_strips_code_block(self):
        """Verifies markdown-fenced JSON is unwrapped."""
        raw = "```json\n{\"reliability_rating\": \"HIGH\"}\n```"
        cleaned = self.service._clean_json_response(raw)
        self.assertEqual(cleaned, "{\"reliability_rating\": \"HIGH\"}")

    def test_clean_json_response_strips_bare_fence(self):
        """Verifies generic ``` fences (without language tag) are handled."""
        raw = "```\n{\"a\": 1}\n```"
        self.assertEqual(self.service._clean_json_response(raw), "{\"a\": 1}")

    def test_clean_json_response_plain_text_unchanged(self):
        """Verifies plain JSON without fences is only stripped of whitespace."""
        raw = "  {\"a\": 1}  "
        self.assertEqual(self.service._clean_json_response(raw), "{\"a\": 1}")

    def test_get_client_raises_without_api_key(self):
        """Verifies a missing API key raises a clear ValueError."""
        self.service.api_key = ""
        with self.assertRaises(ValueError) as ctx:
            self.service._get_client()
        self.assertIn("OPENAI_API_KEY", str(ctx.exception))

    @patch("app.services.llm_service.OpenAI")
    def test_analyze_returns_parsed_json(self, mock_openai):
        """Verifies a valid LLM JSON payload is parsed and returned."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_chat_response(
            json.dumps(_valid_analysis_dict())
        )

        result = self.service.analyze_combined_specimen(
            disease_name="Downy Mildew",
            disease_conf=0.9,
            disease_info=self.disease_info,
            stage_name="Wilted",
            stage_conf=0.8,
            stage_info=self.stage_info
        )

        self.assertEqual(result["reliability_rating"], "DISTORTED")
        self.assertEqual(result["actionable_recommendations"], "Quarantine the affected zone and avoid seed-saving.")
        # All contract keys must be present
        for key in REQUIRED_KEYS:
            self.assertIn(key, result)

    @patch("app.services.llm_service.OpenAI")
    def test_analyze_handles_markdown_wrapped_json(self, mock_openai):
        """Verifies the service tolerates ```json fences around the payload."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        payload = _valid_analysis_dict()
        payload["reliability_rating"] = "HIGH"
        mock_client.chat.completions.create.return_value = _mock_chat_response(
            "```json\n" + json.dumps(payload) + "\n```"
        )

        result = self.service.analyze_combined_specimen(
            disease_name="Healthy",
            disease_conf=0.98,
            disease_info=self.disease_info,
            stage_name="Full Bloom",
            stage_conf=0.91,
            stage_info=self.stage_info
        )
        self.assertEqual(result["reliability_rating"], "HIGH")

    @patch("app.services.llm_service.OpenAI")
    def test_analyze_fills_missing_contract_keys(self, mock_openai):
        """Verifies missing contract keys default to 'N/A' instead of crashing."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        partial = {"reliability_rating": "LOW"}
        mock_client.chat.completions.create.return_value = _mock_chat_response(json.dumps(partial))

        result = self.service.analyze_combined_specimen(
            disease_name="Powdery Mildew",
            disease_conf=0.5,
            disease_info=self.disease_info,
            stage_name="Early Bloom",
            stage_conf=0.5,
            stage_info=self.stage_info
        )
        self.assertEqual(result["reliability_rating"], "LOW")
        self.assertEqual(result["scientific_rationale"], "N/A")
        self.assertEqual(result["harvest_implications"], "N/A")
        self.assertEqual(result["actionable_recommendations"], "N/A")

    @patch("app.services.llm_service.OpenAI")
    def test_analyze_invalid_json_raises_value_error(self, mock_openai):
        """Verifies malformed LLM JSON surfaces as a ValueError."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_chat_response("this is not json")

        with self.assertRaises(ValueError):
            self.service.analyze_combined_specimen(
                disease_name="Downy Mildew",
                disease_conf=0.9,
                disease_info=self.disease_info,
                stage_name="Wilted",
                stage_conf=0.8,
                stage_info=self.stage_info
            )

    @patch("app.services.llm_service.OpenAI")
    def test_analyze_api_error_raises_runtime_error(self, mock_openai):
        """Verifies transport-level failures surface as RuntimeError."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("connection timeout")

        with self.assertRaises(RuntimeError) as ctx:
            self.service.analyze_combined_specimen(
                disease_name="Downy Mildew",
                disease_conf=0.9,
                disease_info=self.disease_info,
                stage_name="Wilted",
                stage_conf=0.8,
                stage_info=self.stage_info
            )
        self.assertIn("Failed to communicate with LLM API", str(ctx.exception))

    @patch("app.services.llm_service.OpenAI")
    def test_prompt_contains_interpolated_confidence(self, mock_openai):
        """Verifies confidence is converted to percentage and injected into the prompt."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_chat_response(
            json.dumps(_valid_analysis_dict())
        )

        self.service.analyze_combined_specimen(
            disease_name="Downy Mildew",
            disease_conf=0.9,
            disease_info=self.disease_info,
            stage_name="Wilted",
            stage_conf=0.8,
            stage_info=self.stage_info
        )

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        user_content = call_kwargs["messages"][1]["content"]
        self.assertIn("Downy Mildew (Confidence: 90.00%)", user_content)
        self.assertIn("Wilted (Confidence: 80.00%)", user_content)
        self.assertEqual(call_kwargs["temperature"], 0.2)
        self.assertEqual(call_kwargs["response_format"], {"type": "json_object"})

if __name__ == '__main__':
    unittest.main()
