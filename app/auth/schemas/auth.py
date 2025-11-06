from datetime import datetime
from pydantic import BaseModel, field_validator
from zoneinfo import ZoneInfo


class UserCreateResponse(BaseModel):
    uuid: str
    password: str

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    uuid: str
    password: str


class UserLoginResponse(BaseModel):
    success: bool
    uuid: str
    username: str  
    last_synced_time: datetime | None  # 

    class Config:
        from_attributes = True