from fastapi import APIRouter
from app.schemas.auth import UserLogin
from app.services.user_service import create_user


router = APIRouter(tags=['Auth'])


@router.post('/register')
def register():
    user = create_user()
    
    return user


@router.post('/login/')
def login(creds: UserLogin):
    return {
        'success': True,
        'token': 'fuqy3tr3tr87t3dqb:4irt34irtdbxiq3',
    }
    