"""
Centralized application configuration.
Loads values from environment variables / a .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Security
    secret_key: str = "insecure-dev-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Database
    database_url: str = "sqlite:///./debt_relief.db"

    # Gemini AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # CORS
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
