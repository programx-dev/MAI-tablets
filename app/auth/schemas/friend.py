# app/auth/schemas/friend.py

from pydantic import BaseModel

class FriendAddByCode(BaseModel):
    code: str

class FriendActionResponse(BaseModel):
    success: bool
    message: str

class FriendGetResponse(BaseModel):
    uuid: str | None
    message: str | None = None

class PatientGetResponse(BaseModel):
    uuid: str | None
    message: str | None = None

class InvitationCodeGenerateResponse(BaseModel):
    code: str
    expires_in_seconds: int