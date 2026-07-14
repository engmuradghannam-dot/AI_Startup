"""
Health Router - Always available, no DB required
"""
from fastapi import APIRouter, HTTPException
import time

router = APIRouter()

_start_time = time.time()

@router.get("/")
async def health_status():
    """Basic health status"""
    uptime = time.time() - _start_time
    return {
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "service": "ai-startup"
    }

@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes/Railway"""
    return {"ready": True}

@router.get("/live")
async def liveness_check():
    """Liveness probe for Kubernetes/Railway"""
    return {"alive": True}
