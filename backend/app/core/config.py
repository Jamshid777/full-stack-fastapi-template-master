from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/admin_panel_cc")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    refresh_token_expire_minutes: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080"))
    cors_origins: List[str] = (
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,https://your-frontend-domain.com",
        ).split(",")
    )
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()