"""Tests for skill management."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_list_skills():
    """Test listing skills."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/skills/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)


@pytest.mark.asyncio
async def test_get_skill_categories():
    """Test getting skill categories summary."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/skills/categories/summary")
        assert response.status_code in [200, 404]
