from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.db.session import db_helper
from app.auth.models.user import User
from app.auth.core.security import get_current_user
from app.auth.crud.friend import add_med_friend, remove_med_friend, get_med_friend, get_patient
from app.auth.schemas.friend import FriendAdd, FriendAddResponse, FriendGetResponse, PatientGetResponse

router = APIRouter(prefix="/friends", tags=["friends"])

@router.post("/add", response_model=FriendAddResponse)
async def add_friend(
    data: FriendAdd,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Добавить мед-друга по UUID"""
    result = await add_med_friend(db, current_user.id, data.uuid)
    return result

@router.delete("/remove", response_model=FriendAddResponse)
async def remove_friend(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Удалить мед-друга"""
    result = await remove_med_friend(db, current_user.id)
    return result

@router.get("/get_med_friend", response_model=FriendGetResponse)
async def get_my_med_friend(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Получить UUID мед-друга для текущего пользователя (пациента)"""
    result = await get_med_friend(db, current_user.id)
    return result

@router.get("/get_patient/{friend_uuid}", response_model=PatientGetResponse)
async def get_patient_by_friend_uuid(
    friend_uuid: str,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Получить UUID пациента по UUID мед-друга"""
    result = await get_patient(db, friend_uuid)
    return result