import os
import datetime
from typing import List, Dict
from dotenv import load_dotenv
import praw
from textblob import TextBlob

# Load environment variables from .env file
load_dotenv()

# PRAW Reddit API setup (read-only)
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# List of subreddits to search
SUBREDDITS = ['stocks', 'wallstreetbets', 'investing']

def scrape_reddit(stock_ticker: str) -> List[Dict]:
    """
    Scrape Reddit for a given stock ticker and return the top 5 most recent and popular posts with content.
    Each result contains a 'summary' field with the post's title and content.
    Only includes posts with actual text content (not just images).
    """
    posts_seen = set()
    all_posts = []
    query = f'"{stock_ticker}"'
    
    for subreddit_name in SUBREDDITS:
        subreddit = reddit.subreddit(subreddit_name)
        # Search for recent posts mentioning the stock ticker
        for post in subreddit.search(query, sort='new', limit=10):
            if post.id in posts_seen:
                continue
            posts_seen.add(post.id)
            
            # Extract post metadata
            title = post.title
            selftext = post.selftext
            author = str(post.author) if post.author else 'deleted'
            date = datetime.datetime.fromtimestamp(post.created_utc).isoformat()
            subreddit_name = post.subreddit.display_name
            score = post.score
            permalink = f'https://reddit.com{post.permalink}'

            # Only include posts with actual text content (not just images)
            if not selftext.strip():
                continue

            # Build summary with just title and content
            summary = f"Title: {title}\nContent: {selftext}"

            # Sentiment analysis using TextBlob
            text = f'{title} {selftext}'
            sentiment = TextBlob(text).sentiment.polarity  # Range: -1 (neg) to 1 (pos)

            # Prepare result dictionary
            result = {
                "title": title,
                'summary': summary,
                'stock_ticker': stock_ticker,
                'author': author,
                'date': date,  # ISO 8601 string of post creation
                'subreddit': subreddit_name,
                'score': score,
                'permalink': permalink,
                'sentiment': sentiment
            }
            all_posts.append(result)
    
    # Sort all posts by score (most upvoted first), then by date (most recent)
    all_posts.sort(key=lambda x: (x['score'], x['date']), reverse=True)
    # Return only the top 5
    return all_posts[:5]

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
