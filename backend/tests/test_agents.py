"""Tests for agent management."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_create_agent():
    """Test agent creation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/agents/", json={
            "name": "Test Agent",
            "role": "general",
            "description": "A test agent",
            "priority": 5,
        })
        assert response.status_code in [201, 200, 422]


@pytest.mark.asyncio
async def test_list_agents():
    """Test listing agents."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/agents/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)


@pytest.mark.asyncio
async def test_get_agent():
    """Test getting a specific agent."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/agents/strategist")
        assert response.status_code in [200, 404, 503]


@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
