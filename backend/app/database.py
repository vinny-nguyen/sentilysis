from motor.core import AgnosticClient, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Database:
    client: AgnosticClient | None = None
    database: AgnosticDatabase | None = None


async def connect_to_mongo():
    """Create database connection."""
    try:
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv("MONGODB_URI")
        database_name = os.getenv("MONGODB_DATABASE", "sentilytics")

        if not mongodb_uri:
            logger.error("MONGODB_URI not found in environment variables")
            raise ValueError("MONGODB_URI is required")

        # Create connection
        Database.client = AsyncIOMotorClient(mongodb_uri)
        Database.database = Database.client[database_name]

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
    if Database.database is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return Database.database


def get_collection(collection_name: str):
    """Get collection instance."""
    if Database.database is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return Database.database[collection_name]
