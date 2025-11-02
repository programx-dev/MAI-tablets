# app/auth/tasks/cleanup_tasks.py

import datetime
import logging
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.invitation import InvitationCode
from app.db.session import db_helper

# Настраиваем простой логгер для вывода информации о работе задачи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cleanup_expired_codes():
    """
    Находит и удаляет все просроченные и/или использованные коды-приглашения.
    """
    logger.info("Запуск фоновой задачи: очистка кодов-приглашений...")
    
    # Создаем асинхронную сессию БД специально для этой задачи
    async with db_helper.session_factory() as session:
        try:
            now = datetime.datetime.utcnow()
            
            # Определяем условие для удаления: код либо использован, либо его срок истек
            stmt = delete(InvitationCode).where(
                (InvitationCode.is_used == True) | (InvitationCode.expires_at < now)
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            # result.rowcount содержит количество удаленных строк
            if result.rowcount > 0:
                logger.info(f"Задача очистки завершена. Удалено кодов: {result.rowcount}.")
            else:
                logger.info("Задача очистки завершена. Просроченных кодов не найдено.")

        except Exception as e:
            logger.error(f"Ошибка во время выполнения задачи очистки кодов: {e}")
            await session.rollback()