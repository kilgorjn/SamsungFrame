"""Configuration settings for the Samsung Frame Art Controller backend."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Samsung TV Configuration
    tv_ip: str = "192.168.86.25"
    tv_port: int = 8001
    tv_timeout: int = 30

    # Cache Configuration
    cache_ttl: int = 300  # 5 minutes

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
