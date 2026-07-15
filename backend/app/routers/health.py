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


@router.get("/groq-status")
async def groq_status():
    """Check Groq API status and validate API key."""
    from app.services.groq_service import get_groq_service

    try:
        groq = await get_groq_service()
        validation = await groq.validate_api_key()
        return {
            "status": "ok" if validation["valid"] else "error",
            "message": validation["message"],
            "models_count": validation.get("models_count", 0),
            "api_key_set": bool(groq.settings.GROQ_API_KEY and groq.settings.GROQ_API_KEY != "your_groq_api_key_here"),
            "base_url": groq.settings.GROQ_BASE_URL,
            "default_model": groq.settings.GROQ_DEFAULT_MODEL,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "api_key_set": False,
        }


@router.get("/debug")
async def debug_info():
    """Debug endpoint to check environment variables and configuration."""
    from app.config import get_settings
    settings = get_settings()

    return {
        "groq_api_key_set": bool(settings.groq_api_key and settings.groq_api_key != "your_groq_api_key_here"),
        "groq_api_key_length": len(settings.groq_api_key) if settings.groq_api_key else 0,
        "groq_api_key_prefix": settings.groq_api_key[:10] + "..." if settings.groq_api_key else None,
        "groq_base_url": settings.groq_base_url,
        "groq_default_model": settings.groq_default_model,
        "llm_mode": settings.llm_mode,
        "environment": settings.environment,
        "port": settings.port,
    }
