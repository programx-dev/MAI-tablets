import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
import os

from app.db.session import db_helper
from app.core.scheduler import scheduler
from app.auth.tasks.cleanup_tasks import cleanup_old_data

from app.auth.api.auth import router as auth_router
from app.auth.api.friend import router as friend_router
from app.medicines.api.medication import router as medication_router
from app.medicines.api.intake import router as intake_router
from app.medicines.api.sync import router as sync_router


@asynccontextmanager
async def lifespan(app: FastAPI):
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


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://158.160.68.214:8000",  
        "http://localhost:19006",      
        "http://localhost:8081",       
        "exp://127.0.0.1:19000",       
        "*",                           
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


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,

    )