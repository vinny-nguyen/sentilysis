import asyncio
import json
import logging
from typing import List, Dict, Any

from ..scripts.summarize_news import generate_news_overviews
from ..scripts.summarize_reddit import get_summaries_for_ticker

logger = logging.getLogger(__name__)

top20Stock = [
    "TSLA",
    "NVDA",
    "CRCL",
    "AAPL",
    "AMZN",
    "MSFT",
    "META",
    "PLTR",
    "AVGO",
    "AMD",
    "COIN",
    "GOOG",
    "NFLX",
    "V",
    "CRWD",
    "UNH",
    "MSTR",
    "LLY",
    "MA",
    "ORCL",
]


class GenerationService:
    def __init__(self):
        self._overview_service = None

    @property
    def overview_service(self):
        """Lazy initialization of OverviewService"""
        if self._overview_service is None:
            from .overview_service import OverviewService

            self._overview_service = OverviewService()
        return self._overview_service

    async def generate_and_store_overviews(self):
        """
        Iterates through the top 20 stock tickers, generates overview records from news and Reddit,
        and writes them to the database, avoiding duplicates.
        """
        logger.info("Starting generation and storage of overviews for top 20 stocks.")

        for ticker in top20Stock:
            logger.info(f"Processing ticker: {ticker}")

            # Generate news overviews
            try:
                news_overviews = await generate_news_overviews(
                    ticker=ticker, page_size=5
                )
                logger.info(
                    f"Generated {len(news_overviews)} news overviews for {ticker}."
                )
            except Exception as e:
                logger.error(f"Error generating news overviews for {ticker}: {e}")
                news_overviews = []

            # Generate Reddit overviews
            try:
                reddit_overviews_json = await get_summaries_for_ticker(ticker=ticker)
                reddit_overviews = json.loads(reddit_overviews_json)
                logger.info(
                    f"Generated {len(reddit_overviews)} Reddit overviews for {ticker}."
                )
            except Exception as e:
                logger.error(f"Error generating Reddit overviews for {ticker}: {e}")
                reddit_overviews = []

            all_overviews = news_overviews + reddit_overviews

            if not all_overviews:
                logger.warning(f"No overviews generated for {ticker}. Skipping.")
                continue

            logger.info(f"Storing {len(all_overviews)} total overviews for {ticker}.")
            created_count = 0
            skipped_count = 0

            for overview in all_overviews:
                try:
                    # Check for duplicates
                    existing = await self.overview_service.get_by_post_id(
                        overview["post_id"]
                    )
                    if existing:
                        skipped_count += 1
                        continue

                    # Create record if it doesn't exist
                    await self.overview_service.create_one(overview)
                    created_count += 1
                except Exception as e:
                    logger.error(
                        f"Error storing overview for {ticker} (post_id: {overview.get('post_id')}): {e}"
                    )

            logger.info(
                f"Finished processing for {ticker}. Created: {created_count}, Skipped (duplicates): {skipped_count}"
            )

        logger.info("Completed generation and storage of overviews for all tickers.")


generation_service = GenerationService()


# Example usage (can be run as a script)
async def main():
    logging.basicConfig(level=logging.INFO)
    await generation_service.generate_and_store_overviews()


if __name__ == "__main__":
    asyncio.run(main())
