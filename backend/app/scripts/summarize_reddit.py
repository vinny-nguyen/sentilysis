import requests
import json
import sys
import os
import re

# Add the backend directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from app.services.gemini_service import gemini_service
from app.scripts.scrape_reddit import scrape_reddit, format_reddit_data


async def get_summaries_for_ticker(ticker: str) -> str:
    """
    Get AI-generated summaries for Reddit posts about a given stock ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'TSLA')

    Returns:
        str: JSON string containing overview records in the proper schema format
    """
    # Scrape Reddit data for the ticker
    reddit_data = scrape_reddit(ticker)

    results = []

    for post in reddit_data:
        # Format each post as string
        post_string = f"""
Title: {post['title']}
Summary: {post['summary']}
Subreddit: {post['subreddit']}
Date: {post['date']}
Score: {post['score']}
"""
        response = await gemini_service.summarize_text(prompt=post_string)

        # Check if response is an error
        if response.startswith("Error:"):
            results.append({"input_post": post["title"], "ai_response": response})
        else:
            results.append({"input_post": post["title"], "ai_response": response})

    # Clean the AI responses
    cleaned_data = clean_ai_responses(results)

    # Transform to overview schema format
    overview_records = []
    for i, cleaned_item in enumerate(cleaned_data):
        # Extract date from the original post data
        post_date = reddit_data[i]["date"][:10]  # Take just the date part (YYYY-MM-DD)

        # Create overview record according to schema
        overview_record = {
            "post_id": "",
            "date": post_date,
            "ticker": ticker.upper(),
            "title": reddit_data[i]["title"],
            "sentiment": {
                "summary": cleaned_item.get("summary", "No summary available"),
                "view": cleaned_item.get("view", "neutral"),
                "tone": cleaned_item.get("tone", "neutral"),
            },
            "source_link": f"https://reddit.com/r/{reddit_data[i]['link']}",
            "type": "reddit",
            "sentiment_score": _convert_view_to_score(
                cleaned_item.get("view", "neutral")
            ),
        }

        overview_records.append(overview_record)

    # Return as JSON string
    summaries = json.dumps(overview_records, indent=4)
    return summaries


def clean_ai_responses(data):
    cleaned = []
    for item in data:
        raw = item.get("ai_response", "")
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if not match:
            match = re.search(r"(\{.*?\})", raw, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(1))
                cleaned.append(parsed)
            except json.JSONDecodeError:
                continue
    return cleaned


def _convert_view_to_score(view: str) -> float:
    """Convert sentiment view to numeric score"""
    view_lower = view.lower()
    if view_lower == "positive":
        return 0.8
    elif view_lower == "negative":
        return -0.8
    else:
        return 0.0


# Example usage (for backward compatibility)
if __name__ == "__main__":
    import asyncio

    ticker = "AAPL"

    async def main():
        summaries = await get_summaries_for_ticker(ticker)
        print("\n\n--- Individual Summaries ---\n")
        print(summaries)

    asyncio.run(main())
