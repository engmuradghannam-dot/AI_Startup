"""Tests for Multi-Provider AI Service - 11 providers."""
import pytest
from app.services.multi_provider_ai import MultiProviderAIService, get_multi_provider_service


@pytest.mark.asyncio
async def test_multi_provider_service_init():
    """Test service initialization."""
    service = MultiProviderAIService()
    assert service is not None
    assert len(service.PROVIDERS) == 11

    # Check all providers defined
    expected = ["groq", "openai", "google", "anthropic", "mistral", 
                "cohere", "ollama", "huggingface", "openrouter", "xai", "kimi"]
    for pid in expected:
        assert pid in service.PROVIDERS


@pytest.mark.asyncio
async def test_provider_configs():
    """Test each provider has required config."""
    service = MultiProviderAIService()

    for pid, config in service.PROVIDERS.items():
        assert "name" in config
        assert "base_url" in config
        assert "models" in config
        assert "headers" in config
        assert "chat_endpoint" in config
        assert len(config["models"]) > 0


@pytest.mark.asyncio
async def test_get_api_key_from_env():
    """Test API key retrieval from environment."""
    import os
    service = MultiProviderAIService()

    # Test with no env var
    key = service._get_api_key("nonexistent")
    assert key is None or key == ""

    # Ollama should return "local"
    ollama_key = service._get_api_key("ollama")
    assert ollama_key == "local"


@pytest.mark.asyncio
async def test_get_base_url():
    """Test base URL retrieval."""
    service = MultiProviderAIService()

    groq_url = service._get_base_url("groq")
    assert "groq.com" in groq_url

    openai_url = service._get_base_url("openai")
    assert "openai.com" in openai_url


@pytest.mark.asyncio
async def test_get_model():
    """Test default model retrieval."""
    service = MultiProviderAIService()

    groq_model = service._get_model("groq")
    assert groq_model in service.PROVIDERS["groq"]["models"]

    openai_model = service._get_model("openai")
    assert openai_model in service.PROVIDERS["openai"]["models"]


@pytest.mark.asyncio
async def test_get_multi_provider_service_singleton():
    """Test service singleton pattern."""
    service1 = await get_multi_provider_service()
    service2 = await get_multi_provider_service()
    assert service1 is service2


@pytest.mark.asyncio
async def test_metrics_initialization():
    """Test metrics are initialized to zero."""
    service = MultiProviderAIService()
    metrics = await service.get_metrics()
    assert metrics["total_requests"] == 0
    assert metrics["total_errors"] == 0
    assert metrics["active_provider"] is None
