from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Text, DateTime, CheckConstraint, ForeignKey
from app.db.base import Base
from typing import Optional

class IntakeHistory(Base):
    __tablename__ = "intake_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    medication_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("medications.id", ondelete="CASCADE"), nullable=False)
    scheduled_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False) # timestamp when it was scheduled
    taken_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False) # actual time when taken
    status: Mapped[str] = mapped_column(Text, nullable=False) # 'taken', 'skipped'
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(status.in_(['taken', 'skipped']), name='valid_status'),
    )