from pydantic import BaseModel
from datetime import datetime

class UserCreateRequest(BaseModel):
    username: str 


class UserCreateResponse(BaseModel):
    uuid: str
    username: str
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
    last_synced_time: datetime | None 

    class Config:
        from_attributes = True