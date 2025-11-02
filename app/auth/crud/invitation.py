# app/auth/crud/invitation.py

import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.auth.models.invitation import InvitationCode

async def code_exists(db: AsyncSession, code: str) -> bool:
    """Проверяет, существует ли код в БД."""
    stmt = select(InvitationCode).where(InvitationCode.code == code)
    result = await db.execute(select(stmt.exists()))
    return bool(result.scalar())

async def create_invitation_code_db(
    db: AsyncSession, code: str, med_friend_id: int, expires_at: datetime.datetime
) -> InvitationCode:
    """Сохраняет новый код-приглашение в БД."""
    invitation = InvitationCode(
        code=code,
        med_friend_id=med_friend_id,
        expires_at=expires_at,
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)
    return invitation

async def get_invitation_by_code_db(db: AsyncSession, code: str) -> InvitationCode | None:
    """Находит код-приглашение в БД."""
    stmt = select(InvitationCode).where(InvitationCode.code == code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def delete_invitation_code_db(db: AsyncSession, code_id: int) -> None:
    """Удаляет код-приглашение из БД."""
    stmt = delete(InvitationCode).where(InvitationCode.id == code_id)
    await db.execute(stmt)
    await db.commit()