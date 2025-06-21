# Sentilytics Backend

Real-time stock sentiment analysis backend using FastAPI, MongoDB Atlas, and Google Gemini API.

## 🚀 Features

- **Real-time Sentiment Analysis**: Analyze stock sentiment using AI
- **Social Media Integration**: Scrape and analyze Reddit, Twitter, and news data
- **MongoDB Storage**: Store sentiment data and analysis results
- **RESTful API**: Clean FastAPI endpoints with automatic documentation
- **AI Chatbot**: Interactive chatbot for stock insights
- **CORS Support**: Ready for frontend integration

## 📋 Prerequisites

- Python 3.8+
- MongoDB Atlas account
- Google Gemini API key

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your credentials:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sentilytics
   MONGODB_DATABASE=sentilytics
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## 🚀 Running the Application

### Development Mode
```bash
python run.py
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Sentiment Analysis

#### POST `/sentiment/analyze`
Analyze sentiment for a stock ticker.

**Request Body:**
```json
{
  "ticker": "AAPL",
  "include_reddit": true,
  "include_twitter": true,
  "include_news": true,
  "max_posts": 100
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "sentiment_summary": {
    "ticker": "AAPL",
    "total_posts": 15,
    "positive_count": 8,
    "neutral_count": 4,
    "negative_count": 3,
    "overall_sentiment": "positive",
    "average_confidence": 0.85,
    "top_headlines": ["Apple reports strong Q4 earnings", "..."],
    "geopolitical_summary": "Supply chain concerns in China...",
    "macro_summary": "Interest rate environment affecting tech stocks..."
  },
  "recent_posts": [...],
  "processing_time": 2.5,
  "status": "completed",
  "message": "Analysis completed successfully"
}
```

#### GET `/sentiment/latest/{ticker}`
Get the latest sentiment analysis for a ticker.

#### GET `/sentiment/history/{ticker}?days=7`
Get sentiment history for a ticker (1-30 days).

#### POST `/sentiment/chat`
Chat with AI assistant about stock sentiment.

**Request Body:**
```json
{
  "message": "Why is AAPL trending negatively?",
  "ticker": "AAPL"
}
```

### Health Checks

#### GET `/health`
Global health check.

#### GET `/sentiment/health`
Sentiment service health check.

## 🗄️ Database Schema

### Collections

#### `posts`
Stores scraped social media posts and news articles.

#### `sentiment_analysis`
Stores individual sentiment analysis results.

#### `sentiment_summaries`
Stores aggregated sentiment summaries.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB Atlas connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `sentilytics` |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DEBUG` | Debug mode | `True` |
| `ENVIRONMENT` | Environment name | `development` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["http://localhost:3000"]` |

## 🧪 Testing

### Manual Testing with curl

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Analyze Sentiment**
   ```bash
   curl -X POST http://localhost:8000/sentiment/analyze \
     -H "Content-Type: application/json" \
     -d '{"ticker": "AAPL", "max_posts": 10}'
   ```

3. **Chat with AI**
   ```bash
   curl -X POST http://localhost:8000/sentiment/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the sentiment for AAPL?", "ticker": "AAPL"}'
   ```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # MongoDB connection
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── sentiment.py # Sentiment API routes
│   ├── models/
│   │   ├── __init__.py
│   │   └── sentiment.py     # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── gemini_service.py    # Gemini API integration
│       └── sentiment_service.py # Sentiment analysis logic
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
├── run.py                  # Run script
└── README.md               # This file
```

## 🔮 Future Enhancements

- [ ] Real web scraping implementation (Reddit, Twitter, News)
- [ ] Real-time data streaming
- [ ] User authentication and watchlists
- [ ] Historical sentiment tracking
- [ ] Sector-based sentiment analysis
- [ ] Investment recommendations
- [ ] Email alerts and notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the logs for error details
- Ensure all environment variables are set correctly 