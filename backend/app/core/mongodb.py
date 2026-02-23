"""
MongoDB connection (motor async driver).
Stores block content and templates.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core import settings


class MongoDB:
    """MongoDB connection manager."""
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    def connect(cls):
        cls.client = AsyncIOMotorClient(settings.mongo_url)
        cls.db = cls.client[settings.MONGO_DB]

    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        return cls.db


async def get_mongo() -> AsyncIOMotorDatabase:
    """Dependency for getting MongoDB database instance."""
    return MongoDB.get_db()
