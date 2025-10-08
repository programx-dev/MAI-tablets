from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/auth.db"
    # DATABASE_ECHO: bool = False
    DATABASE_ECHO: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
