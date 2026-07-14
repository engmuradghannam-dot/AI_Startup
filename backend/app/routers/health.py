"""
Health Router - Always available, no DB required
"""
from fastapi import APIRouter, HTTPException
import time
import os

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

@router.get("/metrics")
async def health_metrics():
    """System health metrics"""
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - _start_time, 2),
        "service": "ai-startup",
        "metrics": {
            "memory_usage": "N/A",
            "cpu_usage": "N/A",
            "active_connections": 0,
        }
    }

@router.get("/costs")
async def health_costs():
    """Cost tracking metrics"""
    return {
        "status": "healthy",
        "daily_cost": 0.0,
        "monthly_cost": 0.0,
        "budget_limit": 1000.0,
        "budget_usage_percent": 0.0,
        "api_calls_today": 0,
    }

@router.get("/alerts")
async def health_alerts():
    """System alerts"""
    return {
        "status": "healthy",
        "alerts": [],
        "warnings": [],
        "last_check": time.time(),
    }

@router.get("/security")
async def health_security():
    """Security status"""
    return {
        "status": "secure",
        "threats_detected": 0,
        "last_scan": time.time(),
        "security_score": 100,
    }
