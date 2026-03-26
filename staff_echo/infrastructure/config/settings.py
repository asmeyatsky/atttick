"""
Application Settings

Architectural Intent:
- Centralized configuration loaded from environment variables
- STAFF_ECHO_ prefix for all env vars
- Sensible defaults for local development
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "STAFF_ECHO_", "env_file": ".env", "env_file_encoding": "utf-8"}

    bigquery_project: str = ""
    bigquery_dataset: str = "staff_echo"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    redis_url: str = "redis://localhost:6379"
    cache_ttl_seconds: int = 3600
    max_concurrent_requests: int = 10
    cors_origins: list[str] = ["http://localhost:3000"]
    host: str = "0.0.0.0"
    port: int = 8001
