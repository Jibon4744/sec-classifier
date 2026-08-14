import io
import logging
from PIL import Image
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.classifier import classifier_service
from app.services.llm_service import llm_service
from app.api.schemas import DiseaseResponse, StageResponse, CombinedResponse, CombinedAnalysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

def _load_image(file: UploadFile) -> Image.Image:
    """Safely parses bytes into a PIL Image."""
    try:
        contents = file.file.read()
        image = Image.open(io.BytesIO(contents))
        # Trigger actual load to verify image integrity
        image.load()
        return image
    except Exception as e:
        logger.error(f"Image parsing failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Uploaded file '{file.filename}' is not a valid or readable image."
        )

@router.post("/predict/disease", response_model=DiseaseResponse)
async def predict_disease(file: UploadFile = File(...)):
    """Diagnoses leaf diseases from an uploaded leaf image."""
    image = _load_image(file)
    try:
        class_name, confidence, info = classifier_service.predict_disease(image)
        return DiseaseResponse(
            class_name=class_name,
            confidence=confidence,
            info=info
        )
    except Exception as e:
        logger.error(f"Prediction failed for leaf: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/growth", response_model=StageResponse)
async def predict_growth(file: UploadFile = File(...)):
    """Classifies sunflower head growth stage from an uploaded flower image."""
    image = _load_image(file)
    try:
        class_name, confidence, info = classifier_service.predict_growth_stage(image)
        return StageResponse(
            class_name=class_name,
            confidence=confidence,
            info=info
        )
    except Exception as e:
        logger.error(f"Prediction failed for flower: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/combined", response_model=CombinedResponse)
async def predict_combined(
    leaf_file: UploadFile = File(...),
    flower_file: UploadFile = File(...)
):
    """
    Executes local TFLite predictions for both leaf disease and flower growth stage,
    then dispatches metrics to the LLM to verify agronomic relationships.
    """
    leaf_image = _load_image(leaf_file)
    flower_image = _load_image(flower_file)
    
    try:
        # 1. Run local classifiers
        leaf_class, leaf_conf, leaf_info = classifier_service.predict_disease(leaf_image)
        flower_class, flower_conf, flower_info = classifier_service.predict_growth_stage(flower_image)
        
        # 2. Run LLM cross-analysis
        analysis_dict = llm_service.analyze_combined_specimen(
            disease_name=leaf_class,
            disease_conf=leaf_conf,
            disease_info=leaf_info,
            stage_name=flower_class,
            stage_conf=flower_conf,
            stage_info=flower_info
        )
        
        # 3. Assemble response objects
        leaf_response = DiseaseResponse(class_name=leaf_class, confidence=leaf_conf, info=leaf_info)
        flower_response = StageResponse(class_name=flower_class, confidence=flower_conf, info=flower_info)
        combined_analysis = CombinedAnalysis(
            reliability_rating=analysis_dict.get("reliability_rating", "N/A"),
            scientific_rationale=analysis_dict.get("scientific_rationale", "N/A"),
            harvest_implications=analysis_dict.get("harvest_implications", "N/A"),
            actionable_recommendations=analysis_dict.get("actionable_recommendations", "N/A")
        )
        
        return CombinedResponse(
            leaf_result=leaf_response,
            flower_result=flower_response,
            combined_analysis=combined_analysis
        )
        
    except ValueError as ve:
        logger.error(f"Combined analysis validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        logger.error(f"Combined analysis server/LLM error: {re}")
        raise HTTPException(status_code=502, detail=str(re))
    except Exception as e:
        logger.error(f"Unexpected error in combined prediction flow: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred.")
