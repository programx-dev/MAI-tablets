from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Text, Date, Time, Integer, CheckConstraint, ARRAY, ForeignKey
from app.db.base import Base
from typing import List, Optional

class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    form: Mapped[str] = mapped_column(Text, nullable=False)  # 'tablet', 'drop', 'spray', 'other'
    instructions: Mapped[str] = mapped_column(Text, nullable=True)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date] = mapped_column(Date, nullable=True)
    schedule_type: Mapped[str] = mapped_column(Text, nullable=False)  # 'daily', 'weekly_days', 'every_x_days'
    week_days: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=True) # [1, 3, 5] for Mon, Wed, Fri
    interval_days: Mapped[int] = mapped_column(Integer, nullable=True) # e.g., 3 for every 3 days
    times_per_day: Mapped[List[Time]] = mapped_column(ARRAY(Time), nullable=False) # ['08:00', '14:30']

    __table_args__ = (
        CheckConstraint(form.in_(['tablet', 'drop', 'spray', 'other']), name='valid_form'),
        CheckConstraint(schedule_type.in_(['daily', 'weekly_days', 'every_x_days']), name='valid_schedule_type'),
    )