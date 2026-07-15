"""AI Startup - Main Application Entry Point."""
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# LIFESPAN MANAGEMENT
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 AI Startup Server Starting...")
    yield
    logger.info("🛑 AI Startup Server Shutting down...")

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="AI Startup API",
    description="Multi-Agent AI System with Groq, OpenAI, and more",
    version="2.1.0",
    lifespan=lifespan,
)

# ============================================
# CORS MIDDLEWARE
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# HEALTH CHECK (Always available)
# ============================================

@app.get("/health/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.1.0",
        "mode": "production",
        "timestamp": "2026-07-15",
    }

@app.get("/api/health/")
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.1.0",
        "mode": "production",
        "timestamp": "2026-07-15",
    }

# ============================================
# AI CHAT ROUTER (CRITICAL - load first!)
# ============================================

try:
    from app.routers import ai_chat
    app.include_router(ai_chat.router, tags=["ai-chat"])
    logger.info("✅ ai_chat router loaded")
except Exception as e:
    logger.error(f"❌ Failed to load ai_chat router: {e}")

# ============================================
# OTHER ROUTERS
# ============================================

try:
    from app.routers import agents
    app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
    logger.info("✅ agents router loaded")
except Exception as e:
    logger.warning(f"⚠️ Could not load agents router: {e}")

try:
    from app.routers import skills
    app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
    logger.info("✅ skills router loaded")
except Exception as e:
    logger.warning(f"⚠️ Could not load skills router: {e}")

try:
    from app.routers import training
    app.include_router(training.router, prefix="/api/training", tags=["training"])
    logger.info("✅ training router loaded")
except Exception as e:
    logger.warning(f"⚠️ Could not load training router: {e}")

try:
    from app.routers import voice
    app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
    logger.info("✅ voice router loaded")
except Exception as e:
    logger.warning(f"⚠️ Could not load voice router: {e}")

try:
    from app.routers import health
    app.include_router(health.router, prefix="/api/health", tags=["health"])
    logger.info("✅ health router loaded")
except Exception as e:
    logger.warning(f"⚠️ Could not load health router: {e}")

# ============================================
# STATIC FILES - Frontend
# ============================================

# Serve frontend static files
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend_dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    logger.info(f"✅ Static files mounted from {frontend_dist}")
else:
    logger.warning(f"⚠️ Frontend dist not found at {frontend_dist}")

# ============================================
# CATCH-ALL ROUTE (MUST be last!)
# ============================================

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Catch-all route to serve frontend."""
    if full_path.startswith("api/") or full_path.startswith("ai-chat/"):
        return JSONResponse(
            status_code=404,
            content={"detail": f"API endpoint /{full_path} not found"}
        )

    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return JSONResponse(
        status_code=200,
        content={
            "status": "AI Startup API Server Running",
            "version": "2.1.0",
            "frontend": "not_built" if not os.path.exists(frontend_dist) else "available",
            "endpoints": [
                "/health/",
                "/ai-chat/chat",
                "/ai-chat/providers",
                "/api/agents/*",
                "/api/skills/*",
                "/api/training/*",
                "/api/voice/*",
            ],
        }
    )
