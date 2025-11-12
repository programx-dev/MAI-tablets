# app/medicines/api/sync.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional
from app.db.session import db_helper
from app.core.security import get_current_user
from app.auth.models.user import User
from app.medicines.models.medication import Medication
from app.medicines.models.intake import IntakeHistory
from app.medicines.schemas.schemas import MedicationResponse, IntakeHistoryResponse

router = APIRouter(prefix="/sync", tags=["sync"])


class ClientIntakeHistoryUpdate:
    server_id: Optional[int]
    medication_server_id: int  # ID лекарства на сервере
    status: str  # 'taken', 'skipped'
    taken_time: datetime
    notes: Optional[str] = None


class PushSyncRequest:
    intake_history: List[ClientIntakeHistoryUpdate]


@router.get("/pull")
async def pull_sync(
    since: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_dependency)
):
    """
    Выгрузка новых или изменённых данных с сервера.
    """
    # Запросить лекарства пользователя
    medications_query = select(Medication).where(Medication.patient_id == current_user.uuid)
    if since:
        medications_query = medications_query.where(Medication.updated_at > since)

    medications_result = await db.execute(medications_query)
    medications = [MedicationResponse.from_orm(m) for m in medications_result.scalars().all()]

    # Запросить историю приёма пользователя
    intake_history_query = select(IntakeHistory).join(Medication).where(
        Medication.patient_id == current_user.uuid
    )
    if since:
        intake_history_query = intake_history_query.where(IntakeHistory.updated_at > since)

    intake_result = await db.execute(intake_history_query)
    intake_history = [IntakeHistoryResponse.from_orm(i) for i in intake_result.scalars().all()]

    return {
        "medications": medications,
        "intake_history": intake_history
    }


@router.post("/push")
async def push_sync(
    data: PushSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_dependency)
):
    """
    Отправка локальных изменений на сервер.
    """
    response_data = {"intake_history": []}

    for idx, intake in enumerate(data.intake_history):
        if intake.server_id is not None:
            # Обновление существующей записи
            stmt = select(IntakeHistory).join(Medication).where(
                IntakeHistory.id == intake.server_id,
                Medication.patient_id == current_user.uuid  # Защита от чужих данных
            )
            result = await db.execute(stmt)
            existing_intake = result.scalar_one_or_none()

            if existing_intake:
                existing_intake.status = intake.status
                existing_intake.taken_time = intake.taken_time
                existing_intake.notes = intake.notes
                await db.commit()
                await db.refresh(existing_intake)
                response_data["intake_history"].append({"client_id": idx, "server_id": existing_intake.id})
            else:
                raise HTTPException(status_code=404, detail=f"IntakeHistory with id {intake.server_id} not found or not owned by user.")
        else:
            # Создание новой записи
            # Проверяем, что лекарство принадлежит пользователю
            med_stmt = select(Medication.id).where(
                Medication.id == intake.medication_server_id,
                Medication.patient_id == current_user.uuid
            )
            med_result = await db.execute(med_stmt)
            med_id = med_result.scalar_one_or_none()

            if not med_id:
                raise HTTPException(status_code=404, detail=f"Medication with id {intake.medication_server_id} not found or not owned by user.")

            new_intake = IntakeHistory(
                medication_id=med_id,
                scheduled_time=intake.taken_time,  # или null, если точное время неизвестно
                taken_time=intake.taken_time,
                status=intake.status,
                notes=intake.notes
            )
            db.add(new_intake)
            await db.commit()
            await db.refresh(new_intake)
            response_data["intake_history"].append({"client_id": idx, "server_id": new_intake.id})

    # Обновляем last_synced_time пользователя
    current_user.last_synced_time = datetime.utcnow()
    await db.commit()

    return response_data
