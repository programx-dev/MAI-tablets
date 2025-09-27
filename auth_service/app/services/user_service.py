from uuid import UUID
from app.schemas.auth import UserResponse, UserRole

def create_user():
    user = UserResponse(
        uuid=UUID("123e4567-e89b-12d3-a456-426614174000"),
        pswd="my_secure_password",
        role=UserRole.patient,
    )
    
    return user