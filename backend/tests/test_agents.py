"""Tests for agent management."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_create_agent():
    """Test agent creation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/agents/", json={
            "name": "Test Agent",
            "role": "general",
            "description": "A test agent",
            "priority": 5,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["role"] == "general"


@pytest.mark.asyncio
async def test_list_agents():
    """Test listing agents."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/agents/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_agent():
    """Test getting a specific agent."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First create an agent
        create_resp = await client.post("/agents/", json={
            "name": "Get Test Agent",
            "role": "general",
        })
        agent_id = create_resp.json()["id"]

        # Get the agent
        response = await client.get(f"/agents/{agent_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Test Agent"


@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
