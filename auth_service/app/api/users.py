from fastapi import APIRouter, Depends
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "uuid": current_user.uuid,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }
