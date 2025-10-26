from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.medicines.models.medication import Medication

# --- Medications ---

async def create_medication(
    db: AsyncSession, patient_id: int, medication_data: dict
) -> Medication:
    medication = Medication(patient_id=patient_id, **medication_data)
    db.add(medication)
    await db.commit()
    await db.refresh(medication)
    return medication


async def get_medications_by_patient_id(
    db: AsyncSession, patient_id: int
) -> list[Medication]:
    stmt = select(Medication).where(Medication.patient_id == patient_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())