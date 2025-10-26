from pydantic import BaseModel


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
