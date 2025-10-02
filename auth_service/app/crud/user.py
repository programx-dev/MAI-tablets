import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.utils.password import hash_password, verify_password
from app.schemas.auth import UserRole


async def create_user(db: AsyncSession, role: UserRole) -> tuple[User, str]:
    raw_password = secrets.token_urlsafe(8)
    hashed = hash_password(raw_password)

    user = User(role=role.value, hash_password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user, raw_password


async def authenticate_user(
    db: AsyncSession, uuid_: str, password: str, role: UserRole
) -> bool:
    stmt = select(User).where(User.uuid == uuid_, User.role == role.value)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return False
    return verify_password(password, user.hash_password)
