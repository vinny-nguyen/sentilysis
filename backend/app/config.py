from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv
from pydantic import field_validator

load_dotenv()


class Settings(BaseSettings):
    # Application Configuration
    app_name: str = "Sentilytics"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"

    # MongoDB Configuration
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "sentilytics")

    # Gemini API Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # CORS Configuration
    allowed_origins: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:8080",
    )

    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
