import os
import datetime
import json
import logging
from typing import List, Dict
from dotenv import load_dotenv
import praw
from textblob import TextBlob

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# PRAW Reddit API setup (read-only)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "stock-sentiment-script")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

# List of subreddits to search
SUBREDDITS = ["stocks", "wallstreetbets", "investing"]

# List of geopolitical/macro keywords to detect
GEO_KEYWORDS = [
    "inflation",
    "war",
    "china",
    "fed",
    "election",
    "tariffs",
    "interest rate",
    "recession",
    "trade",
    "sanction",
    "geopolitics",
    "conflict",
    "opec",
    "oil",
    "currency",
    "debt",
    "default",
    "stimulus",
    "regulation",
    "policy",
    "gdp",
    "unemployment",
    "crisis",
    "bank",
    "central bank",
    "federal reserve",
    "biden",
    "trump",
    "xi",
    "putin",
    "ukraine",
    "taiwan",
    "sanctions",
    "trade war",
    "supply chain",
    "macro",
    "macro-economic",
    "macro economic",
]


def scrape_reddit(stock_ticker: str) -> List[Dict]:
    """
    Scrape Reddit for a given stock ticker and return the top 5 most relevant and recent posts as a list of dictionaries.
    Each result contains a 'summary' field with the post's title, content, and the top (most upvoted, non-stickied) comment.
    The 'date' field is the post's creation date in ISO 8601 format.
    """
    posts_seen = set()
    all_posts = []
    query = f'"{stock_ticker}"'

    logger.info(f"Starting Reddit scraping for ticker: {stock_ticker}")
    logger.info(f"Searching in subreddits: {', '.join(SUBREDDITS)}")

    total_subreddits = len(SUBREDDITS)
    for subreddit_index, subreddit_name in enumerate(SUBREDDITS, 1):
        logger.info(
            f"Progress: {subreddit_index}/{total_subreddits} - Searching r/{subreddit_name}"
        )

        subreddit = reddit.subreddit(subreddit_name)
        posts_found_in_subreddit = 0

        # Search for recent and relevant posts mentioning the stock ticker
        for post_index, post in enumerate(
            subreddit.search(query, sort="relevance", limit=3), 1
        ):
            logger.info(f"Checking post {post_index}/3: {post.title[:50]}...")

            if post.id in posts_seen:
                logger.info(f"Skipping duplicate post")
                continue

            posts_seen.add(post.id)
            posts_found_in_subreddit += 1

            # Extract post metadata
            title = post.title
            selftext = post.selftext
            date = datetime.datetime.fromtimestamp(post.created_utc).isoformat()
            subreddit_name = post.subreddit.display_name
            score = post.score

            # Get the top (most upvoted, non-stickied) comment efficiently
            top_comment = "No top comment found."
            post.comment_sort = "top"
            post.comments.replace_more(limit=0)
            for comment in post.comments:
                if not getattr(comment, "stickied", False) and hasattr(comment, "body"):
                    top_comment = comment.body
                    break

            # Build summary
            summary = f"Title: {title}\nContent: {selftext}\nTop Comment: {top_comment}"

            # Sentiment analysis using TextBlob
            text = f"{title} {selftext} {top_comment}"

            # Detect geopolitical/macro keywords
            found_keywords = [kw for kw in GEO_KEYWORDS if kw.lower() in text.lower()]

            # Prepare result dictionary
            result = {
                "title": title,
                "summary": summary,
                "stock_ticker": stock_ticker,
                "date": date,  # ISO 8601 string of post creation
                "subreddit": subreddit_name,
                "score": score,
                "geopolitics_found": found_keywords,
                "link": f"https://reddit.com/{post.permalink}",
            }
            all_posts.append(result)
            logger.info(f"Added post: {title[:50]}... (Score: {score})")

    # Sort all posts by date (most recent first), then by score (most upvoted)
    all_posts.sort(key=lambda x: (x["date"], x["score"]), reverse=True)

    logger.info(f"Reddit scraping completed")
    logger.info(f"Total posts found: {len(all_posts)}")
    logger.info(f"Posts by subreddit:")
    for subreddit in SUBREDDITS:
        count = len([post for post in all_posts if post["subreddit"] == subreddit])
        logger.info(f"  - r/{subreddit}: {count} posts")

    return all_posts


def format_reddit_data(reddit_data: List[Dict]) -> str:

    return json.dumps(reddit_data, indent=4)


if __name__ == "__main__":
    ticker_to_scrape = "AAPL"
    logger.info(f"Scraping Reddit for {ticker_to_scrape} and formatting as JSON...")
    results = scrape_reddit(ticker_to_scrape)

    # Convert the list of dictionaries to a JSON string
    json_output = json.dumps(results, indent=4)

    # print(json.dumps(results, indent=4))

    logger.info(f"Successfully formatted {len(results)} posts into JSON.")

# Example usage
# stock_ticker = 'NVDA'
# print(f'Scraping Reddit for {stock_ticker}...')
# results = scrape_reddit(stock_ticker)
# print(f'Found {len(results)} posts. Example:')
# if results:
#     print("FOUND RESULT!!!")
#     for r in results:
#         print(r["date"], r["permalink"])
#         print(r["summary"])
#         print('\n')
