import uuid as uuid_pkg
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, func
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(
        String, unique=True, index=True, default=lambda: str(uuid_pkg.uuid4())
    )
    hash_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # для SQLite обязательно
        onupdate=func.now(),
        nullable=False,
    )

    # Пациент -> его мед-друзья
    friends = relationship(
        "UserRelation",
        foreign_keys="[UserRelation.user_id]",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Мед-друг -> его пациенты
    patients = relationship(
        "UserRelation",
        foreign_keys="[UserRelation.friend_id]",
        back_populates="friend",
        cascade="all, delete-orphan",
    )
