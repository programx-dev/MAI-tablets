# app/medicines/api/medication.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import db_helper
from app.auth.models.user import User
from app.core.security import get_current_user
from app.medicines.schemas.schemas import MedicationCreateRequest, MedicationResponse
from app.medicines.crud.medication import create_medication, get_medications_by_patient_id, delete_medication
from app.medicines.models.medication import Medication

router = APIRouter(prefix="/medicines", tags=["medicines"])


@router.post("/add_medication", response_model=MedicationResponse)
async def add_medication(
    data: MedicationCreateRequest,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Добавить препарат для текущего пользователя (пациента)"""
    medication = await create_medication(db, current_user.uuid, data.model_dump())
    return medication


@router.get("/get_medications_for_current_friend")
async def get_medications_for_current_friend(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Мед-друг может просматривать препараты пациента, но НЕ управлять ими."""
    from app.auth.crud.friend import get_patient_id_for_current_friend
    patient_id = await get_patient_id_for_current_friend(db, current_user.uuid)
    if not patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found for this med friend"
        )
    medications = await get_medications_by_patient_id(db, patient_id)
    return medications


@router.delete(
    "/delete_medication/{medication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Medication deleted successfully"},
        403: {"description": "Only patients can delete medications"},
        404: {"description": "Medication not found or does not belong to you"},
    }
)
async def delete_medication_endpoint(
    medication_id: int,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить лекарство — ТОЛЬКО для пациента и ТОЛЬКО своё.
    Мед-друзья НЕ имеют права на удаление.
    """

    stmt = select(Medication).where(
        (Medication.id == medication_id) & (Medication.patient_id == current_user.uuid)
    )
    result = await db.execute(stmt)
    medication = result.scalar_one_or_none()

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found or does not belong to you"
        )

    success = await delete_medication(db, medication_id, current_user.uuid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deletion failed"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)