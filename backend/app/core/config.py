"""
CloudScope Core Configuration
Enforces strict environment variable validation and sensible defaults for enterprise multi-cloud management.
"""

from typing import List, Optional
import os
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "CloudScope Multi-Cloud Governance"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False)
    
    # Security & JWT
    SECRET_KEY: str = Field(
        default="cloudscope-insecure-dev-secret-key-32-bytes-long!!",
        description="Master encryption and JWT secret key"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./cloudscope.db",
        description="Database connection URL (PostgreSQL in production, SQLite in local dev)"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    
    # Redis / Task Queue
    REDIS_URL: Optional[str] = Field(default="redis://localhost:6379/0")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Rate Limiting & Timeouts
    DEFAULT_HTTP_TIMEOUT_SECONDS: float = 15.0
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_SECONDS: int = 30
    
    # Demo Mode
    DEMO_MODE_ENABLED: bool = True
    
    # Freshness Thresholds (Hours)
    PRICING_STALE_HOURS: int = 24
    BILLING_STALE_HOURS: int = 24
    METRICS_STALE_HOURS: int = 2
    INVENTORY_STALE_HOURS: int = 6

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if not v:
            return "sqlite:///./cloudscope.db"
        # Support postgres:// -> postgresql:// compatibility if needed
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
