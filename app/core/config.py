import os
from PIL import Image
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    HOST: str = "0.0.0.0"
    PORT: int = 7860
    
    # Hugging Face Config
    HF_REPO_ID: str = "Jibon4744/SEC-sunflower-classifier"

    # Directory where downloaded TFLite models are cached by huggingface_hub.
    # When None, huggingface_hub uses HF_HOME (set in Dockerfile to
    # /home/user/.cache/huggingface) so downloads persist across restarts.
    HF_CACHE_DIR: str = ""

    # Maximum time (seconds) to wait for a model download from HF Hub.
    HF_HUB_DOWNLOAD_TIMEOUT: int = 300
    
    # LLM Config (configurable via environment variables)
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"

    # Maximum image size (in pixels) accepted for uploads. Raised above PIL's
    # default (178,956,970) so high-resolution mobile camera photos (e.g. 200 MP)
    # can be decoded. Higher values increase peak decode memory and DoS surface.
    MAX_IMAGE_PIXELS: int = 50_000_000

    # Ensemble fusion strategy for the 4-model TFLite ensemble:
    # "geometric" = weighted geometric mean (crisp confidence when models agree),
    # "mean" = weighted arithmetic mean.
    ENSEMBLE_FUSION: str = "geometric"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Apply the configured guard process-wide BEFORE any Gradio/FastAPI
# preprocessing decodes a user upload; otherwise PIL raises a
# DecompressionBombError for high-resolution camera photos.
Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS
