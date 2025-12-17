"""
Configuration settings for Chatterbox TTS API
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import field_validator

class Settings(BaseSettings):
    # API Settings
    api_title: str = "Chatterbox TTS API"
    api_version: str = "1.0.0"
    api_description: str = "REST API for Chatterbox Text-to-Speech models by Resemble AI"

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Model Settings
    default_model: str = "turbo"
    preload_models: list[str] = []  # Comma-separated models to preload: "turbo,multilingual,original"

    # CORS Settings
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]

    # Audio Settings
    max_text_length: int = 5000
    output_format: str = "wav"

    # Device Settings (auto-detected if not set)
    device: Optional[str] = None  # "cuda", "mps", or "cpu"

    # Hugging Face Token
    hf_token: Optional[str] = None

    @field_validator('preload_models', mode='before')
    @classmethod
    def parse_preload_models(cls, v):
        """Parse comma-separated string or empty string into list"""
        if v is None or v == "" or v == []:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            return [model.strip() for model in v.split(",") if model.strip()]
        return []

    class Config:
        env_prefix = "CHATTERBOX_"
        env_file = ".env"

settings = Settings()
