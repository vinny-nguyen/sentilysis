"""
Example usage of the Overview Service
This demonstrates how to use the overview service for sentiment analysis records
"""

import sys
import os

from app.services.overview_service import overview_service, SourceType, SentimentView
import asyncio


async def example_overview_operations():
    """Example of using the overview service"""

    print("=== Overview Service Examples ===")

    # Example 1: Create a single record
    print("\n1. Creating a single overview record...")

    record_data = {
        "post_id": "reddit_123456",
        "date": "2025-06-20",
        "ticker": "AAPL",
        "title": "Apple's new iPhone announcement",
        "sentiment": {
            "summary": "Overall positive sentiment about Apple's new product launch",
            "view": "positive",
            "tone": "enthusiastic",
        },
        "source_link": "https://reddit.com/r/stocks/comments/123456",
        "type": "reddit",
        "sentiment_score": 0.85,
    }

    try:
        created_record = await overview_service.create_one(record_data)
        print(f"✅ Created record with ID: {created_record['_id']}")
    except Exception as e:
        print(f"❌ Error creating record: {e}")

    # Example 2: Create another record
    print("\n2. Creating another record...")

    record_data_2 = {
        "post_id": "google_789012",
        "date": "2025-06-20",
        "ticker": "TSLA",
        "title": "Tesla stock analysis",
        "sentiment": {
            "summary": "Mixed reactions to Tesla's quarterly earnings",
            "view": "neutral",
            "tone": "analytical",
        },
        "source_link": "https://news.google.com/article/789012",
        "type": "google",
        "sentiment_score": 0.02,
    }

    try:
        created_record_2 = await overview_service.create_one(record_data_2)
        print(f"✅ Created record with ID: {created_record_2['_id']}")
    except Exception as e:
        print(f"❌ Error creating record: {e}")

    # Example 3: Get many records
    print("\n3. Getting all records...")

    try:
        all_records = await overview_service.get_many(limit=10)
        print(f"✅ Retrieved {len(all_records)} records")
        for record in all_records:
            print(f"  - {record['ticker']}: {record['title'][:50]}...")
    except Exception as e:
        print(f"❌ Error getting records: {e}")

    # Example 4: Get records by ticker
    print("\n4. Getting records for AAPL...")

    try:
        aapl_records = await overview_service.get_by_ticker("AAPL")
        print(f"✅ Found {len(aapl_records)} records for AAPL")
    except Exception as e:
        print(f"❌ Error getting AAPL records: {e}")

    # Example 5: Get records by sentiment
    print("\n5. Getting positive sentiment records...")

    try:
        positive_records = await overview_service.get_by_sentiment(
            SentimentView.POSITIVE
        )
        print(f"✅ Found {len(positive_records)} positive records")
    except Exception as e:
        print(f"❌ Error getting positive records: {e}")

    # Example 6: Get records by source type
    print("\n6. Getting Reddit records...")

    try:
        reddit_records = await overview_service.get_by_source_type(SourceType.REDDIT)
        print(f"✅ Found {len(reddit_records)} Reddit records")
    except Exception as e:
        print(f"❌ Error getting Reddit records: {e}")

    # Example 7: Get records by date range
    print("\n7. Getting records from 2025-06-20...")

    try:
        date_records = await overview_service.get_by_date_range(
            "2025-06-20", "2025-06-20"
        )
        print(f"✅ Found {len(date_records)} records for 2025-06-20")
    except Exception as e:
        print(f"❌ Error getting date range records: {e}")

    # Example 8: Count records by ticker
    print("\n8. Counting records by ticker...")

    try:
        aapl_count = await overview_service.count_by_ticker("AAPL")
        tsla_count = await overview_service.count_by_ticker("TSLA")
        print(f"✅ AAPL: {aapl_count} records, TSLA: {tsla_count} records")
    except Exception as e:
        print(f"❌ Error counting records: {e}")

    # Example 9: Delete records by ticker
    print("\n9. Deleting TSLA records...")

    try:
        deleted_count = await overview_service.delete_by_ticker("TSLA")
        print(f"✅ Deleted {deleted_count} TSLA records")
    except Exception as e:
        print(f"❌ Error deleting TSLA records: {e}")

    # Example 10: Delete records by date range
    print("\n10. Deleting records from 2025-06-20...")

    try:
        deleted_count = await overview_service.delete_by_date_range(
            "2025-06-20", "2025-06-20"
        )
        print(f"✅ Deleted {deleted_count} records from 2025-06-20")
    except Exception as e:
        print(f"❌ Error deleting date range records: {e}")


# Example of how to use the service in your application
async def create_sentiment_record(
    post_id: str,
    ticker: str,
    title: str,
    sentiment_summary: str,
    sentiment_view: str,
    tone: str,
    source_link: str,
    source_type: str,
    sentiment_score: float,
    date_str: str | None = None,
):
    """Helper function to create a sentiment record"""

    from datetime import datetime

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    record_data = {
        "post_id": post_id,
        "date": date_str,
        "ticker": ticker.upper(),
        "title": title,
        "sentiment": {
            "summary": sentiment_summary,
            "view": sentiment_view.lower(),
            "tone": tone,
        },
        "source_link": source_link,
        "type": source_type.lower(),
        "sentiment_score": sentiment_score,
    }

    return await overview_service.create_one(record_data)


# Example usage in your application
async def example_usage_in_app():
    """Example of how you might use this in your sentiment analysis pipeline"""

    # After analyzing a Reddit post
    await create_sentiment_record(
        post_id="reddit_post_123",
        ticker="AAPL",
        title="Apple's new product is amazing!",
        sentiment_summary="Very positive reaction to Apple's announcement",
        sentiment_view="positive",
        tone="excited",
        source_link="https://reddit.com/r/apple/comments/123",
        source_type="reddit",
        sentiment_score=0.92,
    )

    # After analyzing a Google News article
    await create_sentiment_record(
        post_id="google_news_456",
        ticker="TSLA",
        title="Tesla faces production challenges",
        sentiment_summary="Concerns about Tesla's production capacity",
        sentiment_view="negative",
        tone="concerned",
        source_link="https://news.google.com/article/456",
        source_type="google",
        sentiment_score=-0.45,
    )


# Run examples
if __name__ == "__main__":
    asyncio.run(example_overview_operations())
