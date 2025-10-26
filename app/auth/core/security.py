from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.db.session import db_helper
from app.auth.crud.user import get_user_by_uuid
from app.auth.models.user import User
from app.auth.utils.password import verify_password

security = HTTPBasic()


async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    user: User | None = await get_user_by_uuid(db, credentials.username)

    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

    if not user or not verify_password(
        credentials.password,
        user.hash_password,
    ):
        raise unauthed_exc
        
    return user