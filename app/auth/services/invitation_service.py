# app/auth/services/invitation_service.py

import random
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.crud import invitation as crud_invitation
from app.auth.crud import friend as crud_friend

INVITATION_CODE_LIFETIME_SECONDS = 180  # 3 минуты

async def _generate_unique_simple_code(db: AsyncSession) -> str:
    """Генерирует уникальный 6-значный числовой код."""
    while True:
        code = str(random.randint(100000, 999999))
        if not await crud_invitation.code_exists(db, code):
            return code

async def create_invitation(db: AsyncSession, med_friend_id: str) -> tuple[str, int]:
    """
    Создает код-приглашение для мед-друга.
    Возвращает кортеж (код, время жизни в секундах).
    """
    # Проверка, не является ли пользователь уже чьим-то мед-другом
    if await crud_friend.get_patient_by_friend_id(db, med_friend_id):
        raise ValueError("Вы уже являетесь мед-другом. Нельзя генерировать новые приглашения.")

    code = await _generate_unique_simple_code(db)
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=INVITATION_CODE_LIFETIME_SECONDS)
    
    await crud_invitation.create_invitation_code_db(
        db, code=code, med_friend_id=med_friend_id, expires_at=expires_at
    )
    
    return code, INVITATION_CODE_LIFETIME_SECONDS