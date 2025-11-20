# app/main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ← добавлен импорт
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta

from app.db.session import db_helper
from app.core.scheduler import scheduler
from app.auth.tasks.cleanup_tasks import cleanup_old_data

# Роутеры
from app.auth.api.auth import router as auth_router
from app.auth.api.friend import router as friend_router
from app.medicines.api.medication import router as medication_router
from app.medicines.api.intake import router as intake_router
from app.medicines.api.sync import router as sync_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем ежедневную очистку (первый запуск через 1 мин после старта)
    scheduler.add_job(
        cleanup_old_data,
        "interval",
        days=1,
        id="daily_cleanup",
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=1),
    )
    scheduler.start()
    print("✅ Планировщик запущен: daily_cleanup (ежедневно)")

    yield

    scheduler.shutdown()
    print("🛑 Планировщик остановлен.")


# 🔹 Сначала создаём приложение
app = FastAPI(lifespan=lifespan)

# 🔹 Потом добавляем middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:19006",           # Expo Web
        "exp://192.168.31.174:19000",       # Expo Go (порт 19000 — стандартный для LAN)
        "exp://192.168.31.174:8081",        # возможный альтернативный порт
        "exp://192.168.31.174",             # общая маска
        "http://192.168.31.174:8000",       # прямой вызов API из браузера
        "*",                                # ← для разработки допустимо
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(friend_router)
app.include_router(medication_router)
app.include_router(intake_router)
app.include_router(sync_router)


@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в МАИ таблетки!"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",     
        reload=True,
    )