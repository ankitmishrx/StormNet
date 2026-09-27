"""Application configuration settings for STORMNET API."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """STORMNET Configuration Settings loaded from environment variables."""

    # Project Information
    PROJECT_NAME: str = "STORMNET Convective Nowcasting API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server Binding
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Database Configuration (PostgreSQL + PostGIS)
    DATABASE_URL: str = "postgresql+psycopg2://stormnet_user:stormnet_secret_password@localhost:5432/stormnet_db"
    POSTGRES_ECHO: bool = False

    # Cache Configuration (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Operational Mode: LIVE | REPLAY | SIMULATION
    OPERATIONAL_MODE: str = "SIMULATION"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
