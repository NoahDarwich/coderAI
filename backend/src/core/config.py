"""
Configuration management using Pydantic Settings.

This module loads environment variables and provides type-safe configuration
for the application.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or .env file.
    """
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/data_extraction",
        description="Async PostgreSQL connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for job queue and pub/sub"
    )
    REDIS_MAX_CONNECTIONS: int = Field(default=20, description="Max Redis connection pool size")

    # ARQ Worker Configuration
    ARQ_MAX_JOBS: int = Field(default=10, description="Max concurrent ARQ jobs")
    ARQ_JOB_TIMEOUT: int = Field(default=3600, description="ARQ job timeout in seconds")
    ARQ_QUEUE_NAME: str = Field(default="arq:queue", description="ARQ queue name")

    # JWT Configuration
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration in days"
    )
    
    # LLM Provider Configuration
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key for LLM calls"
    )
    OPENAI_MODEL: str = Field(default="gpt-4", description="OpenAI model to use")
    OPENAI_TEMPERATURE: float = Field(default=0.2, description="Temperature for LLM calls")
    OPENAI_MAX_TOKENS: int = Field(default=1000, description="Max tokens for LLM responses")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host address")
    API_PORT: int = Field(default=8000, description="API port")
    DEBUG: bool = Field(default=True, description="Debug mode")
    API_PREFIX: str = Field(default="/api/v1", description="API route prefix")
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        description="Comma-separated list of allowed CORS origins"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # Security (for future use)
    SECRET_KEY: str = Field(
        default="your-secret-key-here-replace-in-production",
        description="Secret key for JWT encoding"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )
    
    # Application Settings
    PROJECT_NAME: str = Field(default="Data Extraction Backend", description="Project name")
    VERSION: str = Field(default="1.0.0", description="API version")
    ENVIRONMENT: str = Field(default="development", description="Environment (development, production)")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or text)")
    
    # Processing Configuration
    MAX_DOCUMENT_SIZE_MB: int = Field(
        default=10,
        description="Maximum document size in MB"
    )
    MAX_CONCURRENT_JOBS: int = Field(
        default=10,
        description="Maximum concurrent processing jobs"
    )
    JOB_TIMEOUT_SECONDS: int = Field(
        default=3600,
        description="Job timeout in seconds (1 hour)"
    )
    
    # LLM Retry Configuration
    LLM_RETRY_MAX_ATTEMPTS: int = Field(default=3, description="Max retry attempts for LLM calls")
    LLM_RETRY_BASE_DELAY: float = Field(
        default=1.0,
        description="Base delay in seconds for exponential backoff"
    )
    LLM_RETRY_MAX_DELAY: float = Field(
        default=10.0,
        description="Maximum delay in seconds for retries"
    )
    
    # LLM Rate Limiting
    LLM_RATE_LIMIT_CALLS: int = Field(
        default=10,
        description="Max LLM calls per period"
    )
    LLM_RATE_LIMIT_PERIOD: int = Field(
        default=60,
        description="Rate limit period in seconds"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
