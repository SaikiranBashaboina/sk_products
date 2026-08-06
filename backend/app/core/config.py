"""Application configuration management using Pydantic Settings."""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
import json
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables with production defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "SKProducts"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Security - MUST be set in production via .env
    SECRET_KEY: str = Field(
        default="",
        description="JWT signing key. Generate with: python -c 'import secrets; print(secrets.token_hex(32))'"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 5
    RATE_LIMIT_GENERAL_PER_MINUTE: int = 60

    # Account Lockout
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15

    # Database
    DATABASE_URL: str = "sqlite:///./skproducts.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Admin Defaults
    ADMIN_NAME: str = "Admin"
    ADMIN_EMAIL: str = "admin@skcompany.com"
    ADMIN_PASSWORD: str = "admin@12345"

    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,gif"

    # CORS - comma-separated origins for production
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure SECRET_KEY is set. In production, this MUST be configured."""
        if not v:
            if cls.model_config.get("env_file") and cls.model_config["env_file"] == ".env":
                # During development, generate a default if .env doesn't have it
                return secrets.token_hex(32)
            raise ValueError(
                "SECRET_KEY must be set in production. "
                "Generate with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        if len(v.encode("utf-8")) < 32:
            raise ValueError("SECRET_KEY must be at least 32 bytes. Generate a secure random key.")
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions from comma-separated string."""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"


settings = Settings()