from datetime import datetime
from pydantic import BaseModel


class FriendBase(BaseModel):
    uuid: str


class FriendAdd(FriendBase):
    """Добавление мед-друга по его UUID"""
    pass


class FriendResponse(BaseModel):
    uuid: str
    created_at: datetime
