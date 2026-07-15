"""Database connection and initialization."""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.agent import Agent
from app.models.skill import Skill
from app.models.memory import TrainingDataset, MemoryEntry, FeedbackEntry
from app.models.task import Task
from app.routers.settings_api import AIProviderDocument

_client = None


async def get_database():
    """Get database connection."""
    global _client

    if _client is None:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        _client = AsyncIOMotorClient(mongodb_uri)

    database_name = os.getenv("DATABASE_NAME", "ai_startup")
    return _client[database_name]


async def init_db():
    """Initialize database with Beanie ODM."""
    global _client

    try:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        _client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)

        await _client.admin.command('ping')
        print("✅ MongoDB connected successfully")

        database_name = os.getenv("DATABASE_NAME", "ai_startup")
        db = _client[database_name]

        await init_beanie(
            database=db,
            document_models=[
                Agent,
                Skill,
                TrainingDataset,
                MemoryEntry,
                FeedbackEntry,
                Task,
                AIProviderDocument,
            ]
        )
        print("✅ Beanie ODM initialized")

    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
        print("⚠️ Running in LIMITED MODE - using in-memory storage")
        raise
