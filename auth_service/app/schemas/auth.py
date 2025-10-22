from pydantic import BaseModel
from datetime import datetime


class RegisterResponse(BaseModel):
    uuid: str
    password: str
    created_at: datetime


class UserLogin(BaseModel):
    uuid: str
    password: str


class LoginResponse(BaseModel):
    uuid: str
    created_at: datetime
