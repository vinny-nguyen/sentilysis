import logging

logger = logging.getLogger(__name__)


class TestService:
    def __init__(self):
        # Don't initialize collection during __init__
        self._test_collection = None

    @property
    def test_collection(self):
        """Lazy initialization of test collection"""
        if self._test_collection is None:
            from ..database import get_collection

            self._test_collection = get_collection("test")
        return self._test_collection

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
