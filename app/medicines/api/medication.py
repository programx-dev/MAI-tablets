from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import db_helper
from app.auth.models.user import User
from app.core.security import get_current_user
from app.medicines.schemas.schemas import MedicationCreateRequest, MedicationResponse
from app.medicines.crud.medication import create_medication, get_medications_by_patient_id
from app.auth.crud.friend import get_patient_id_for_current_friend

router = APIRouter(prefix="/medicines", tags=["medicines"])

# --- Medications ---

@router.post("/add_medication", response_model=MedicationResponse)
async def add_medication(
    data: MedicationCreateRequest,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user), # Пациент (current_user) добавляет препарат
):
    """Добавить препарат для текущего пользователя (пациента)"""
    medication = await create_medication(db, current_user.id, data.model_dump())
    return medication

@router.get("/get_medications_for_current_friend") # Изменим путь
async def get_medications_for_current_friend(
    # friend_uuid: str, # Убираем этот параметр
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user), # Это мед-друг
):
    """Получить все препараты пациента, для которого текущий пользователь является мед-другом"""
    # 1. Найти id пациента по id текущего мед-друга
    patient_id = await get_patient_id_for_current_friend(db, current_user.id) # Передаём id мед-друга

    if not patient_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found for this med friend")

    # 2. Получить препараты пациента
    medications = await get_medications_by_patient_id(db, patient_id)
    return medications # Просто возвращаем список объектов ORM