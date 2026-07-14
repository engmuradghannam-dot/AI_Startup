import os
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Support both MONGODB_URL and MONGODB_URI
MONGODB_URL = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017"
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "ai_startup")

# Global client instance
_mongo_client: Optional[AsyncIOMotorClient] = None
_mongo_db = None

async def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create MongoDB client"""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
        )
    return _mongo_client

async def get_database():
    """Get database instance"""
    global _mongo_db
    if _mongo_db is None:
        client = await get_mongo_client()
        _mongo_db = client[MONGODB_DB_NAME]
    return _mongo_db

async def test_connection() -> bool:
    """Test MongoDB connection"""
    try:
        client = await get_mongo_client()
        await client.admin.command('ping')
        print(f"✅ MongoDB connected successfully to {MONGODB_URL.split('@')[-1].split('/')[0]}")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"⚠️ Database connection failed: {e}")
        return False

async def init_database():
    # Alias for init_database (used by main.py)
init_db = init_database
    """Initialize database connection"""
    try:
        connected = await test_connection()
        if connected:
            db = await get_database()
            # Create indexes if needed
            await db.agents.create_index("agent_id", unique=True)
            await db.memories.create_index([("agent_id", 1), ("created_at", -1)])
            await db.datasets.create_index("name", unique=True)
            print("✅ MongoDB initialized successfully")
            return True
        else:
            print("⚠️ Running in LIMITED MODE - some features unavailable")
            return False
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("⚠️ Running in LIMITED MODE - some features unavailable")
        return False

async def close_database():
    """Close database connection"""
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        print("✅ MongoDB connection closed")

# Collection helpers
async def get_collection(collection_name: str):
    """Get a collection from the database"""
    db = await get_database()
    return db[collection_name]
