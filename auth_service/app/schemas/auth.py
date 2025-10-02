from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    patient = "patient"
    guardian = "guardian"


class UserRegister(BaseModel):
    role: UserRole = Field(..., description="Role of user")


class UserResponse(BaseModel):
    uuid: str
    role: UserRole
    password: str
    created_at: datetime


class UserLogin(BaseModel):
    uuid: str
    password: str
    role: UserRole


class LoginResponse(BaseModel):
    success: bool
