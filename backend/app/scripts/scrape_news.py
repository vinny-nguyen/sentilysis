import requests
import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# NewsAPI configuration
NEWS_API_KEY = os.getenv("NEWSAPI_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"


def scrape_news(
    stock_ticker: str,
    keywords: Optional[List[str]] = None,
    page_size: int = 10,
    language: str = "en",
) -> List[Dict]:
    """
    Scrape news articles for a given stock ticker and optional keywords.

    Args:
        stock_ticker (str): The stock ticker symbol (e.g., 'AAPL', 'TSLA')
        keywords (List[str], optional): Additional keywords to search for
        page_size (int): Number of articles to return (default: 10)
        language (str): Language code for articles (default: 'en')

    Returns:
        List[Dict]: List of article dictionaries with title, url, description, etc.

    Raises:
        ValueError: If API key is not configured
        requests.RequestException: If API request fails
    """

    # Validate API key
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY not found in environment variables")

    # Build search query
    query_parts = [stock_ticker]
    if keywords:
        query_parts.extend(keywords)

    search_query = " AND ".join(query_parts)

    logger.info(f"Searching news for ticker: {stock_ticker}")
    if keywords:
        logger.info(f"Additional keywords: {', '.join(keywords)}")

    # Prepare API parameters
    params = {
        "q": search_query,
        "apiKey": NEWS_API_KEY,
        "language": language,
        "pageSize": page_size,
        "sortBy": "publishedAt",  # Sort by publication date
    }

    try:
        logger.info(f"Making request to NewsAPI for query: {search_query}")
        response = requests.get(NEWS_API_URL, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            total_results = data.get("totalResults", 0)

            logger.info(
                f"Successfully retrieved {len(articles)} articles (total available: {total_results})"
            )

            # Process and clean articles
            processed_articles = []
            for i, article in enumerate(articles, 1):
                logger.info(
                    f"Processing article {i}/{len(articles)}: {article.get('title', 'No title')[:50]}..."
                )

                processed_article = {
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "published_at": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "author": article.get("author", ""),
                    "stock_ticker": stock_ticker,
                    "keywords": keywords or [],
                }

                processed_articles.append(processed_article)

            logger.info(
                f"News scraping completed. Retrieved {len(processed_articles)} articles"
            )
            return processed_articles

        else:
            error_msg = (
                f"NewsAPI request failed with status code: {response.status_code}"
            )
            logger.error(error_msg)
            if response.status_code == 401:
                error_msg += " - Invalid API key"
            elif response.status_code == 429:
                error_msg += " - Rate limit exceeded"
            elif response.status_code == 400:
                error_msg += " - Bad request"

            raise requests.RequestException(error_msg)

    except requests.Timeout:
        error_msg = "NewsAPI request timed out"
        logger.error(error_msg)
        raise requests.RequestException(error_msg)
    except requests.RequestException as e:
        logger.error(f"NewsAPI request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during news scraping: {e}")
        raise


def format_news_data(news_data: List[Dict]) -> str:
    """Format news data as JSON string"""
    import json

    return json.dumps(news_data, indent=4)


# Example usage
if __name__ == "__main__":
    # Configure basic logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Example: Search for NVIDIA articles with war-related keywords
        ticker = "NVDA"
        keywords = None

        logger.info(f"Starting news scraping for {ticker}")
        articles = scrape_news(ticker, keywords, page_size=10)

        print(f"\nFound {len(articles)} articles:")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   URL: {article['url']}")
            print(f"   Published: {article['published_at']}")
            print()

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"Error: {e}")
