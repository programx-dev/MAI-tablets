from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import db_helper
from app.models.user import User
from app.schemas.auth import RegisterResponse, LoginResponse
from app.crud.user import create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
async def register(db: AsyncSession = Depends(db_helper.session_dependency)):
    user, raw_password = await create_user(db)
    return RegisterResponse(
        uuid=user.uuid,
        password=raw_password,
        created_at=user.created_at
    )


@router.get("/login", response_model=LoginResponse)
async def login(current_user: User = Depends(get_current_user)):
    return LoginResponse(
        uuid=current_user.uuid,
        created_at=current_user.created_at
    )
