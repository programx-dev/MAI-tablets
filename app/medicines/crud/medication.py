# app/medicines/crud/medication.py
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.medicines.models.medication import Medication


async def create_medication(
    db: AsyncSession, patient_id: str, medication_data: dict
) -> Medication:
    medication = Medication(patient_id=patient_id, **medication_data)
    db.add(medication)
    await db.commit()
    await db.refresh(medication)
    return medication


async def get_medications_by_patient_id(
    db: AsyncSession, patient_id: str
) -> list[Medication]:
    stmt = select(Medication).where(Medication.patient_id == patient_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_medication(
    db: AsyncSession, medication_id: int, patient_id: str
) -> bool:
    stmt = select(Medication).where(
        (Medication.id == medication_id) & (Medication.patient_id == patient_id)
    )
    result = await db.execute(stmt)
    medication = result.scalar_one_or_none()

    if not medication:
        return False

    await db.execute(delete(Medication).where(Medication.id == medication_id))
    await db.commit()
    return True