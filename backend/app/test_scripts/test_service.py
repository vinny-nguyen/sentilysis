# backend/test_scripts/test_service.py
import sys
import os

from app.database import get_collection
import logging

logger = logging.getLogger(__name__)


class TestService:
    def __init__(self):
        self.test_collection = get_collection("test")

    async def test_connection(self):
        """Test database connection by inserting a document"""
        try:
            result = await self.test_collection.insert_one(
                {"message": "Test connection", "timestamp": "2024-01-01"}
            )
            logger.info(f"Test document inserted with ID: {result.inserted_id}")
            return {"status": "success", "message": "Database connection working"}
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            return {"status": "error", "message": str(e)}
