from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base  # Base из db.py

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)

    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    intakes = relationship("Intake", back_populates="patient", cascade="all, delete-orphan")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    drug_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)

    patient = relationship("Patient", back_populates="prescriptions")


class Intake(Base):
    __tablename__ = "intakes"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    time = Column(String, nullable=False)
    amount = Column(String, nullable=False)

    patient = relationship("Patient", back_populates="intakes")
