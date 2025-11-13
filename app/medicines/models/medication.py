# app/medicines/models/medication.py
from datetime import date, time, datetime
from typing import List, Optional
from sqlalchemy import (
    String, BigInteger, Text, Date, Time,
    Integer, CheckConstraint, ARRAY, ForeignKey, TIMESTAMP
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func  # <-- Убедитесь, что этот импорт есть
from app.db.base import Base


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    patient_id: Mapped[str] = mapped_column(String, ForeignKey("users.uuid"), nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    form: Mapped[str] = mapped_column(Text, nullable=False)  # 'tablet', 'drop', ...
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    schedule_type: Mapped[str] = mapped_column(Text, nullable=False)  # 'daily', ...
    week_days: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    interval_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    times_per_day: Mapped[List[time]] = mapped_column(ARRAY(Time), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    # ✅ Добавляем updated_at
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()  # <-- Это ключевое: обновляется при UPDATE
    )

    __table_args__ = (
        CheckConstraint(
            "form IN ('tablet', 'drop', 'spray', 'other')",
            name="valid_form"
        ),
        CheckConstraint(
            "schedule_type IN ('daily', 'weekly_days', 'every_x_days')",
            name="valid_schedule_type"
        ),
    )