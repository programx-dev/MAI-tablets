# app/medicines/models/intake.py
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func 
from app.db.base import Base


class IntakeHistory(Base):
    __tablename__ = "intake_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    medication_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medications.id", ondelete="CASCADE"),
        nullable=False
    )
    scheduled_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    taken_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)  # 'taken', 'skipped'
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )


    __table_args__ = (
        CheckConstraint("status IN ('taken', 'skipped')", name='valid_status'),
    )