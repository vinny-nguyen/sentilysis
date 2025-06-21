import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..database import get_collection
from ..models.sentiment import (
    ScrapedPost,
    SentimentAnalysis,
    SentimentSummary,
    SentimentType,
    AnalysisRequest,
    AnalysisResponse,
)
from .gemini_service import gemini_service

logger = logging.getLogger(__name__)


class SentimentService:
    def __init__(self):
        self.posts_collection = get_collection("posts")
        self.sentiment_collection = get_collection("sentiment_analysis")
        self.summary_collection = get_collection("sentiment_summaries")

    async def analyze_ticker(self, request: AnalysisRequest) -> AnalysisResponse:
        """Main method to analyze sentiment for a ticker"""
        start_time = datetime.utcnow()

        try:
            # For now, we'll use mock data since scraping is not implemented yet
            mock_posts = await self._get_mock_posts(request.ticker, request.max_posts)

            # Analyze sentiment for each post
            sentiment_results = []
            for post in mock_posts:
                sentiment = await gemini_service.analyze_sentiment(
                    post["content"], request.ticker
                )
                sentiment.post_id = post["id"]
                sentiment_results.append(sentiment)

                # Store sentiment analysis
                await self._store_sentiment_analysis(sentiment)

            # Generate overall summary
            summary_data = await gemini_service.generate_summary(
                mock_posts, request.ticker
            )

            # Create sentiment summary
            sentiment_summary = await self._create_sentiment_summary(
                request.ticker, sentiment_results, summary_data
            )

            # Store summary
            await self._store_sentiment_summary(sentiment_summary)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            return AnalysisResponse(
                ticker=request.ticker,
                sentiment_summary=sentiment_summary,
                recent_posts=[ScrapedPost(**post) for post in mock_posts],
                processing_time=processing_time,
                status="completed",
                message="Analysis completed successfully",
            )

        except Exception as e:
            logger.error(f"Error analyzing ticker {request.ticker}: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            return AnalysisResponse(
                ticker=request.ticker,
                sentiment_summary=await self._create_error_summary(request.ticker),
                recent_posts=[],
                processing_time=processing_time,
                status="error",
                message=f"Error during analysis: {str(e)}",
            )

    async def get_latest_analysis(self, ticker: str) -> Optional[SentimentSummary]:
        """Get the latest sentiment analysis for a ticker"""
        try:
            result = await self.summary_collection.find_one(
                {"ticker": ticker.upper()}, sort=[("last_updated", -1)]
            )

            if result:
                return SentimentSummary(**result)
            return None

        except Exception as e:
            logger.error(f"Error getting latest analysis for {ticker}: {e}")
            return None

    async def get_sentiment_history(
        self, ticker: str, days: int = 7
    ) -> List[SentimentSummary]:
        """Get sentiment analysis history for a ticker"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            cursor = self.summary_collection.find(
                {"ticker": ticker.upper(), "last_updated": {"$gte": cutoff_date}}
            ).sort("last_updated", -1)

            results = await cursor.to_list(length=None)
            return [SentimentSummary(**result) for result in results]

        except Exception as e:
            logger.error(f"Error getting sentiment history for {ticker}: {e}")
            return []

    async def _get_mock_posts(
        self, ticker: str, max_posts: int
    ) -> List[Dict[str, Any]]:
        """Get mock posts for testing (will be replaced with real scraping)"""
        mock_posts = [
            {
                "id": f"mock_1_{ticker}",
                "source": "reddit",
                "content": f"Just bought more {ticker} shares! The company's latest earnings report looks promising and I'm bullish on their future prospects.",
                "author": "investor123",
                "url": f"https://reddit.com/r/stocks/comments/mock1",
                "timestamp": datetime.utcnow() - timedelta(hours=2),
                "ticker": ticker.upper(),
                "subreddit": "stocks",
                "likes": 45,
                "comments": 12,
            },
            {
                "id": f"mock_2_{ticker}",
                "source": "twitter",
                "content": f"#{ticker} is showing strong technical indicators. Support level holding well. #stocks #trading",
                "author": "trader456",
                "url": f"https://twitter.com/trader456/status/mock2",
                "timestamp": datetime.utcnow() - timedelta(hours=1),
                "ticker": ticker.upper(),
                "subreddit": None,
                "likes": 23,
                "comments": 5,
            },
            {
                "id": f"mock_3_{ticker}",
                "source": "news",
                "content": f"Analysts are concerned about {ticker}'s exposure to supply chain disruptions. The company may face challenges in Q4 due to geopolitical tensions affecting global trade.",
                "author": "Financial Times",
                "url": f"https://ft.com/article/mock3",
                "timestamp": datetime.utcnow() - timedelta(hours=3),
                "ticker": ticker.upper(),
                "subreddit": None,
                "likes": None,
                "comments": None,
            },
        ]

        return mock_posts[:max_posts]

    async def _create_sentiment_summary(
        self,
        ticker: str,
        sentiment_results: List[SentimentAnalysis],
        summary_data: Dict[str, Any],
    ) -> SentimentSummary:
        """Create sentiment summary from analysis results"""
        positive_count = sum(
            1 for s in sentiment_results if s.sentiment == SentimentType.POSITIVE
        )
        neutral_count = sum(
            1 for s in sentiment_results if s.sentiment == SentimentType.NEUTRAL
        )
        negative_count = sum(
            1 for s in sentiment_results if s.sentiment == SentimentType.NEGATIVE
        )

        total_posts = len(sentiment_results)
        average_confidence = (
            sum(s.confidence for s in sentiment_results) / total_posts
            if total_posts > 0
            else 0
        )

        # Determine overall sentiment
        if positive_count > negative_count:
            overall_sentiment = SentimentType.POSITIVE
        elif negative_count > positive_count:
            overall_sentiment = SentimentType.NEGATIVE
        else:
            overall_sentiment = SentimentType.NEUTRAL

        return SentimentSummary(
            ticker=ticker.upper(),
            total_posts=total_posts,
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            overall_sentiment=overall_sentiment,
            average_confidence=average_confidence,
            top_headlines=summary_data.get("top_headlines", []),
            geopolitical_summary=summary_data.get("geopolitical_summary", ""),
            macro_summary=summary_data.get("macro_summary", ""),
        )

    async def _create_error_summary(self, ticker: str) -> SentimentSummary:
        """Create error summary when analysis fails"""
        return SentimentSummary(
            ticker=ticker.upper(),
            total_posts=0,
            positive_count=0,
            neutral_count=0,
            negative_count=0,
            overall_sentiment=SentimentType.NEUTRAL,
            average_confidence=0.0,
            top_headlines=[],
            geopolitical_summary="Unable to analyze due to an error.",
            macro_summary="Unable to analyze due to an error.",
        )

    async def _store_sentiment_analysis(self, sentiment: SentimentAnalysis):
        """Store sentiment analysis in database"""
        try:
            await self.sentiment_collection.insert_one(sentiment.dict())
        except Exception as e:
            logger.error(f"Error storing sentiment analysis: {e}")

    async def _store_sentiment_summary(self, summary: SentimentSummary):
        """Store sentiment summary in database"""
        try:
            # Use upsert to update existing or insert new
            await self.summary_collection.update_one(
                {"ticker": summary.ticker}, {"$set": summary.dict()}, upsert=True
            )
        except Exception as e:
            logger.error(f"Error storing sentiment summary: {e}")


# Create global instance
sentiment_service = SentimentService()
