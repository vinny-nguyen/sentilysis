from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SourceType(str, Enum):
    """Enum for source types"""

    REDDIT = "reddit"
    GOOGLE = "google"


class SentimentView(str, Enum):
    """Enum for sentiment views"""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class OverviewService:
    """Service for overview collection operations"""

    def __init__(self):
        # Don't initialize CRUD service during __init__
        self._crud_service = None

    @property
    def crud_service(self):
        """Lazy initialization of CRUD service"""
        if self._crud_service is None:
            from .crud_service import create_crud_service

            self._crud_service = create_crud_service("overview")
        return self._crud_service

    async def create_one(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single overview record"""
        try:
            # Validate required fields
            required_fields = [
                "post_id",
                "date",
                "ticker",
                "title",
                "sentiment",
                "source_link",
                "type",
            ]
            for field in required_fields:
                if field not in record_data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate sentiment structure
            sentiment = record_data.get("sentiment", {})
            if not isinstance(sentiment, dict):
                raise ValueError("sentiment must be a dictionary")

            required_sentiment_fields = ["summary", "view", "tone"]
            for field in required_sentiment_fields:
                if field not in sentiment:
                    raise ValueError(f"Missing required sentiment field: {field}")

            # Validate enums
            if record_data["type"] not in [SourceType.REDDIT, SourceType.GOOGLE]:
                raise ValueError(
                    f"Invalid type. Must be one of: {[e.value for e in SourceType]}"
                )

            if sentiment["view"] not in [
                SentimentView.POSITIVE,
                SentimentView.NEUTRAL,
                SentimentView.NEGATIVE,
            ]:
                raise ValueError(
                    f"Invalid sentiment view. Must be one of: {[e.value for e in SentimentView]}"
                )

            # Convert date string to datetime if needed
            if isinstance(record_data["date"], str):
                try:
                    record_data["date"] = str(
                        datetime.strptime(record_data["date"], "%Y-%m-%d").date()
                    )
                except ValueError:
                    raise ValueError("Invalid date format. Use YYYY-MM-DD")

            # Ensure sentiment_score is a float
            if "sentiment_score" in record_data:
                try:
                    record_data["sentiment_score"] = float(
                        record_data["sentiment_score"]
                    )
                except (ValueError, TypeError):
                    raise ValueError("sentiment_score must be a number")

            # Create the record
            record = await self.crud_service.create_one(record_data)
            logger.info(
                f"Created overview record: {record['post_id']} for ticker {record['ticker']}"
            )
            return record

        except Exception as e:
            logger.error(f"Error creating overview record: {e}")
            raise e

    async def get_many(
        self,
        filter_dict: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[List[tuple]] = None,
    ) -> List[Dict[str, Any]]:
        """Get multiple overview records with filtering, pagination, and sorting"""
        try:
            # Default sorting by date (newest first)
            if sort_by is None:
                sort_by = [("date", -1), ("created_at", -1)]

            records = await self.crud_service.find_many(
                filter_dict=filter_dict, skip=skip, limit=limit, sort_by=sort_by
            )

            logger.info(f"Retrieved {len(records)} overview records")
            return records

        except Exception as e:
            logger.error(f"Error getting overview records: {e}")
            raise e

    async def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        """Delete multiple overview records based on filter"""
        try:
            deleted_count = await self.crud_service.delete_many(filter_dict)
            logger.info(f"Deleted {deleted_count} overview records")
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting overview records: {e}")
            raise e

    # Additional convenience methods
    async def get_by_ticker(
        self, ticker: str, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get records for a specific ticker"""
        try:
            return await self.get_many(
                filter_dict={"ticker": ticker.upper()}, skip=skip, limit=limit
            )
        except Exception as e:
            logger.error(f"Error getting records for ticker {ticker}: {e}")
            raise e

    async def get_by_date_range(
        self,
        start_date: Union[str, date],
        end_date: Union[str, date],
        ticker: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get records within a date range"""
        try:
            # Convert string dates to date objects
            if isinstance(start_date, str):
                start_date = str(datetime.strptime(start_date, "%Y-%m-%d").date())
            if isinstance(end_date, str):
                end_date = str(datetime.strptime(end_date, "%Y-%m-%d").date())

            # Build filter
            filter_dict: Dict[str, Any] = {
                "date": {"$gte": start_date, "$lte": end_date}
            }

            if ticker:
                filter_dict["ticker"] = ticker.upper()

            return await self.get_many(filter_dict=filter_dict, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error getting records by date range: {e}")
            raise e

    async def get_by_sentiment(
        self,
        sentiment_view: SentimentView,
        ticker: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get records by sentiment view"""
        try:
            filter_dict = {"sentiment.view": sentiment_view.value}

            if ticker:
                filter_dict["ticker"] = ticker.upper()

            return await self.get_many(filter_dict=filter_dict, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error getting records by sentiment: {e}")
            raise e

    async def get_by_source_type(
        self,
        source_type: SourceType,
        ticker: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get records by source type"""
        try:
            filter_dict = {"type": source_type.value}

            if ticker:
                filter_dict["ticker"] = ticker.upper()

            return await self.get_many(filter_dict=filter_dict, skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error getting records by source type: {e}")
            raise e

    async def get_by_post_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get a single record by post_id"""
        try:
            return await self.crud_service.find_one({"post_id": post_id})
        except Exception as e:
            logger.error(f"Error getting record by post_id: {e}")
            raise e

    async def count_by_ticker(self, ticker: str) -> int:
        """Count records for a specific ticker"""
        try:
            return await self.crud_service.count_documents({"ticker": ticker.upper()})
        except Exception as e:
            logger.error(f"Error counting records for ticker {ticker}: {e}")
            raise e

    async def delete_by_ticker(self, ticker: str) -> int:
        """Delete all records for a specific ticker"""
        try:
            return await self.delete_many({"ticker": ticker.upper()})
        except Exception as e:
            logger.error(f"Error deleting records for ticker {ticker}: {e}")
            raise e

    async def delete_by_date_range(
        self, start_date: Union[str, date], end_date: Union[str, date]
    ) -> int:
        """Delete records within a date range"""
        try:
            # Convert string dates to date objects
            if isinstance(start_date, str):
                start_date = str(datetime.strptime(start_date, "%Y-%m-%d").date())
            if isinstance(end_date, str):
                end_date = str(datetime.strptime(end_date, "%Y-%m-%d").date())

            filter_dict = {"date": {"$gte": start_date, "$lte": end_date}}

            return await self.delete_many(filter_dict)
        except Exception as e:
            logger.error(f"Error deleting records by date range: {e}")
            raise e


# Create a singleton instance
overview_service = OverviewService()
