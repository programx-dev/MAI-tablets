# app/auth/api/friend.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import db_helper
from app.auth.models.user import User
from app.core.security import get_current_user
from app.auth.services import invitation_service, friend_service
from app.auth.crud import friend as crud_friend # Импортируем для GET-запросов
from app.auth.schemas.friend import (
    FriendAddByCode,
    FriendActionResponse,
    FriendGetResponse,
    PatientGetResponse,
    InvitationCodeGenerateResponse,
)

router = APIRouter(prefix="/friends", tags=["friends"])

# --- Эндпоинты для генерации и использования приглашений ---

@router.post(
    "/invitation",
    response_model=InvitationCodeGenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_invitation(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Сгенерировать уникальный временный код-приглашение (для мед-друга)."""
    try:
        code, lifetime = await invitation_service.create_invitation(db, current_user.id)
        return InvitationCodeGenerateResponse(code=code, expires_in_seconds=lifetime)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/add", response_model=FriendActionResponse)
async def add_friend_by_invitation_code(
    data: FriendAddByCode,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Добавить мед-друга по коду-приглашению (для пациента)."""
    try:
        await friend_service.add_friend_by_code(db, current_user, data.code)
        return FriendActionResponse(success=True, message="Мед-друг успешно добавлен.")
    except friend_service.FriendServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Эндпоинты для удаления/отписки ---

@router.delete("/remove-for-patient", response_model=FriendActionResponse)
async def remove_friend_for_patient(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Удалить мед-друга (для пациента)."""
    try:
        await friend_service.remove_friend_for_patient(db, current_user)
        return FriendActionResponse(success=True, message="Мед-друг успешно удален.")
    except friend_service.FriendServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/unsubscribe-from-patient", response_model=FriendActionResponse)
async def unsubscribe_from_patient(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Отписаться от пациента (для мед-друга)."""
    try:
        await friend_service.unsubscribe_from_patient(db, current_user)
        return FriendActionResponse(success=True, message="Вы успешно отписались от пациента.")
    except friend_service.FriendServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Эндпоинты для получения информации (GET) ---

@router.get("/get-med-friend", response_model=FriendGetResponse)
async def get_my_med_friend(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user), # Это пациент
):
    """Получить информацию о своем мед-друге (для пациента)."""
    result = await friend_service.get_med_friend_info(db, current_user)
    return result

@router.get("/get-patient", response_model=PatientGetResponse)
async def get_my_patient(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user), # Это мед-друг
):
    """Получить информацию о своем пациенте (для мед-друга)."""
    result = await friend_service.get_patient_info_for_friend(db, current_user)
    return result