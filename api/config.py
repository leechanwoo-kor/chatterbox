"""
Configuration settings for Chatterbox TTS API
"""

from pydantic_settings import BaseSettings
from typing import Optional

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
    preload_models: list[str] = []  # Models to preload on startup: ["turbo", "multilingual", "original"]

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

    class Config:
        env_prefix = "CHATTERBOX_"
        env_file = ".env"

settings = Settings()
