"""
Configuration module - Railway Compatible
"""
import os
import secrets
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with Railway fallbacks"""

    # Application
    APP_NAME: str = Field(default="AI Startup", alias="APP_NAME")
    DEBUG: bool = Field(default=False, alias="DEBUG")

    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        alias="SECRET_KEY"
    )

    # MongoDB - Railway compatible
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017/ai_startup",
        alias="MONGODB_URL"
    )
    MONGODB_DB_NAME: str = Field(default="ai_startup", alias="MONGODB_DB_NAME")

    # Redis - Optional
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL"
    )

    # Groq API
    GROQ_API_KEY: str = Field(default="", alias="GROQ_API_KEY")

    # Celery - Optional
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        alias="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        alias="CELERY_RESULT_BACKEND"
    )

    # Server
    PORT: int = Field(default=8000, alias="PORT")
    HOST: str = Field(default="0.0.0.0", alias="HOST")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
