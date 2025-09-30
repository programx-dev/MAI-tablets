from .base import Base
from sqlalchemy.orm import Mapped


class User(Base):
    __tablename__ = "users"

    name: Mapped[str]
    uuid: Mapped[str]
    hash_psw: Mapped[str]
