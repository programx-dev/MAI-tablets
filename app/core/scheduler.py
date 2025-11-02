# app/core/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Создаем единственный экземпляр планировщика для всего приложения
scheduler = AsyncIOScheduler(timezone="UTC")