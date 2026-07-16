"""Tests for Unified AI Service."""
import pytest
from app.services.unified_ai_service import UnifiedAIService, get_unified_ai_service


@pytest.mark.asyncio
async def test_unified_service_init():
    """Test unified service initialization."""
    service = UnifiedAIService()
    assert service is not None
    assert service.mode in ["groq", "local", "auto"]


@pytest.mark.asyncio
async def test_unified_service_metrics():
    """Test metrics initialization."""
    service = UnifiedAIService()
    metrics = service.get_metrics()
    assert "cloud_requests" in metrics
    assert "local_requests" in metrics
    assert "fallback_count" in metrics
    assert "errors" in metrics


@pytest.mark.asyncio
async def test_get_unified_ai_service_singleton():
    """Test singleton pattern."""
    service1 = await get_unified_ai_service()
    service2 = await get_unified_ai_service()
    assert service1 is service2
