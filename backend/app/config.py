"""Application configuration."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # MongoDB
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb+srv://engmuradghannam_db_user:IWqsSLrcTgnwdgpD@cluster0.ouxl0wd.mongodb.net/ai_startup?retryWrites=true&w=majority")
    database_name: str = os.getenv("DATABASE_NAME", "ai_startup")

    # Groq API (optional - fallback)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    # Local LLM (Ollama)
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_default_model: str = os.getenv("OLLAMA_DEFAULT_MODEL", "phi4-mini")
    ollama_fallback_model: str = os.getenv("OLLAMA_FALLBACK_MODEL", "qwen3:0.6b")

    # LocalAI (alternative local provider)
    localai_host: str = os.getenv("LOCALAI_HOST", "http://localhost:8080")
    localai_enabled: bool = os.getenv("LOCALAI_ENABLED", "false").lower() == "true"

    # LLM Mode: "local" | "groq" | "auto" (auto tries local first, then groq)
    llm_mode: str = os.getenv("LLM_MODE", "auto")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 86400  # 24 hours

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
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
