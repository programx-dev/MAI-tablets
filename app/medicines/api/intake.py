from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import db_helper
from app.auth.models.user import User
from app.core.security import get_current_user
from app.medicines.models.medication import Medication
from app.medicines.schemas.schemas import IntakeHistoryCreateRequest, IntakeHistoryResponse
from app.medicines.crud.intake import create_or_update_intake_history, get_intake_history_by_patient_id
from app.auth.crud.friend import get_patient_id_for_current_friend

router = APIRouter(prefix="/intake", tags=["intake"])

# --- Intake History ---

@router.post("/add_or_update", response_model=IntakeHistoryResponse)
async def add_or_update_intake(
    data: IntakeHistoryCreateRequest,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user), # Пациент (current_user) добавляет/обновляет прием
):
    """Добавить или обновить запись о приеме лекарства"""
    # Проверим, принадлежит ли медикамент пользователю
    stmt = select(Medication).where(
        and_(Medication.id == data.medication_id, Medication.patient_id == current_user.uuid)
    )
    result = await db.execute(stmt)
    medication = result.scalar_one_or_none()

    if not medication:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Medication does not belong to current user")

    intake = await create_or_update_intake_history(db, data.model_dump())
    return intake

@router.get("/get_intakes_for_current_friend") # Изменим путь
async def get_intakes_for_current_friend(
    # friend_uuid: str, # Убираем этот параметр
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user), # Это мед-друг
):
    """Получить всю историю приемов пациента, для которого текущий пользователь является мед-другом"""
    # 1. Найти id пациента по id текущего мед-друга
    patient_id = await get_patient_id_for_current_friend(db, current_user.uuid) # Передаём id мед-друга

    if not patient_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found for this med friend")

    # 2. Получить историю приемов пациента
    intakes = await get_intake_history_by_patient_id(db, patient_id)
    return intakes # Просто возвращаем список объектов ORM

