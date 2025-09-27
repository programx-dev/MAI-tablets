from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timezone
from enum import Enum


class UserRole(str, Enum):
    '''Перечисление возможных ролей пользователеей'''
    patient = "patient"
    guardian = "guardian"

 
class UserResponse(BaseModel):
    '''Схема для выдачи информации о зарегистрированном пользователе'''
    uuid: UUID
    pswd: str
    role: UserRole
    created_at: datetime = datetime.now(timezone.utc)


class UserLogin(BaseModel):
    '''Схема для входа (логина) пользователя'''
    uuid: UUID
    pswd: str
    role: UserRole
