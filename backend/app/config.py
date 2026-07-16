"""Application configuration."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with all 11 AI providers."""

    # ============================================
    # 1. Groq API (Primary)
    # ============================================
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    groq_default_model: str = os.getenv("GROQ_DEFAULT_MODEL", "llama-3.3-70b-versatile")
    groq_temperature: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    groq_max_tokens: int = int(os.getenv("GROQ_MAX_TOKENS", "2048"))

    # ============================================
    # 2. OpenAI
    # ============================================
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_default_model: str = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o")

    # ============================================
    # 3. Google Gemini
    # ============================================
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_base_url: str = os.getenv("GOOGLE_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    google_default_model: str = os.getenv("GOOGLE_DEFAULT_MODEL", "gemini-1.5-pro")

    # ============================================
    # 4. Anthropic Claude
    # ============================================
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_base_url: str = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")
    anthropic_default_model: str = os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-3-5-sonnet-20241022")

    # ============================================
    # 5. Mistral AI
    # ============================================
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")
    mistral_base_url: str = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
    mistral_default_model: str = os.getenv("MISTRAL_DEFAULT_MODEL", "mistral-large-latest")

    # ============================================
    # 6. Cohere
    # ============================================
    cohere_api_key: str = os.getenv("COHERE_API_KEY", "")
    cohere_base_url: str = os.getenv("COHERE_BASE_URL", "https://api.cohere.com/v1")
    cohere_default_model: str = os.getenv("COHERE_DEFAULT_MODEL", "command-r-plus")

    # ============================================
    # 7. Ollama (Local)
    # ============================================
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    ollama_default_model: str = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3")
    ollama_fallback_model: str = os.getenv("OLLAMA_FALLBACK_MODEL", "phi4-mini")
    localai_host: str = os.getenv("LOCALAI_HOST", "http://localhost:8080")

    # ============================================
    # 8. Hugging Face (FREE)
    # ============================================
    hf_api_key: str = os.getenv("HF_API_KEY", "")
    hf_base_url: str = os.getenv("HF_BASE_URL", "https://api-inference.huggingface.co/models")
    hf_default_model: str = os.getenv("HF_DEFAULT_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")

    # ============================================
    # 9. OpenRouter (FREE models available)
    # ============================================
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_default_model: str = os.getenv("OPENROUTER_DEFAULT_MODEL", "meta-llama/llama-3.1-70b-instruct:free")

    # ============================================
    # 10. xAI (Grok)
    # ============================================
    xai_api_key: str = os.getenv("XAI_API_KEY", "")
    xai_base_url: str = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
    xai_default_model: str = os.getenv("XAI_DEFAULT_MODEL", "grok-beta")

    # ============================================
    # 11. KIMI (Moonshot)
    # ============================================
    kimi_api_key: str = os.getenv("KIMI_API_KEY", "")
    kimi_base_url: str = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
    kimi_default_model: str = os.getenv("KIMI_DEFAULT_MODEL", "moonshot-v1-8k")

    # ============================================
    # LLM Mode
    # "groq" | "openai" | "google" | "anthropic" | "mistral" | "cohere" |
    # "ollama" | "huggingface" | "openrouter" | "xai" | "kimi" | "auto"
    # ============================================
    llm_mode: str = os.getenv("LLM_MODE", "groq")

    # ============================================
    # Auto-Scaling
    # ============================================
    auto_scale_enabled: bool = os.getenv("AUTO_SCALE_ENABLED", "true").lower() == "true"
    auto_scale_min_agents: int = int(os.getenv("AUTO_SCALE_MIN_AGENTS", "5"))
    auto_scale_max_agents: int = int(os.getenv("AUTO_SCALE_MAX_AGENTS", "10000"))
    auto_scale_cpu_threshold: float = float(os.getenv("AUTO_SCALE_CPU_THRESHOLD", "80.0"))
    auto_scale_memory_threshold: float = float(os.getenv("AUTO_SCALE_MEMORY_THRESHOLD", "85.0"))

    # ============================================
    # Cost Optimization
    # ============================================
    cost_budget_usd: float = float(os.getenv("COST_BUDGET_USD", "1000.0"))
    cost_alert_threshold: float = float(os.getenv("COST_ALERT_THRESHOLD", "0.8"))

    # ============================================
    # JWT
    # ============================================
    jwt_secret: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 86400

    # ============================================
    # Environment
    # ============================================
    environment: str = os.getenv("ENVIRONMENT", "production")
    debug: bool = environment == "development"

    # ============================================
    # Server
    # ============================================
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8080"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def get_settings():
    """Get application settings."""
    return settings
