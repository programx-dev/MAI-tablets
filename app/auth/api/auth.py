# app/auth/api/auth.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.auth.crud.user import create_user
from app.db.session import db_helper
from app.auth.models.user import User
from app.auth.schemas.auth import UserCreateRequest, UserCreateResponse  

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(db_helper.session_dependency)
):
    user, raw_password = await create_user(db, username=user_data.username)
    return UserCreateResponse(
        uuid=user.uuid,
        username=user.username,
        password=raw_password  
    )