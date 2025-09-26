from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# ------------------- SCHEMAS FOR PRESCRIPTIONS -------------------

class PrescriptionBase(BaseModel):
    drug_name: str
    dosage: str

class PrescriptionCreate(PrescriptionBase):
    pass

class Prescription(PrescriptionBase):
    id: int
    patient_id: int

    model_config = ConfigDict(from_attributes=True)


# ------------------- SCHEMAS FOR INTAKES -------------------

class IntakeBase(BaseModel):
    intake_time: datetime  # меняем на datetime для точного времени
    amount: str

class IntakeCreate(IntakeBase):
    pass

class Intake(IntakeBase):
    id: int
    patient_id: int

    model_config = ConfigDict(from_attributes=True)


# ------------------- SCHEMAS FOR PATIENT -------------------

class PatientBase(BaseModel):
    name: str
    birth_date: date

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    prescriptions: List[Prescription] = []
    intakes: List[Intake] = []

    model_config = ConfigDict(from_attributes=True)
