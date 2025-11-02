# app/auth/crud/friend.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.auth.models.user import User

async def get_patient_by_friend_id(db: AsyncSession, friend_id: int) -> User | None:
    """Находит пациента, привязанного к ID мед-друга."""
    stmt = select(User).where(User.relation_id == friend_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_friend_by_id(db: AsyncSession, friend_id: int) -> User | None:
    """Находит пользователя (мед-друга) по его ID."""
    return await db.get(User, friend_id)

async def update_patient_relation(db: AsyncSession, patient: User, friend_id: int | None) -> None:
    """Обновляет или удаляет связь мед-друга у пациента."""
    patient.relation_id = friend_id
    await db.commit()

# Вот ваша функция с новым, консистентным именем
async def get_patient_id_for_current_friend(db: AsyncSession, friend_id: int) -> int | None:
    """Находит id пациента, у которого relation_id равно friend_id."""
    stmt = select(User.id).where(User.relation_id == friend_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()