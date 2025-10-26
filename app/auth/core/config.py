from pydantic_settings import BaseSettings
from pydantic import BaseModel
import os

class DbSettings(BaseModel):
    url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/maisafe")
    echo: bool = True


class Settings(BaseSettings):
    db: DbSettings = DbSettings()


settings = Settings()
