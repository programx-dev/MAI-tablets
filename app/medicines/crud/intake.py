from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.medicines.models.intake import IntakeHistory 
from app.medicines.crud.medication import get_medications_by_patient_id 


async def create_or_update_intake_history(
    db: AsyncSession, intake_data: dict
) -> IntakeHistory:
    stmt = select(IntakeHistory).where(
        and_(
            IntakeHistory.medication_id == intake_data["medication_id"],
            IntakeHistory.scheduled_time == intake_data["scheduled_time"],
        )
    )
    result = await db.execute(stmt)
    existing_intake = result.scalar_one_or_none()

    if existing_intake:
        for key, value in intake_data.items():
            if value is not None:  
                setattr(existing_intake, key, value)
        await db.commit()
        await db.refresh(existing_intake)
        return existing_intake
    else:
        intake = IntakeHistory(**intake_data)
        db.add(intake)
        await db.commit()
        await db.refresh(intake)
        return intake


async def get_intake_history_by_patient_id(
    db: AsyncSession, patient_id: int
) -> list[IntakeHistory]:
    medications = await get_medications_by_patient_id(db, patient_id)
    medication_ids = [med.id for med in medications]

    if not medication_ids:
        return []

    from app.medicines.models.intake import IntakeHistory 
    stmt = select(IntakeHistory).where(IntakeHistory.medication_id.in_(medication_ids))
    result = await db.execute(stmt)
    return list(result.scalars().all())