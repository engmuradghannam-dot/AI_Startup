"""Tests for Settings API - 11 AI Providers & Ensemble Mode."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_list_providers():
    """Test listing all 11 AI providers."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/settings/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 11  # All 11 providers should be present

        # Check all providers exist
        provider_ids = [p["id"] for p in data]
        expected = ["groq", "openai", "google", "anthropic", "mistral", 
                    "cohere", "ollama", "huggingface", "openrouter", "xai", "kimi"]
        for pid in expected:
            assert pid in provider_ids, f"Provider {pid} not found"


@pytest.mark.asyncio
async def test_get_single_provider():
    """Test getting a specific provider."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/settings/providers/groq")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "groq"
        assert data["name"] == "Groq"
        assert "api_key" in data
        assert "base_url" in data
        assert "default_model" in data


@pytest.mark.asyncio
async def test_update_provider_api_key():
    """Test updating provider API key."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch("/api/settings/providers/groq", json={
            "api_key": "test-groq-key-12345",
            "default_model": "llama3-70b",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["api_key"] == "test-groq-key-12345"
        assert data["default_model"] == "llama3-70b"


@pytest.mark.asyncio
async def test_activate_multiple_providers():
    """Test activating multiple providers for ensemble mode."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Activate Groq
        resp1 = await client.patch("/api/settings/providers/groq", json={
            "is_active": True,
            "api_key": "gsk_test_groq_key",
        })
        assert resp1.status_code == 200
        assert resp1.json()["is_active"] == True

        # Activate OpenAI
        resp2 = await client.patch("/api/settings/providers/openai", json={
            "is_active": True,
            "api_key": "sk-test-openai-key",
        })
        assert resp2.status_code == 200
        assert resp2.json()["is_active"] == True

        # Verify all are active
        list_resp = await client.get("/api/settings/providers")
        providers = list_resp.json()
        active = [p for p in providers if p["is_active"]]
        assert len(active) >= 2


@pytest.mark.asyncio
async def test_llm_mode_settings():
    """Test LLM mode configuration."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Set ensemble mode
        response = await client.post("/api/settings/llm-mode/ensemble")
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "ensemble"

        # Set groq mode
        response = await client.post("/api/settings/llm-mode/groq")
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "groq"

        # Set auto mode
        response = await client.post("/api/settings/llm-mode/auto")
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "auto"


@pytest.mark.asyncio
async def test_provider_not_found():
    """Test 404 for non-existent provider."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/settings/providers/nonexistent")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_all_providers_have_required_fields():
    """Test that all providers have required configuration fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/settings/providers")
        providers = response.json()

        required_fields = ["id", "name", "api_key", "base_url", "default_model", 
                          "is_active", "temperature", "max_tokens"]

        for provider in providers:
            for field in required_fields:
                assert field in provider, f"Provider {provider['id']} missing field: {field}"


@pytest.mark.asyncio
async def test_provider_temperature_range():
    """Test temperature setting within valid range."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch("/api/settings/providers/groq", json={
            "temperature": 1.5,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] == 1.5

        response = await client.patch("/api/settings/providers/groq", json={
            "temperature": 0.0,
        })
        assert response.status_code == 200
        assert response.json()["temperature"] == 0.0


@pytest.mark.asyncio
async def test_ensemble_endpoint_exists():
    """Test that ensemble endpoint exists and accepts requests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First activate at least one provider
        await client.patch("/api/settings/providers/groq", json={
            "is_active": True,
            "api_key": "test-key",
        })

        response = await client.post("/api/settings/ensemble", json={
            "task": "What is 2+2?",
            "mode": "parallel",
        })
        # Should either succeed or return 503 if no real API keys
        assert response.status_code in [200, 503]
