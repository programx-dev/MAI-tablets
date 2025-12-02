# app/medicines/api/sync.py

from datetime import date, datetime, time  # ✅ Добавьте date и time
from typing import List, Optional, Literal # ✅ Убедитесь, что List импортирован
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import db_helper
from app.core.security import get_current_user
from app.auth.models.user import User
from app.medicines.models.medication import Medication
from app.medicines.models.intake import IntakeHistory
from app.medicines.schemas.schemas import MedicationResponse, IntakeHistoryResponse
from pydantic import BaseModel

router = APIRouter(prefix="/sync", tags=["sync"])



class ClientIntakeHistoryUpdate(BaseModel):
    server_id: Optional[int] 
    medication_server_id: int 
    status: str 
    taken_time: datetime
    notes: Optional[str] = None


class ClientMedicationUpdate(BaseModel):
    server_id: Optional[int] 
    action: Literal["create", "update"] 
    name: str
    form: str 
    instructions: Optional[str] = None
    start_date: date 
    end_date: Optional[date] = None 
    schedule_type: str 
    week_days: Optional[List[int]] = None 
    interval_days: Optional[int] = None
    times_per_day: List[str] 


class PushSyncRequest(BaseModel):
    medications: List[ClientMedicationUpdate] = []
    intake_history: List[ClientIntakeHistoryUpdate] = []



@router.get("/pull", response_model=dict)
async def pull_sync(
    since: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_helper.session_dependency)
):
    """
    Выгрузка новых или изменённых данных с сервера.
    """
    medications_query = select(Medication).where(
        Medication.patient_id == current_user.uuid
    )
    if since:
        medications_query = medications_query.where(Medication.updated_at > since)

    medications_result = await db.execute(medications_query)
    medications = [MedicationResponse.from_orm(m) for m in medications_result.scalars().all()]

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
    response_data = {
        "medications": [],
        "intake_history": []
    }

    for idx, med in enumerate(data.medications):
        if med.action == "update":
            if med.server_id is None:
                # Ошибка: нельзя обновить, если нет server_id
                raise HTTPException(status_code=400, detail=f"Cannot update medication without server_id. Index: {idx}")

            stmt = select(Medication).where(
                Medication.id == med.server_id,
                Medication.patient_id == current_user.uuid # Защита от чужих данных
            )
            result = await db.execute(stmt)
            existing_med = result.scalar_one_or_none()

            if existing_med:
                converted_times = [time.fromisoformat(t) for t in med.times_per_day]

                existing_med.name = med.name
                existing_med.form = med.form
                existing_med.instructions = med.instructions
                existing_med.start_date = med.start_date
                existing_med.end_date = med.end_date
                existing_med.schedule_type = med.schedule_type
                existing_med.week_days = med.week_days
                existing_med.interval_days = med.interval_days
                existing_med.times_per_day = converted_times
                await db.commit()
                await db.refresh(existing_med)
                response_data["medications"].append({"client_id": idx, "server_id": existing_med.id})
            else:
                raise HTTPException(status_code=404, detail=f"Medication with id {med.server_id} not found or not owned by user. Index: {idx}")

        elif med.action == "create":
            if med.server_id is not None:
                raise HTTPException(status_code=400, detail=f"Cannot create medication with existing server_id. Index: {idx}")

            converted_times = [time.fromisoformat(t) for t in med.times_per_day]

            new_med = Medication(
                patient_id=current_user.uuid, 
                name=med.name,
                form=med.form,
                instructions=med.instructions,
                start_date=med.start_date,
                end_date=med.end_date,
                schedule_type=med.schedule_type,
                week_days=med.week_days,
                interval_days=med.interval_days,
                times_per_day=converted_times 
            )
            db.add(new_med)
            await db.commit()
            await db.refresh(new_med)
            response_data["medications"].append({"client_id": idx, "server_id": new_med.id})

    for idx, intake in enumerate(data.intake_history):
        if intake.server_id is not None:
            stmt = select(IntakeHistory).join(Medication).where(
                IntakeHistory.id == intake.server_id,
                Medication.patient_id == current_user.uuid  
            )
            result = await db.execute(stmt)
            existing_intake = result.scalar_one_or_none()

            if existing_intake:
                existing_intake.status = intake.status
                existing_intake.taken_time = intake.taken_time
                existing_intake.notes = intake.notes
                # updated_at обновится автоматически
                await db.commit()
                await db.refresh(existing_intake)
                response_data["intake_history"].append({"client_id": idx, "server_id": existing_intake.id})
            else:
                raise HTTPException(status_code=404, detail=f"IntakeHistory with id {intake.server_id} not found or not owned by user. Index: {idx}")
        else:
            med_stmt = select(Medication.id).where(
                Medication.id == intake.medication_server_id,
                Medication.patient_id == current_user.uuid
            )
            med_result = await db.execute(med_stmt)
            med_id = med_result.scalar_one_or_none()

            if not med_id:
                raise HTTPException(status_code=404, detail=f"Medication with id {intake.medication_server_id} not found or not owned by user. Index: {idx}")

            new_intake = IntakeHistory(
                medication_id=med_id,
                scheduled_time=intake.taken_time, 
                taken_time=intake.taken_time,
                status=intake.status,
                notes=intake.notes
            )
            db.add(new_intake)
            await db.commit()
            await db.refresh(new_intake)
            response_data["intake_history"].append({"client_id": idx, "server_id": new_intake.id})

    current_user.last_synced_time = datetime.utcnow()
    await db.commit()

    return response_data