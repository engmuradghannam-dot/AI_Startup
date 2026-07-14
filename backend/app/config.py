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

    # Redis - Railway provides these automatically when Redis service is added
    # Format: redis://default:${REDIS_PASSWORD}@${RAILWAY_TCP_PROXY_DOMAIN}:${RAILWAY_TCP_PROXY_PORT}
    REDIS_URL: str | None = None

    # Railway Redis individual variables (fallback)
    REDISHOST: str | None = None
    REDISPORT: str | None = None
    REDISUSER: str = "default"
    REDIS_PASSWORD: str | None = None
    RAILWAY_TCP_PROXY_DOMAIN: str | None = None
    RAILWAY_TCP_PROXY_PORT: str | None = None

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

    def get_redis_url(self) -> str | None:
        """Build Redis URL from Railway variables or return existing REDIS_URL."""
        # If full REDIS_URL is provided, use it
        if self.REDIS_URL:
            return self.REDIS_URL

        # Build from Railway individual variables
        if self.RAILWAY_TCP_PROXY_DOMAIN and self.REDIS_PASSWORD:
            host = self.RAILWAY_TCP_PROXY_DOMAIN
            port = self.RAILWAY_TCP_PROXY_PORT or "6379"
            password = self.REDIS_PASSWORD
            return f"redis://default:{password}@{host}:{port}"

        if self.REDISHOST and self.REDIS_PASSWORD:
            host = self.REDISHOST
            port = self.REDISPORT or "6379"
            user = self.REDISUSER or "default"
            password = self.REDIS_PASSWORD
            return f"redis://{user}:{password}@{host}:{port}"

        return None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
