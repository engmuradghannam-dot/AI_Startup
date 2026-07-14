"""Application configuration and settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "AI Startup - Multi-Agent System"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "ai_startup"

    # Redis (optional - app works without it)
    REDIS_URL: str | None = None

    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS: int = 4096
    GROQ_TEMPERATURE: float = 0.7

    # Agent System
    MAX_AGENTS: int = 100000
    DEFAULT_AGENT_TIMEOUT: int = 300
    AGENT_POOL_SIZE: int = 100

    # Auto-Scaling
    AUTO_SCALE_ENABLED: bool = True
    AUTO_SCALE_MIN_AGENTS: int = 5
    AUTO_SCALE_MAX_AGENTS: int = 10000
    AUTO_SCALE_CPU_THRESHOLD: float = 80.0
    AUTO_SCALE_MEMORY_THRESHOLD: float = 85.0

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Monitoring
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"

    # Cost Optimization
    COST_BUDGET_USD: float = 1000.0
    COST_ALERT_THRESHOLD: float = 0.8

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
