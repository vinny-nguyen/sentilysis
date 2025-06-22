# Sentilytics Backend

A basic FastAPI application for Sentilytics with AI capabilities powered by Google Gemini.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env.example .env
```
Edit `.env` file and add your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

3. Run the application:
```bash
python run.py
```

Or alternatively:
```bash
python -m app.main
```

## API Endpoints

### Basic Endpoints
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `GET /api/example` - Example endpoint for testing

### AI Endpoints (Gemini)
- `POST /ai/generate` - Generate text using Gemini AI
- `POST /ai/analyze` - Analyze text using Gemini AI
- `POST /ai/chat` - Chat with Gemini AI
- `POST /ai/insights` - Generate insights about a topic
- `GET /ai/status` - Check Gemini service status
- `GET /ai/health` - AI service health check

### Overview Endpoints (Sentiment Analysis Records)
- `POST /overview/search` - Search records by ticker and specific date
- `POST /overview/search/range` - Search records by ticker and date range
- `POST /overview/ticker/{ticker}` - Get all records for a specific ticker
- `GET /overview/status` - Check overview service status
- `GET /overview/health` - Overview service health check

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## AI Service Features

The Gemini service provides:
- **Text Generation**: Generate text based on prompts
- **Text Analysis**: Analyze text with different types (general, summary, sentiment)
- **Chat Interface**: Interactive chat with AI
- **Insights Generation**: Generate insights about topics (general, financial, technical)

## Overview Service (Sentiment Analysis Records)

The Overview service manages sentiment analysis records with the following schema:

```json
{
  "post_id": "string",
  "date": "2025-06-20",
  "ticker": "string",
  "title": "string",
  "sentiment": {
    "summary": "string",
    "view": "positive|neutral|negative",
    "tone": "string"
  },
  "source_link": "string",
  "type": "reddit|google",
  "sentiment_score": 0.0001
}
```

### Basic Operations

```python
from app.services.overview_service import overview_service

# Create a sentiment record
record = await overview_service.create_one({
    "post_id": "reddit_123",
    "date": "2025-06-20",
    "ticker": "AAPL",
    "title": "Apple's new product announcement",
    "sentiment": {
        "summary": "Positive reaction to Apple's announcement",
        "view": "positive",
        "tone": "enthusiastic"
    },
    "source_link": "https://reddit.com/r/stocks/comments/123",
    "type": "reddit",
    "sentiment_score": 0.85
})

# Get multiple records with pagination
records = await overview_service.get_many(limit=10, skip=0)

# Delete records by filter
deleted_count = await overview_service.delete_many({"ticker": "TSLA"})
```

### Advanced Queries

#### Get Records by Ticker
```python
# Get all records for a specific stock
aapl_records = await overview_service.get_by_ticker("AAPL")

# Get records with pagination
aapl_records = await overview_service.get_by_ticker("AAPL", skip=0, limit=50)
```

#### Get Records by Sentiment
```python
from app.services.overview_service import SentimentView

# Get all positive sentiment records
positive_records = await overview_service.get_by_sentiment(SentimentView.POSITIVE)

# Get negative sentiment records for a specific ticker
negative_aapl = await overview_service.get_by_sentiment(
    SentimentView.NEGATIVE, 
    ticker="AAPL"
)
```

#### Get Records by Source Type
```python
from app.services.overview_service import SourceType

# Get all Reddit records
reddit_records = await overview_service.get_by_source_type(SourceType.REDDIT)

# Get Google News records for a specific ticker
google_tsla = await overview_service.get_by_source_type(
    SourceType.GOOGLE, 
    ticker="TSLA"
)
```

#### Get Records by Date Range
```python
# Get records from a specific date range
recent_records = await overview_service.get_by_date_range(
    "2025-06-15", 
    "2025-06-21"
)

# Get records for a specific ticker within date range
aapl_week = await overview_service.get_by_date_range(
    "2025-06-15", 
    "2025-06-21", 
    ticker="AAPL"
)
```

#### Complex Filtering
```python
# Custom filter with multiple conditions
custom_filter = {
    "ticker": "AAPL",
    "sentiment.view": "positive",
    "type": "reddit",
    "sentiment_score": {"$gte": 0.5}
}

filtered_records = await overview_service.get_many(
    filter_dict=custom_filter,
    sort_by=[("date", -1), ("sentiment_score", -1)]
)
```

#### Aggregation and Analytics
```python
# Count records by ticker
aapl_count = await overview_service.count_by_ticker("AAPL")
tsla_count = await overview_service.count_by_ticker("TSLA")

# Get records by post ID
specific_record = await overview_service.get_by_post_id("reddit_123456")
```

#### Bulk Operations
```python
# Delete all records for a ticker
deleted_count = await overview_service.delete_by_ticker("TSLA")

# Delete records within a date range
deleted_count = await overview_service.delete_by_date_range(
    "2025-06-01", 
    "2025-06-30"
)
```
## Development

The application runs on `http://localhost:8000` with auto-reload enabled for development.

## Features

- FastAPI framework
- Google Gemini AI integration
- MongoDB Atlas integration with CRUD services
- CORS middleware enabled
- Request timing middleware
- Global exception handling
- Interactive API documentation
- Environment-based configuration

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY` 