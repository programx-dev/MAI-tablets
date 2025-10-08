from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import db_helper
from app.schemas.auth import UserRegister, UserResponse, UserLogin, LoginResponse
from app.crud.user import create_user, authenticate_user
from app.schemas.auth import UserRole

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncSession = Depends(db_helper.session_dependency)):
    user, raw_password = await create_user(db, user_in.role)
    return UserResponse(
        uuid=user.uuid,
        role=UserRole(user.role),
        password=raw_password,
        created_at=user.created_at,
    )


@router.post("/login", response_model=LoginResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(db_helper.session_dependency)):
    success = await authenticate_user(db, user_in.uuid, user_in.password, user_in.role)
    return LoginResponse(success=success)
