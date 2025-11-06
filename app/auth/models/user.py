import uuid as uuid_pkg
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base
from datetime import datetime
from typing import Optional
class User(Base):
    __tablename__ = "users"

    uuid: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        unique=True,
        index=True,
        default=lambda: str(uuid_pkg.uuid4())
    )
    username: Mapped[str] = mapped_column(String, unique=True)
    hash_password: Mapped[str] = mapped_column(String, nullable=False)

    relation_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.uuid"),
        nullable=True
    )


    last_synced_time: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )

    # FOR очистки: когда создан
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
