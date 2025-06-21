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

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## AI Service Features

The Gemini service provides:
- **Text Generation**: Generate text based on prompts
- **Text Analysis**: Analyze text with different types (general, summary, sentiment)
- **Chat Interface**: Interactive chat with AI
- **Insights Generation**: Generate insights about topics (general, financial, technical)

## Example Usage

### Generate Text
```bash
curl -X POST "http://localhost:8000/ai/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a short story about a robot", "max_tokens": 500}'
```

### Analyze Text
```bash
curl -X POST "http://localhost:8000/ai/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!", "analysis_type": "sentiment"}'
```

### Chat with AI
```bash
curl -X POST "http://localhost:8000/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?", "context": "educational"}'
```

## Development

The application runs on `http://localhost:8000` with auto-reload enabled for development.

## Features

- FastAPI framework
- Google Gemini AI integration
- CORS middleware enabled
- Request timing middleware
- Global exception handling
- Interactive API documentation
- Environment-based configuration

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY` 