from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class SourceType(str, Enum):
    REDDIT = "reddit"
    TWITTER = "twitter"
    NEWS = "news"

class ScrapedPost(BaseModel):
    """Model for scraped social media posts and news articles"""
    id: str = Field(..., description="Unique identifier for the post")
    source: SourceType = Field(..., description="Source platform")
    content: str = Field(..., description="Post content/text")
    author: Optional[str] = Field(None, description="Author username")
    url: Optional[str] = Field(None, description="Original post URL")
    timestamp: datetime = Field(..., description="Post timestamp")
    ticker: str = Field(..., description="Stock ticker mentioned")
    subreddit: Optional[str] = Field(None, description="Subreddit name (for Reddit posts)")
    likes: Optional[int] = Field(None, description="Number of likes/upvotes")
    comments: Optional[int] = Field(None, description="Number of comments")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SentimentAnalysis(BaseModel):
    """Model for sentiment analysis results"""
    post_id: str = Field(..., description="Reference to scraped post")
    ticker: str = Field(..., description="Stock ticker analyzed")
    sentiment: SentimentType = Field(..., description="Sentiment classification")
    confidence: float = Field(..., description="Confidence score (0-1)")
    summary: str = Field(..., description="AI-generated summary")
    key_points: List[str] = Field(default_factory=list, description="Key points extracted")
    geopolitical_events: List[str] = Field(default_factory=list, description="Geopolitical events mentioned")
    macroeconomic_factors: List[str] = Field(default_factory=list, description="Macroeconomic factors mentioned")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SentimentSummary(BaseModel):
    """Model for aggregated sentiment summary"""
    ticker: str = Field(..., description="Stock ticker")
    total_posts: int = Field(..., description="Total number of posts analyzed")
    positive_count: int = Field(..., description="Number of positive posts")
    neutral_count: int = Field(..., description="Number of neutral posts")
    negative_count: int = Field(..., description="Number of negative posts")
    overall_sentiment: SentimentType = Field(..., description="Overall sentiment")
    average_confidence: float = Field(..., description="Average confidence score")
    top_headlines: List[str] = Field(default_factory=list, description="Top headlines")
    geopolitical_summary: str = Field(..., description="Geopolitical events summary")
    macro_summary: str = Field(..., description="Macroeconomic factors summary")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    """Model for chatbot messages"""
    message: str = Field(..., description="User message")
    ticker: Optional[str] = Field(None, description="Stock ticker context")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context data")

class ChatResponse(BaseModel):
    """Model for chatbot responses"""
    response: str = Field(..., description="AI-generated response")
    sources: List[str] = Field(default_factory=list, description="Sources used for response")
    confidence: float = Field(..., description="Confidence in the response")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnalysisRequest(BaseModel):
    """Model for analysis requests"""
    ticker: str = Field(..., description="Stock ticker to analyze")
    include_reddit: bool = Field(default=True, description="Include Reddit data")
    include_twitter: bool = Field(default=True, description="Include Twitter data")
    include_news: bool = Field(default=True, description="Include news data")
    max_posts: int = Field(default=100, description="Maximum number of posts to analyze")

class AnalysisResponse(BaseModel):
    """Model for analysis responses"""
    ticker: str = Field(..., description="Stock ticker analyzed")
    sentiment_summary: SentimentSummary = Field(..., description="Sentiment analysis summary")
    recent_posts: List[ScrapedPost] = Field(default_factory=list, description="Recent posts analyzed")
    processing_time: float = Field(..., description="Time taken to process (seconds)")
    status: str = Field(..., description="Processing status")
    message: Optional[str] = Field(None, description="Additional message") 