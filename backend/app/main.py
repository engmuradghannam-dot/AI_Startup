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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
_db_initialized = False

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
# HEALTH ENDPOINT - Must work without DB
# ============================================
@app.get("/health/")
@app.get("/health")
async def health_check():
    """Health check endpoint - Railway requires this"""
    return {
        "status": "healthy",
        "service": "ai-startup",
        "version": "2.0.0",
        "database_connected": _db_initialized,
        "mode": "full" if _db_initialized else "limited"
    }

@app.get("/api/health/")
@app.get("/api/health")
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
    """Root endpoint"""
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
        from app.routers import agents, skills, training, health as health_router

        app.include_router(health_router.router, prefix="/api/health", tags=["health"])
        app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
        app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
        app.include_router(training.router, prefix="/api/training", tags=["training"])

        logger.info("✅ API routers loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ Could not load all routers: {e}")

# Try to include routers
include_routers()

# ============================================
# STATIC FILES - Frontend
# ============================================
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend_dist")
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        """Serve frontend for all non-API routes"""
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        index_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"detail": "Frontend not built"}, status_code=404)
else:
    logger.warning("⚠️ Frontend dist not found at %s", frontend_path)

logger.info("✅ AI Startup application created successfully")
# Root endpoint for Railway domain
@app.get("/")
async def root():
    return {
        "message": "AI Startup API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health/"
    }
