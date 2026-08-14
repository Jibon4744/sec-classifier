from pydantic import BaseModel
from typing import Optional, List, Union

# --- Mode 1: Disease schemas ---

class DiseaseInfo(BaseModel):
    cause: str
    treatment: str
    severity: str

class DiseaseResponse(BaseModel):
    class_name: str
    confidence: float
    info: DiseaseInfo


# --- Mode 2: Growth Stage schemas ---

class StageInfo(BaseModel):
    description: str
    typical_days_to_harvest: str
    verify_note: Optional[str] = None

class StageResponse(BaseModel):
    class_name: str
    confidence: float
    info: StageInfo


# --- Mode 3: Combined schemas ---

class CombinedAnalysis(BaseModel):
    reliability_rating: str  # HIGH, MEDIUM, LOW, DISTORTED
    scientific_rationale: str
    harvest_implications: str
    actionable_recommendations: Union[str, List[str]]

class CombinedResponse(BaseModel):
    leaf_result: DiseaseResponse
    flower_result: StageResponse
    combined_analysis: CombinedAnalysis
