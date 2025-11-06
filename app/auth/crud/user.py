# app/auth/crud/user.py
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.auth.models.user import User
from app.auth.utils.password import hash_password


async def create_user(db: AsyncSession, username: str) -> tuple[User, str]:  # ✅ Принимаем username
    raw_password = secrets.token_urlsafe(8)
    hashed_password = hash_password(raw_password)

    user = User(
        username=username,  # ✅ Передаём в модель
        hash_password=hashed_password
        # relation_id = ...
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user, raw_password


async def get_user_by_uuid(db: AsyncSession, uuid_: str) -> User | None:
    stmt = select(User).where(User.uuid == uuid_)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()