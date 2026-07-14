"""Health and monitoring API routes."""
from fastapi import APIRouter
from datetime import datetime

from app.services.performance_monitor import get_performance_monitor
from app.services.cost_optimizer import get_cost_optimizer
from app.services.security_guard import get_security_guard
from app.config import get_settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": get_settings().APP_VERSION,
    }


@router.get("/metrics")
async def get_metrics():
    """Get system performance metrics."""
    monitor = await get_performance_monitor()
    return await monitor.get_dashboard_metrics()


@router.get("/costs")
async def get_costs():
    """Get cost optimization report."""
    optimizer = await get_cost_optimizer()
    return optimizer.get_cost_report()


@router.get("/security")
async def get_security_report():
    """Get security status report."""
    guard = await get_security_guard()
    return guard.get_security_report()


@router.get("/alerts")
async def get_alerts():
    """Get current system alerts."""
    monitor = await get_performance_monitor()
    return await monitor.check_alerts()
