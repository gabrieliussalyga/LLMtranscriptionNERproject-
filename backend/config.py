"""Application configuration."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    google_api_key: str = ""
    openai_api_key: str = ""

    # LLM Provider: "openai" or "gemini"
    llm_provider: str = "openai"

    # Gemini settings
    gemini_model: str = "models/gemini-3-pro-preview"

    # OpenAI settings
    openai_model: str = "gpt-4o"

    # CORS settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
