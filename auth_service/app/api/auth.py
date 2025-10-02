from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import UserRegister, UserResponse, UserLogin, LoginResponse
from app.crud.user import create_user, authenticate_user
from app.schemas.auth import UserRole

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    user, raw_password = await create_user(db, user_in.role)
    return UserResponse(
        uuid=user.uuid,
        role=UserRole(user.role),
        password=raw_password,
        created_at=user.created_at,
    )


@router.post("/login", response_model=LoginResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    success = await authenticate_user(db, user_in.uuid, user_in.password, user_in.role)
    return LoginResponse(success=success)
