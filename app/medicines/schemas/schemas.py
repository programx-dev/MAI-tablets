from pydantic import BaseModel, field_validator
from datetime import date, time, datetime
from typing import List, Optional
from zoneinfo import ZoneInfo


def ensure_utc(v):
    if v is None:
        return v
    if isinstance(v, str):
        v = datetime.fromisoformat(v)
    if v.tzinfo is None:
        v = v.replace(tzinfo=ZoneInfo("UTC"))
    return v.astimezone(ZoneInfo("UTC"))


class MedicationCreateRequest(BaseModel):
    name: str
    form: Optional[str] = None
    instructions: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    schedule_type: str 
    week_days: Optional[List[int]] = None 
    interval_days: Optional[int] = None 
    times_per_day: List[time]

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


class IntakeHistoryCreateRequest(BaseModel):
    medication_id: int
    scheduled_time: datetime
    taken_time: Optional[datetime] = None
    status: str
    notes: Optional[str] = None

    @field_validator("scheduled_time", "taken_time", mode="before")
    @classmethod
    def validate_time(cls, v):
        return ensure_utc(v)

class IntakeHistoryUpdateRequest(BaseModel):
    taken_time: Optional[datetime] = None
    status: Optional[str] = None 
    notes: Optional[str] = None

class IntakeHistoryResponse(BaseModel):
    id: int
    medication_id: int
    scheduled_time: datetime
    taken_time: datetime
    status: str
    notes: Optional[str]

    class Config:
        from_attributes = True