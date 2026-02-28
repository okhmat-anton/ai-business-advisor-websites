"""
Application configuration via environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # App
    APP_NAME: str = "AKM Site Builder"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production"

    # JWT (external auth from parent project)
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"

    # External auth service URL
    EXTERNAL_AUTH_URL: str = "https://app.akm-advisor.com"

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "sitebuilder"
    POSTGRES_PASSWORD: str = "sitebuilder_password"
    POSTGRES_DB: str = "sitebuilder_db"

    # MongoDB
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "sitebuilder"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # CORS
    CORS_ORIGINS: str = '["http://localhost:10669","http://localhost:3000"]'

    # Agent API key for logs access (optional)
    AGENT_API_KEY: str = ""

    # Agent project ID for validating agent keys via parent API (from AGENTS.md)
    AGENT_PROJECT_ID: str = "698427043be84d505d347aad"

    # Server IP for DNS verification (A record check)
    SERVER_IP: str = ""

    # File upload
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "/app/uploads"

    # S3 / S3-compatible storage (overridable via admin settings stored in Redis)
    S3_ENABLED: bool = False
    S3_BUCKET: str = ""
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_ENDPOINT_URL: str = ""   # leave empty for real AWS
    S3_PUBLIC_URL: str = ""     # base URL for public access; auto-built if empty
    S3_FOLDER: str = "uploads"  # key prefix inside bucket

    # Publish
    PUBLISH_DIR: str = "/app/published"

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def postgres_sync_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def mongo_url(self) -> str:
        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"


settings = Settings()
