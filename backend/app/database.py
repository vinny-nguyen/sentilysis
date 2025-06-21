from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from .config import settings

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    database = None


async def connect_to_mongo():
    """Create database connection."""
    try:
        Database.client = AsyncIOMotorClient(settings.mongodb_uri)
        Database.database = Database.client[settings.mongodb_database]

        # Test the connection
        await Database.client.admin.command("ping")
        logger.info("Successfully connected to MongoDB Atlas")

    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise e


async def close_mongo_connection():
    """Close database connection."""
    if Database.client:
        Database.client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get database instance."""
    return Database.database


def get_collection(collection_name: str):
    """Get collection instance."""
    return Database.database[collection_name]
