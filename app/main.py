# app/main.py

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from app.db.session import db_helper
from app.core.scheduler import scheduler
from app.auth.tasks.cleanup_tasks import cleanup_old_data  # ✅ новая задача

from app.auth.api.auth import router as auth_router
from app.auth.api.friend import router as friend_router
from app.medicines.api.medication import router as medication_router
from app.medicines.api.intake import router as intake_router
from app.medicines.api.sync import router as sync_router  # ✅ Импортируем новый роутер


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ❌ УДАЛИТЬ этот блок полностью:
    # async with db_helper.engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    # ✅ Запускаем ежедневную очистку (первый запуск через 1 мин после старта)
    scheduler.add_job(
        cleanup_old_data,
        "interval",
        days=1,
        id="daily_cleanup",
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    scheduler.start()
    print("✅ Планировщик запущен: daily_cleanup (ежедневно)")

    yield

    scheduler.shutdown()
    print("🛑 Планировщик остановлен.")


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(friend_router)
app.include_router(medication_router)
app.include_router(intake_router)
app.include_router(sync_router)  # ✅ Добавляем новый роутер синхронизации


@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в МАИ таблетки!"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)