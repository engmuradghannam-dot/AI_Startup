"""AI Startup - Main Application Entry Point."""
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import logging

# Load environment variables from .env file (for local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded .env file")
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# LIFESPAN MANAGEMENT
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("AI Startup Server Starting...")

    # Initialize local LLM service
    try:
        from app.services.local_llm_service import get_local_llm_service
        local_llm = await get_local_llm_service()
        if local_llm.is_available:
            logger.info(f"Local LLM ready: {local_llm.provider}")
            logger.info(f"Available models: {local_llm.available_models}")
        else:
            logger.warning("No local LLM provider available. Install Ollama or LocalAI.")
    except Exception as e:
        logger.warning(f"Local LLM initialization failed: {e}")

    # Initialize multi-agent orchestrator
    try:
        from app.services.multi_agent_orchestrator import get_multi_agent_orchestrator
        orchestrator = await get_multi_agent_orchestrator()
        agents = orchestrator.list_agents()
        logger.info(f"Multi-Agent Orchestrator ready with {len(agents)} agents")
        for agent in agents:
            logger.info(f"  - {agent['name']}: {agent['specialty']}")
    except Exception as e:
        logger.warning(f"Multi-agent initialization failed: {e}")

    yield
    logger.info("AI Startup Server Shutting down...")

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="AI Startup API",
    description="Multi-Agent AI System with Local LLM (Ollama/LocalAI) + Groq Fallback",
    version="3.0.0",
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
        "version": "3.0.0",
        "mode": "production",
        "timestamp": "2026-07-15",
        "features": ["local_llm", "multi_agent", "groq_fallback", "fable5_skills"],
    }

@app.get("/api/health/")
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "features": ["local_llm", "multi_agent", "groq_fallback", "fable5_skills"],
    }

# ============================================
# ROOT ENDPOINT
# ============================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Startup API",
        "version": "3.0.0",
        "description": "Multi-Agent AI System with Local LLM + Groq Fallback",
        "docs": "/docs",
        "health": "/health",
        "features": {
            "local_llm": "Ollama/LocalAI integration - FREE, no API keys",
            "multi_agent": "4 specialized agents with skill integration",
            "groq_fallback": "Cloud fallback when local is unavailable",
            "fable5_skills": "10 advanced skills for agent intelligence",
        },
    }

# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )

# ============================================
# ROUTER IMPORTS & REGISTRATION
# ============================================

# Import all routers
try:
    from app.routers import agents, skills, health, training, voice, ai_chat, local_llm

    # Include all routers
    app.include_router(agents.router, prefix="/api")
    app.include_router(skills.router, prefix="/api")
    app.include_router(health.router, prefix="/api")
    app.include_router(training.router, prefix="/api")
    app.include_router(voice.router, prefix="/api")
    app.include_router(ai_chat.router, prefix="/api")
    app.include_router(local_llm.router, prefix="/api")

    logger.info("All API routers registered successfully")

except Exception as e:
    logger.error(f"Failed to register routers: {e}")
    # Create minimal fallback router
    from fastapi import APIRouter
    fallback_router = APIRouter()

    @fallback_router.get("/fallback/")
    async def fallback():
        return {"status": "fallback_mode", "error": str(e)}

    app.include_router(fallback_router, prefix="/api")

# ============================================
# STATIC FILES (Frontend)
# ============================================

# Serve frontend static files
try:
    frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend_dist")
    if os.path.exists(frontend_dist):
        app.mount("/static", StaticFiles(directory=frontend_dist), name="static")
        logger.info(f"Serving static files from {frontend_dist}")
    else:
        logger.warning(f"Frontend dist not found at {frontend_dist}")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Catch-all for SPA routing
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve frontend SPA for all non-API routes."""
    # Don't intercept API routes
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    # Try to serve index.html
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend_dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return {"message": "AI Startup API - Frontend not built yet"}

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
