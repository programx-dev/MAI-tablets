from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String, BigInteger, Text, Date, Time,
    Integer, CheckConstraint, ARRAY, ForeignKey
)
from typing import List, Optional
from app.db.base import Base


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    form: Mapped[str] = mapped_column(Text, nullable=False)  # 'tablet', 'drop', 'spray', 'other'
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)

    schedule_type: Mapped[str] = mapped_column(Text, nullable=False)  # 'daily', 'weekly_days', 'every_x_days'
    week_days: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    interval_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    times_per_day: Mapped[List[Time]] = mapped_column(ARRAY(Time), nullable=False)

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
