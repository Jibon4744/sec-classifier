import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    HOST: str = "0.0.0.0"
    PORT: int = 7860
    
    # Hugging Face Config
    HF_REPO_ID: str = "Jibon4744/SEC-sunflower-classifier"
    
    # LLM Config (configurable via environment variables)
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
