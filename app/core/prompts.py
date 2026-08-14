COMBINED_ANALYSIS_PROMPT = """You are an expert plant pathologist and agronomist specializing in sunflower crops (Helianthus annuus).
Analyze the following diagnostic results for a single sunflower specimen:

---
DIAGNOSTIC DATA:
1. Leaf Disease Detected: {disease_name} (Confidence: {disease_conf:.2f}%)
   - Cause: {disease_cause}
   - Severity: {disease_severity}
   - Standard Treatment: {disease_treatment}

2. Flower Growth Stage Classified: {stage_name} (Confidence: {stage_conf:.2f}%)
   - Stage Description: {stage_description}
   - Estimated Days to Harvest (Standard): {stage_days_to_harvest}
---

TASK:
Determine if the flower's growth stage appearance is a reliable indicator of natural maturity, or if it is likely distorted, stunted, or accelerated prematurely by the detected disease.

Generate a structured JSON response containing:
1. "reliability_rating": "HIGH", "MEDIUM", "LOW", or "DISTORTED".
2. "scientific_rationale": A detailed explanation of how the pathology of {disease_name} interacts with the physiology of the {stage_name} stage (e.g., does the disease cause premature flower drooping, petal drying, or head stunting?).
3. "harvest_implications": Adjusted advice on harvesting (e.g., should they harvest early, is the crop lost, or can they trust the days-to-harvest estimate?).
4. "actionable_recommendations": Specific steps the grower should take next, prioritizing containment of the pathogen.

Format the output strictly as a single JSON object. Do not include markdown code block formatting or extra text outside the JSON structure.
"""
