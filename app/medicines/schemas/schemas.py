from pydantic import BaseModel
from datetime import date, time, datetime
from typing import List, Optional

# --- Medications ---

class MedicationCreateRequest(BaseModel):
    name: str
    form: Optional[str] = None
    instructions: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    schedule_type: str # 'daily', 'weekly_days', 'every_x_days'
    week_days: Optional[List[int]] = None # [1, 3, 5]
    interval_days: Optional[int] = None # e.g., 3
    times_per_day: List[time] # ['08:00', '14:30']

class MedicationResponse(BaseModel):
    id: int
    patient_id: str
    name: str
    form: Optional[str]
    instructions: Optional[str]
    start_date: date
    end_date: Optional[date]
    schedule_type: str
    week_days: Optional[List[int]]
    interval_days: Optional[int]
    times_per_day: List[time]

    class Config:
        from_attributes = True

# --- Intake History ---

class IntakeHistoryCreateRequest(BaseModel):
    medication_id: int
    scheduled_time: datetime
    taken_time: Optional[datetime] = None
    status: str # 'taken', 'skipped'
    notes: Optional[str] = None

class IntakeHistoryUpdateRequest(BaseModel):
    taken_time: Optional[datetime] = None
    status: Optional[str] = None # 'taken', 'skipped'
    notes: Optional[str] = None

class IntakeHistoryResponse(BaseModel):
    id: int
    medication_id: int
    scheduled_time: datetime
    taken_time: Optional[datetime]
    status: str
    notes: Optional[str]

    class Config:
        from_attributes = True