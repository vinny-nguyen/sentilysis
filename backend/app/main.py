from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from .database import close_mongo_connection, connect_to_mongo
from .services.test_service import TestService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info("Starting Sentilytics Backend...")
    try:
        await connect_to_mongo()
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e

    yield

    # Shutdown
    logger.info("Shutting down Sentilytics Backend...")
    await close_mongo_connection()
    logger.info("MongoDB connection closed")


# Get CORS origins from environment
def get_cors_origins():
    if os.getenv("ENVIRONMENT") == "production":
        # Production: specific domains only
        origins = "https://sentilysis.vercel.app/"
    else:
        # Development: allow common dev ports
        origins = "http://localhost:3000/"
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


# Create FastAPI app
app = FastAPI(
    title="Sentilytics API",
    version="1.0.0",
    description="A basic API for Sentilytics with AI capabilities",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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


@app.get("/test-db")
async def test_database():
    """Test database connection"""
    await connect_to_mongo()
    test_service = TestService()
    return await test_service.test_connection()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
