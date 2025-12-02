# app/auth/models/invitation.py

import datetime
import uuid as uuid_pkg
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, TIMESTAMP
from app.db.base import Base


class InvitationCode(Base):
    __tablename__ = "invitation_codes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid_pkg.uuid4()) 
    )
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    med_friend_id: Mapped[str] = mapped_column(String, ForeignKey("users.uuid"), nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)