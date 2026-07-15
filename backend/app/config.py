"""Application configuration."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Groq API (primary for cloud)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    # Local LLM (Ollama) - optional, for local dev
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_default_model: str = os.getenv("OLLAMA_DEFAULT_MODEL", "phi4-mini")
    ollama_fallback_model: str = os.getenv("OLLAMA_FALLBACK_MODEL", "qwen3:0.6b")

    # LLM Mode: "groq" | "local" | "auto"
    llm_mode: str = os.getenv("LLM_MODE", "groq")

    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 86400

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "production")
    debug: bool = environment == "development"

    # Server
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8080"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def get_settings():
    """Get application settings."""
    return settings
