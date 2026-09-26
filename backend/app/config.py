"""
PrivacyLens – Application Configuration
All settings are loaded from environment variables (see .env.example).
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    # ── Database ────────────────────────────────────────────────────────────
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/privacylens"

    # ── JWT ─────────────────────────────────────────────────────────────────
    JWT_SECRET: str = "change-this-to-a-long-random-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── File uploads ─────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = ["txt", "pdf", "docx", "png", "jpg", "jpeg"]

    # ── Reports ──────────────────────────────────────────────────────────────
    REPORTS_DIR: str = "reports"

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # ── NLP ──────────────────────────────────────────────────────────────────
    SPACY_MODEL: str = "en_core_web_sm"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Create required directories on startup
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
