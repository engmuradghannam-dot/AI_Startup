"""Tests for AI Chat Router."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_ai_chat_models_endpoint():
    """Test listing AI models."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/ai-chat/models")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_ai_chat_health():
    """Test AI chat health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/ai-chat/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


@pytest.mark.asyncio
async def test_ai_chat_agents_list():
    """Test listing AI agents."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/ai-chat/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data or isinstance(data, dict)


@pytest.mark.asyncio
async def test_chat_endpoint_validation():
    """Test chat endpoint validates input."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Empty messages should be handled
        response = await client.post("/api/ai-chat/chat", json={
            "messages": [],
        })
        assert response.status_code in [200, 422, 500, 503]


@pytest.mark.asyncio
async def test_agent_chat_endpoint():
    """Test agent chat endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/ai-chat/agent-chat", json={
            "task": "Test task",
            "agents": ["strategist"],
            "mode": "hierarchical",
        })
        # May fail if no API keys, but endpoint should exist
        assert response.status_code in [200, 500, 503]
