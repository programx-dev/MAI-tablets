from pydantic import BaseModel

class FriendAdd(BaseModel):
    uuid: str

class FriendAddResponse(BaseModel):
    success: bool
    message: str

class FriendGetResponse(BaseModel):
    uuid: str | None
    message: str | None = None

class PatientGetResponse(BaseModel):
    uuid: str | None
    message: str | None = None