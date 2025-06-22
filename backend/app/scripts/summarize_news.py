import requests
import sys
import os
import json
import re
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from datetime import datetime

# Add the backend directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from app.services.gemini_service import gemini_service
from app.scripts.scrape_news import scrape_news

# Configure logging
logger = logging.getLogger(__name__)


def scrape_article_content(url: str) -> Optional[Dict]:
    """
    Scrape article content from a given URL.

    Args:
        url (str): The URL of the article to scrape

    Returns:
        Dict: Dictionary containing article content and metadata, or None if failed
    """
    try:
        logger.info(f"Scraping article content from: {url}")

        # Make request to the URL
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract article title
        title = ""
        title_selectors = [
            "h1",
            "h1.article-title",
            "h1.title",
            ".article-title",
            ".title",
            "[property='og:title']",
            "title",
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text()
                if isinstance(title_text, str) and title_text:
                    title = title_text.strip()
                elif title_elem.get("content"):
                    content = title_elem.get("content")
                    if isinstance(content, str):
                        title = content.strip()
                if title:
                    break

        # Extract visible paragraphs
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text().strip()
            if text and len(text) > 20:  # Filter out short paragraphs
                paragraphs.append(text)

        # Combine paragraphs into article content
        article_content = "\n\n".join(paragraphs)

        if not article_content:
            logger.warning(f"No article content found for URL: {url}")
            return None

        # Extract source domain for source name
        from urllib.parse import urlparse

        parsed_url = urlparse(url)
        source_name = parsed_url.netloc.replace("www.", "")

        logger.info(f"Successfully scraped article: {title[:50]}...")
        logger.info(f"Content length: {len(article_content)} characters")

        return {
            "title": title,
            "content": article_content,
            "url": url,
            "source": source_name,
            "scraped_at": datetime.utcnow().isoformat(),
        }

    except requests.RequestException as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error scraping article content from {url}: {e}")
        return None


async def summarize_article_to_overview(
    url: str, ticker: str, article_data: Optional[Dict] = None
) -> Optional[Dict]:
    """
    Scrape and summarize an article into an overview entry format.

    Args:
        url (str): The URL of the article to scrape and summarize
        ticker (str): The stock ticker symbol (e.g., 'AAPL', 'TSLA')
        article_data (Dict, optional): Pre-scraped article data

    Returns:
        Dict: Overview entry in the proper schema format, or None if failed
    """
    try:
        logger.info(f"Starting article summarization for {ticker} from URL: {url}")

        # Scrape article content if not provided
        if article_data is None:
            article_data = scrape_article_content(url)
            if article_data is None:
                logger.error(f"Failed to scrape article content from {url}")
                return None

        # Format article for AI summarization
        article_string = f"""
Title: {article_data['title']}
Source: {article_data['source']}
URL: {article_data['url']}
Content: {article_data['content'][:2000]}  # Limit content length for AI processing
"""

        logger.info(f"Sending article to AI for summarization")
        response = await gemini_service.summarize_text(prompt=article_string)

        # Check if response is an error
        if response.startswith("Error:"):
            logger.error(f"AI summarization failed: {response}")
            return None

        # Clean the AI response
        cleaned_response = clean_ai_response(response)
        if not cleaned_response:
            logger.error(f"Failed to parse AI response for article: {url}")
            return None

        # Create overview record according to schema
        overview_record = {
            "post_id": "",  # Generate unique ID from URL hash
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "ticker": ticker.upper(),
            "title": article_data["title"],
            "sentiment": {
                "summary": cleaned_response.get("summary", "No summary available"),
                "view": cleaned_response.get("view", "neutral"),
                "tone": cleaned_response.get("tone", "neutral"),
            },
            "source_link": url,
            "type": "google",  # Using "google" as the type for news articles
            "sentiment_score": _convert_view_to_score(
                cleaned_response.get("view", "neutral")
            ),
        }

        logger.info(
            f"Successfully created overview record for article: {article_data['title'][:50]}..."
        )
        return overview_record

    except Exception as e:
        logger.error(f"Error in article summarization: {e}")
        return None


def clean_ai_response(response: str) -> Optional[Dict]:
    """Clean and parse AI response to extract JSON"""
    try:
        # Try to find JSON in the response
        match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
        if not match:
            match = re.search(r"(\{.*?\})", response, re.DOTALL)

        if match:
            parsed = json.loads(match.group(1))
            return parsed
        else:
            logger.warning(f"No JSON found in AI response: {response[:100]}...")
            return None

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from AI response: {e}")
        return None


def _convert_view_to_score(view: str) -> float:
    """Convert sentiment view to numeric score"""
    view_lower = view.lower()
    if view_lower == "positive":
        return 0.8
    elif view_lower == "negative":
        return -0.8
    else:
        return 0.0


async def generate_news_overviews(
    ticker: str, keywords: Optional[List[str]] = None, page_size: int = 5
) -> List[Dict]:
    """
    Scrapes news for a ticker, summarizes each article, and returns a list of overview records.

    Args:
        ticker (str): The stock ticker symbol.
        keywords (Optional[List[str]], optional): Keywords to search for. Defaults to None.
        page_size (int, optional): Number of articles to process. Defaults to 5.

    Returns:
        List[Dict]: A list of overview record dictionaries.
    """
    logger.info(
        f"Generating news overviews for ticker: {ticker} with keywords: {keywords}"
    )

    # 1. Scrape news to get article links
    try:
        articles = scrape_news(ticker, keywords, page_size=page_size)
    except Exception as e:
        logger.error(f"Failed to scrape news for {ticker}: {e}")
        return []

    if not articles:
        logger.info(f"No news articles found for {ticker}.")
        return []

    # 2. Summarize each article and create overview records
    overview_records = []
    logger.info(f"Found {len(articles)} articles. Starting summarization...")

    for i, article in enumerate(articles, 1):
        url = article.get("url")
        if not url:
            logger.warning(f"Skipping article with no URL: {article.get('title')}")
            continue

        logger.info(f"Processing article {i}/{len(articles)}: {url}")
        # Pass pre-scraped article data to avoid fetching the URL content again
        overview_record = await summarize_article_to_overview(
            url=url, ticker=ticker, article_data=article
        )

        if overview_record:
            overview_records.append(overview_record)
        else:
            logger.warning(f"Failed to generate overview for article: {url}")

    logger.info(
        f"Finished generating news overviews. Created {len(overview_records)} records."
    )
    return overview_records


# Example usage
if __name__ == "__main__":
    import asyncio

    # Configure basic logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    async def main():
        # Example: Generate overview records for a ticker
        ticker = "AAPL"
        keywords = None

        logger.info(f"Starting news overview generation for ticker: {ticker}")
        overview_records = await generate_news_overviews(ticker, keywords, page_size=3)

        if overview_records:
            print("\n--- Generated Overview Records ---")
            print(json.dumps(overview_records, indent=4))
        else:
            print("Failed to generate any overview records.")

    asyncio.run(main())
