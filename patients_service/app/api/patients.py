from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app import models, schemas

router = APIRouter()


# ------------------- PATIENTS -------------------

@router.post("/", response_model=schemas.Patient)
async def create_patient(patient: schemas.PatientCreate, db: AsyncSession = Depends(get_db)):
    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)

    # Создаем объект для сериализации без ленивых связей
    return schemas.Patient.model_validate({
        "id": db_patient.id,
        "name": db_patient.name,
        "birth_date": db_patient.birth_date,
        "prescriptions": [],
        "intakes": []
    })


@router.get("/{patient_id}", response_model=schemas.Patient)
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Patient)
        .where(models.Patient.id == patient_id)
        .options(
            selectinload(models.Patient.prescriptions),
            selectinload(models.Patient.intakes)
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return schemas.Patient.model_validate({
        "id": patient.id,
        "name": patient.name,
        "birth_date": patient.birth_date,
        "prescriptions": [schemas.Prescription.model_validate(p) for p in patient.prescriptions],
        "intakes": [schemas.Intake.model_validate(i) for i in patient.intakes]
    })


@router.get("/", response_model=list[schemas.Patient])
async def list_patients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Patient)
        .options(
            selectinload(models.Patient.prescriptions),
            selectinload(models.Patient.intakes)
        )
    )
    patients = result.scalars().all()

    return [
        schemas.Patient.model_validate({
            "id": p.id,
            "name": p.name,
            "birth_date": p.birth_date,
            "prescriptions": [schemas.Prescription.model_validate(pr) for pr in p.prescriptions],
            "intakes": [schemas.Intake.model_validate(i) for i in p.intakes]
        })
        for p in patients
    ]


@router.delete("/{patient_id}")
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Patient).where(models.Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await db.delete(patient)
    await db.commit()
    return {"detail": f"Patient {patient_id} deleted"}


# ------------------- PRESCRIPTIONS -------------------

@router.post("/{patient_id}/prescriptions", response_model=schemas.Prescription)
async def add_prescription(patient_id: int, prescription: schemas.PrescriptionCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Patient).where(models.Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db_prescription = models.Prescription(patient_id=patient_id, **prescription.model_dump())
    db.add(db_prescription)
    await db.commit()
    await db.refresh(db_prescription)

    return schemas.Prescription.model_validate({
        "id": db_prescription.id,
        "patient_id": db_prescription.patient_id,
        "drug_name": db_prescription.drug_name,
        "dosage": db_prescription.dosage
    })


@router.get("/{patient_id}/prescriptions", response_model=list[schemas.Prescription])
async def get_prescriptions(patient_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Prescription)
        .where(models.Prescription.patient_id == patient_id)
    )
    prescriptions = result.scalars().all()

    return [
        schemas.Prescription.model_validate({
            "id": p.id,
            "patient_id": p.patient_id,
            "drug_name": p.drug_name,
            "dosage": p.dosage
        })
        for p in prescriptions
    ]


# ------------------- INTAKES -------------------

@router.post("/prescriptions/{prescription_id}/intakes", response_model=schemas.Intake)
async def add_intake(prescription_id: int, intake: schemas.IntakeCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Prescription).where(models.Prescription.id == prescription_id))
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    db_intake = models.Intake(prescription_id=prescription_id, **intake.model_dump())
    db.add(db_intake)
    await db.commit()
    await db.refresh(db_intake)

    return schemas.Intake.model_validate({
        "id": db_intake.id,
        "patient_id": db_intake.patient_id,
        "intake_time": db_intake.time,
        "amount": db_intake.amount
    })


@router.get("/prescriptions/{prescription_id}/intakes", response_model=list[schemas.Intake])
async def get_intakes(prescription_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Intake).where(models.Intake.prescription_id == prescription_id))
    intakes = result.scalars().all()

    return [
        schemas.Intake.model_validate({
            "id": i.id,
            "patient_id": i.patient_id,
            "intake_time": i.time,
            "amount": i.amount
        })
        for i in intakes
    ]
