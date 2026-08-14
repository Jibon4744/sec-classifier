import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
import gradio as gr

from app.core.config import settings
from app.api.routes import router as api_router
from app.frontend.interface import build_interface
from app.services.classifier import classifier_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Core Startup Actions
    logger.info("Bootstrapping Sunflower Ensemble Classifier (SEC) Application...")
    try:
        # Pre-download and allocate TFLite interpreters during start phase
        classifier_service.preload_models()
        logger.info("Local TFLite ensemble models successfully preloaded and cached.")
    except Exception as e:
        logger.error(f"Critical startup failure while loading TFLite models: {e}")
        # Allow server to start even if models fail (useful for local debugging or env changes)
        
    yield
    # Cleanup / Shutdown Actions
    logger.info("Shutting down SEC application context...")

# Instantiate FastAPI application
app = FastAPI(
    title="Sunflower Ensemble Classifier (SEC)",
    description="Agronomic intelligence API diagnosing leaf disease and evaluating growth status.",
    version="1.0.0",
    lifespan=lifespan
)

# Register programmatic routes
app.include_router(api_router)

# Mount the interactive Gradio UI at the root path
demo = build_interface()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    # Allow running directly via python app/main.py
    logger.info(f"Launching development server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
