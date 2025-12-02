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


@router.post("/add_or_update", response_model=IntakeHistoryResponse)
async def add_or_update_intake(
    data: IntakeHistoryCreateRequest,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user), 
):
    """Добавить или обновить запись о приеме лекарства"""
    stmt = select(Medication).where(
        and_(Medication.id == data.medication_id, Medication.patient_id == current_user.uuid)
    )
    result = await db.execute(stmt)
    medication = result.scalar_one_or_none()

    if not medication:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Medication does not belong to current user")

    intake = await create_or_update_intake_history(db, data.model_dump())
    return intake

@router.get("/get_intakes_for_current_friend") 
async def get_intakes_for_current_friend(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user), 
):
    """Получить всю историю приемов пациента, для которого текущий пользователь является мед-другом"""
    patient_id = await get_patient_id_for_current_friend(db, current_user.uuid) # Передаём id мед-друга

    if not patient_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found for this med friend")

    intakes = await get_intake_history_by_patient_id(db, patient_id)
    return intakes 

