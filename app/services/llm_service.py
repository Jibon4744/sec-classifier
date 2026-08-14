import json
import logging
from openai import OpenAI
from app.core.config import settings
from app.core.prompts import COMBINED_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model_name = settings.OPENAI_MODEL_NAME
        
    def _get_client(self) -> OpenAI:
        """Instantiates the OpenAI client. Validates API key presence."""
        if not self.api_key:
            logger.error("OPENAI_API_KEY environment variable is not configured.")
            raise ValueError(
                "LLM API Key is missing. Please set the OPENAI_API_KEY environment variable in settings."
            )
        return OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _clean_json_response(self, text: str) -> str:
        """Removes markdown code blocks if the LLM wrapped the JSON output in them."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def analyze_combined_specimen(
        self,
        disease_name: str,
        disease_conf: float,
        disease_info: dict,
        stage_name: str,
        stage_conf: float,
        stage_info: dict
    ) -> dict:
        """
        Sends prediction metrics and static lookup details to the LLM to analyze the
        pathological/physiological interaction. Returns a parsed JSON dictionary.
        """
        client = self._get_client()
        
        # Compile prompt
        prompt = COMBINED_ANALYSIS_PROMPT.format(
            disease_name=disease_name,
            disease_conf=disease_conf * 100.0,
            disease_cause=disease_info.get("cause", "N/A"),
            disease_severity=disease_info.get("severity", "N/A"),
            disease_treatment=disease_info.get("treatment", "N/A"),
            stage_name=stage_name,
            stage_conf=stage_conf * 100.0,
            stage_description=stage_info.get("description", "N/A"),
            stage_days_to_harvest=stage_info.get("typical_days_to_harvest", "N/A")
        )
        
        try:
            logger.info(f"Dispatching prompt to LLM ({self.model_name})...")
            
            # Request completion
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional agricultural advisor and JSON generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            cleaned_text = self._clean_json_response(response_text)
            
            # Load into python dict
            analysis_dict = json.loads(cleaned_text)
            
            # Validate core keys to ensure contract is met
            required_keys = ["reliability_rating", "scientific_rationale", "harvest_implications", "actionable_recommendations"]
            for key in required_keys:
                if key not in analysis_dict:
                    analysis_dict[key] = "N/A"
                    
            logger.info("Successfully received and parsed LLM assessment.")
            return analysis_dict
            
        except json.JSONDecodeError as jde:
            logger.error(f"Failed to parse JSON response from LLM: {jde}. Raw: {response_text}")
            raise ValueError(f"LLM did not return a valid JSON structure: {jde}")
        except Exception as e:
            logger.error(f"LLM API request failed: {e}")
            raise RuntimeError(f"Failed to communicate with LLM API: {e}")

# Singleton instance
llm_service = LLMService()
