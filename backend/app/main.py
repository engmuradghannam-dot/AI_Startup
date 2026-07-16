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

    # Initialize database (MongoDB + Beanie ODM)
    db_ready = False
    try:
        from app.database import init_db
        await init_db()
        db_ready = True
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization: {e} - running without persistence")

    # Seed the skill catalog from app/skills/*/SKILL.md
    if db_ready:
        try:
            from app.services.skill_seeder import seed_skills_from_catalog
            seed_result = await seed_skills_from_catalog()
            logger.info(f"Skill catalog seeded: {seed_result}")
        except Exception as e:
            logger.warning(f"Skill catalog seeding: {e}")

    # Initialize Groq service
    try:
        from app.services.groq_service import get_groq_service
        groq = await get_groq_service()
        logger.info("Groq service initialized")
    except Exception as e:
        logger.warning(f"Groq initialization: {e}")

    # Initialize multi-agent orchestrator
    try:
        from app.services.multi_agent_orchestrator import get_multi_agent_orchestrator
        orchestrator = await get_multi_agent_orchestrator()
        agents = orchestrator.list_agents()
        logger.info(f"Multi-Agent Orchestrator ready with {len(agents)} agents")
        for agent in agents:
            logger.info(f"  - {agent['name']}: {agent['specialty']}")
    except Exception as e:
        logger.warning(f"Multi-agent initialization: {e}")

    # Initialize advanced memory system
    try:
        from app.services.advanced_memory import get_memory_system
        memory_system = await get_memory_system()
        logger.info("Advanced Memory System initialized")
    except Exception as e:
        logger.warning(f"Memory system initialization: {e}")

    # Initialize self-learning system
    try:
        from app.services.self_learning import get_learning_system
        learning_system = await get_learning_system()
        logger.info("Self-Learning System initialized")
    except Exception as e:
        logger.warning(f"Learning system initialization: {e}")

    # Initialize notification system
    try:
        from app.services.notification_system import get_notification_system
        notification_system = await get_notification_system()
        logger.info("Notification & Monitoring System initialized")
    except Exception as e:
        logger.warning(f"Notification system initialization: {e}")

    # Initialize integration manager
    try:
        from app.services.integration_manager import get_integration_manager
        integration_manager = await get_integration_manager()
        logger.info("External Integration Manager initialized")
    except Exception as e:
        logger.warning(f"Integration manager initialization: {e}")

    yield
    logger.info("AI Startup Server Shutting down...")

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="AI Startup API",
    description="Multi-Agent AI System with Groq Cloud API + Local LLM Support",
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
# HEALTH CHECK
# ============================================

@app.get("/health/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "mode": "production",
        "timestamp": "2026-07-15",
        "features": ["groq_cloud", "multi_agent", "fable5_skills", "local_llm_ready"],
    }

@app.get("/api/health/")
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "features": ["groq_cloud", "multi_agent", "fable5_skills", "local_llm_ready"],
    }

# ============================================
# ROOT ENDPOINT - Serve Frontend
# ============================================

@app.get("/")
async def root():
    """Serve the frontend application."""
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend_dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    # Fallback to API info if frontend not built
    return {
        "name": "AI Startup API",
        "version": "3.0.0",
        "description": "Multi-Agent AI System with Groq Cloud + Local LLM Support",
        "docs": "/docs",
        "health": "/health",
        "features": {
            "groq_cloud": "Primary AI via Groq API - fast & reliable",
            "multi_agent": "4 specialized agents with skill integration",
            "fable5_skills": "10 advanced skills for agent intelligence",
            "local_llm_ready": "Ollama/LocalAI support for local development",
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
    from app.routers import agents, skills, health, training, voice, ai_chat, local_llm, memory, learning, notifications, integrations, settings_api

    app.include_router(agents.router, prefix="/api")
    app.include_router(skills.router, prefix="/api")
    app.include_router(health.router, prefix="/api")
    app.include_router(training.router, prefix="/api")
    app.include_router(voice.router, prefix="/api")
    app.include_router(ai_chat.router, prefix="/api")
    app.include_router(local_llm.router, prefix="/api")
    app.include_router(memory.router, prefix="/api")
    app.include_router(learning.router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")
    app.include_router(integrations.router, prefix="/api")
    app.include_router(settings_api.router, prefix="/api")

    logger.info("All API routers registered successfully")

except Exception as e:
    logger.error(f"Failed to register routers: {e}")
    from fastapi import APIRouter
    fallback_router = APIRouter()

    @fallback_router.get("/fallback/")
    async def fallback():
        return {"status": "fallback_mode", "error": str(e)}

    app.include_router(fallback_router, prefix="/api")

# ============================================
# STATIC FILES (Frontend)
# ============================================

try:
    frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend_dist")
    if os.path.exists(frontend_dist):
        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
        logger.info(f"Serving static files from {frontend_dist}")
    else:
        logger.warning(f"Frontend dist not found at {frontend_dist}")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Catch-all for SPA routing - serve index.html for all non-API routes
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve frontend SPA for all non-API routes."""
    # Don't intercept API routes
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi") or full_path.startswith("health"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    # Try to serve index.html
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend_dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return {"message": "AI Startup API - Frontend not built yet. Please build the frontend first."}

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
