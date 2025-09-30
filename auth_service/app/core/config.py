from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///app/db/auth.sqlite3"
    db_echo: bool = True
    
settings = Settings()