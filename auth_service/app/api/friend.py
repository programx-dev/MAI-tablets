from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import db_helper
from app.models.user import User
from app.core.security import get_current_user
from app.crud.friend import add_med_friend, remove_med_friend, get_med_friends, get_patients_for_friend
from app.crud.user import get_user_by_uuid
from app.schemas.friend import FriendAdd, FriendResponse

router = APIRouter(prefix="/friends", tags=["friends"])


@router.post("/add", response_model=FriendResponse)
async def add_friend(
    data: FriendAdd,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Добавить мед-друга по UUID"""
    friend = await get_user_by_uuid(db, data.uuid)
    if not friend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    relation = await add_med_friend(db, current_user.id, friend.id)
    return FriendResponse(uuid=friend.uuid, created_at=relation.created_at)


@router.delete("/remove/{friend_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(
    friend_uuid: str,
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Удалить мед-друга"""
    friend = await get_user_by_uuid(db, friend_uuid)
    if not friend:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    await remove_med_friend(db, current_user.id, friend.id)
    return


@router.get("/list_med_friends")
async def list_my_med_friends(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Список всех моих мед-друзей"""
    friends = await get_med_friends(db, current_user.id)
    return [{"uuid": f.uuid, "created_at": f.created_at} for f in friends]


@router.get("/list_patients")
async def list_patients(
    db: AsyncSession = Depends(db_helper.session_dependency),
    current_user: User = Depends(get_current_user),
):
    """Список всех пациентов, у которых я являюсь мед-другом"""
    patients = await get_patients_for_friend(db, current_user.id)
    return [{"uuid": p.uuid, "created_at": p.created_at} for p in patients]
