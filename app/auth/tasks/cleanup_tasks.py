# app/auth/tasks/cleanup_tasks.py
import datetime
import logging
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.invitation import InvitationCode
from app.medicines.models.intake import IntakeHistory
from app.medicines.models.medication import Medication
from app.db.session import db_helper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cleanup_old_data():
    """
    Ежедневная очистка данных:
    - Удаляет просроченные/использованные коды-приглашения
    - Удаляет IntakeHistory и Medication старше 60 дней (2 месяца)
    """
    logger.info("Запуск ежедневной очистки данных...")

    async with db_helper.session_factory() as session: 
        try:
            now = datetime.datetime.now(datetime.timezone.utc)

            stmt_codes = delete(InvitationCode).where(
                (InvitationCode.is_used == True) | (InvitationCode.expires_at < now)
            )
            result_codes = await session.execute(stmt_codes)

            two_months_ago = now - datetime.timedelta(days=60)
            stmt_intake = delete(IntakeHistory).where(
                IntakeHistory.created_at < two_months_ago
            )
            result_intake = await session.execute(stmt_intake)

            stmt_meds = delete(Medication).where(
                Medication.created_at < two_months_ago
            )
            result_meds = await session.execute(stmt_meds)

            await session.commit()

            logger.info(
                f" Очистка завершена:\n"
                f"   — Коды: {result_codes.rowcount}\n"
                f"   — История приёма: {result_intake.rowcount}\n"
                f"   — Рецепты: {result_meds.rowcount}"
            )

        except Exception as e:
            logger.error(f"Ошибка в cleanup_old_data: {e}")
            await session.rollback()
            raise
