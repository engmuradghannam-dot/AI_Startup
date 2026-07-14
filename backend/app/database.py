"""
Database module - Lazy initialization for Railway
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import get_settings
from app.models.agent import Agent
from app.models.skill import Skill
from app.models.task import Task
from app.models.memory import Memory

logger = logging.getLogger(__name__)

_client = None
_db = None

async def get_client():
    """Get or create MongoDB client"""
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000
        )
    return _client

async def get_database():
    """Get database instance"""
    global _db
    if _db is None:
        settings = get_settings()
        client = await get_client()
        _db = client[settings.MONGODB_DB_NAME]
    return _db

async def init_db():
    """Initialize database with Beanie"""
    try:
        client = await get_client()
        # Test connection
        await client.admin.command('ping')

        settings = get_settings()
        db = client[settings.MONGODB_DB_NAME]

        # Initialize Beanie with document models
        await init_beanie(
            database=db,
            document_models=[
                Agent,
                Skill,
                Task,
                Memory,
            ]
        )
        logger.info("✅ Database initialized with Beanie")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Database initialization failed: {e}")
        return False

async def close_db():
    """Close database connection"""
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("Database connection closed")
