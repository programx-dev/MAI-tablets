from pydantic import BaseModel
from datetime import datetime

class UserCreateRequest(BaseModel):
    username: str  # ← Добавьте это


class UserCreateResponse(BaseModel):
    uuid: str
    username: str
    password: str  # ⚠️ Возвращать пароль — плохо, но если так задумано...

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    uuid: str
    password: str


class UserLoginResponse(BaseModel):
    success: bool
    uuid: str
    username: str  # ✅ Добавьте, если возвращаете
    last_synced_time: datetime | None  # ✅ если добавляли

    class Config:
        from_attributes = True