# Sentilytics Backend

A basic FastAPI application for Sentilytics.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python run.py
```

Or alternatively:
```bash
python -m app.main
```

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `GET /api/example` - Example endpoint for testing
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Development

The application runs on `http://localhost:8000` with auto-reload enabled for development.

## Features

- FastAPI framework
- CORS middleware enabled
- Request timing middleware
- Global exception handling
- Interactive API documentation 