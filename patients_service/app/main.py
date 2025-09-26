from fastapi import FastAPI
from app.core.config import settings
from app.core.db import engine, Base
from app.api import patients

app = FastAPI(title=settings.PROJECT_NAME)

# ---------------- Роуты ----------------
app.include_router(patients.router, prefix="/patients", tags=["patients"])

# ---------------- Автокреация таблиц (для dev) ----------------
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # Создаём все таблицы
        await conn.run_sync(Base.metadata.create_all)
