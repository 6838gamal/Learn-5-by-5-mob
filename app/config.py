from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    APP_NAME: str = "Learn 5 by 5"
    DEBUG: bool = True

    # Session secret — read from SESSION_SECRET env/secret, fallback for local dev only
    SECRET_KEY: str = os.environ.get("SESSION_SECRET", "change-me-in-production")
    SESSION_COOKIE_NAME: str = "l5b5_session"

    # Backend API base URL (same one the Flutter app uses)
    API_BASE_URL: str = "https://learn-5-by-5-api-backend.onrender.com/api/v1"

    # Google OAuth Web Client ID — set GOOGLE_WEB_CLIENT_ID env var
    GOOGLE_WEB_CLIENT_ID: str = ""


def get_settings() -> Settings:
    return Settings()
