from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="Sentilytics API",
    version="1.0.0",
    description="A basic API for Sentilytics with AI capabilities",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Include routers
from .api.routes import ai

app.include_router(ai.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "Welcome to Sentilytics API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "ai_endpoints": "/ai",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Global health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sentilytics API",
        "version": "1.0.0",
    }


# Example endpoint
@app.get("/api/example")
async def example_endpoint():
    """Example endpoint for testing"""
    return {
        "message": "This is an example endpoint",
        "data": {"items": ["item1", "item2", "item3"], "count": 3},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
