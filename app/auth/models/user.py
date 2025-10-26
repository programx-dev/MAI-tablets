import uuid as uuid_pkg
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey
from app.auth.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(String, unique=True, index=True, default=lambda: str(uuid_pkg.uuid4()))
    hash_password: Mapped[str] = mapped_column(String, nullable=False)
    relation_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
