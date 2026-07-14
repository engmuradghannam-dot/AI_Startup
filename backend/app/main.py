"""
AI Startup - Multi-Agent System with Groq API
FastAPI Backend - Railway Compatible
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
_db_initialized = False
_start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - lazy initialization"""
    global _db_initialized

    logger.info("🚀 AI Startup Server Starting...")

    # Try to initialize MongoDB (but don't fail if unavailable)
    try:
        from app.database import init_db
        await init_db()
        _db_initialized = True
        logger.info("✅ MongoDB initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB initialization skipped: {e}")
        logger.warning("⚠️ Running in LIMITED MODE - some features unavailable")

    yield

    # Shutdown
    logger.info("🛑 AI Startup Server Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="AI Startup",
    description="Multi-Agent System with Groq API Integration",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# HEALTH ENDPOINTS - Must work without DB
# These MUST be defined BEFORE catch-all routes
# ============================================
@app.get("/health")
@app.get("/health/")
async def health_check():
    """Health check endpoint - Railway requires this at /health/"""
    uptime = time.time() - _start_time
    return {
        "status": "healthy",
        "service": "ai-startup",
        "version": "2.0.0",
        "database_connected": _db_initialized,
        "mode": "full" if _db_initialized else "limited",
        "uptime_seconds": round(uptime, 2)
    }

@app.get("/ready")
@app.get("/ready/")
async def readiness_check():
    """Readiness probe"""
    return {"ready": True, "database": _db_initialized}

@app.get("/live")
@app.get("/live/")
async def liveness_check():
    """Liveness probe"""
    return {"alive": True}

# ============================================
# API HEALTH ENDPOINTS
# ============================================
@app.get("/api/health")
@app.get("/api/health/")
async def api_health_check():
    """API Health check"""
    return {
        "status": "healthy",
        "service": "ai-startup-api",
        "version": "2.0.0"
    }

# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
async def root():
    """Root endpoint - Serve frontend if available, else API info"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend_dist")
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "AI Startup API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health/"
    }

@app.get("/api/")
async def api_root():
    """API Root"""
    return {
        "message": "AI Startup API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/api/health/",
            "docs": "/docs"
        }
    }

# ============================================
# LAZY IMPORT ROUTERS (only if DB available)
# ============================================
def include_routers():
    """Include API routers with error handling"""
    try:
        from app.routers import agents, skills, training

        app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
        app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
        app.include_router(training.router, prefix="/api/training", tags=["training"])

        logger.info("✅ API routers loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Could not load all routers: {e}")

# Try to include routers
include_routers()

# ============================================
# STATIC FILES - Frontend (MUST be after API routes)
# ============================================
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend_dist")

# Only mount static files if they exist
if os.path.exists(frontend_path):
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    logger.info("✅ Frontend dist found at %s", frontend_path)
else:
    logger.warning("⚠️ Frontend dist not found at %s", frontend_path)

# ============================================
# CATCH-ALL FOR SPA ROUTES
# Must be AFTER all API routes and health endpoints
# Must NOT match /health, /api, /docs, /openapi
# ============================================
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Serve frontend for all non-API routes (SPA support)"""
    # Skip API and system routes
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi") or full_path.startswith("health") or full_path.startswith("ready") or full_path.startswith("live"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    # Try to serve index.html for SPA routes
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend_dist")
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)

    return JSONResponse({"detail": "Frontend not built"}, status_code=404)

logger.info("✅ AI Startup application created successfully")
