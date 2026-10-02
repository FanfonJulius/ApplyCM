import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/applycm")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_jwt_key_for_local_development_12345")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    STORAGE_URL: Optional[str] = os.getenv("STORAGE_URL", None)
    STORAGE_KEY: Optional[str] = os.getenv("STORAGE_KEY", None)

    # Application emails. "brevo" sends through Brevo's HTTPS API (Render's free
    # tier blocks SMTP ports); "console" only logs, for local development.
    EMAIL_BACKEND: str = os.getenv("EMAIL_BACKEND", "brevo")
    BREVO_API_KEY: Optional[str] = os.getenv("BREVO_API_KEY", None)
    EMAIL_FROM_ADDRESS: Optional[str] = os.getenv("EMAIL_FROM_ADDRESS", None)
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "ApplyCM")
    # When set, every outgoing email goes to this address instead of the real
    # recipient (named in the subject). Use it while testing with real schools.
    EMAIL_REDIRECT_TO: Optional[str] = os.getenv("EMAIL_REDIRECT_TO", None)

    model_config = {
        "env_file": [str(BASE_DIR / ".env"), ".env"],
        "extra": "ignore"
    }

settings = Settings()
