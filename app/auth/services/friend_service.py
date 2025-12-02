# app/auth/services/friend_service.py

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models.user import User
from app.auth.crud import invitation as crud_invitation
from app.auth.crud import friend as crud_friend

class FriendServiceError(Exception):
    """Кастомное исключение для ошибок в сервисе."""
    pass

async def add_friend_by_code(db: AsyncSession, patient: User, code: str) -> None:
    """
    Бизнес-логика добавления мед-друга по коду-приглашению.
    Выбрасывает FriendServiceError в случае ошибки.
    """
    invitation = await crud_invitation.get_invitation_by_code_db(db, code)

    if not invitation:
        raise FriendServiceError("Неверный код-приглашение.")

    if invitation.expires_at < datetime.now(timezone.utc):
        await crud_invitation.delete_invitation_code_db(db, invitation.id)
        raise FriendServiceError("Срок действия кода-приглашения истек.")

    if invitation.is_used:
        raise FriendServiceError("Этот код-приглашение уже был использован.")
    
    med_friend_id = invitation.med_friend_id

    if med_friend_id == patient.uuid: 
        raise FriendServiceError("Вы не можете добавить себя в качестве мед-друга.")
    
    if patient.relation_id is not None:
        raise FriendServiceError("У вас уже есть мед-друг. Сначала удалите текущего.")

    if await crud_friend.get_patient_by_friend_id(db, med_friend_id):
        raise FriendServiceError("Этот мед-друг уже закреплен за другим пациентом.")

    await crud_friend.update_patient_relation(db, patient, med_friend_id)
    invitation.is_used = True
    await db.commit() 

async def remove_friend_for_patient(db: AsyncSession, patient: User) -> None:
    """Пациент удаляет своего мед-друга."""
    if patient.relation_id is None:
        raise FriendServiceError("У вас нет назначенного мед-друга.")
    await crud_friend.update_patient_relation(db, patient, None)

async def unsubscribe_from_patient(db: AsyncSession, med_friend: User) -> None:
    """Мед-друг отписывается от своего пациента."""
    patient = await crud_friend.get_patient_by_friend_id(db, med_friend.uuid)  
    if not patient:
        raise FriendServiceError("Вы не привязаны ни к одному пациенту.")
    await crud_friend.update_patient_relation(db, patient, None)
    
async def get_med_friend_info(db: AsyncSession, patient: User) -> dict[str, str | None]:
    """Готовит данные о мед-друге для ответа API."""
    if not patient.relation_id:
        return {"uuid": None, "username": None, "message": "Мед-друг не назначен."}
    
    friend = await db.get(User, patient.relation_id)
    
    if friend:
        return {"uuid": friend.uuid, "username": friend.username, "message": None}
    else:
        return {"uuid": None, "username": None, "message": "Назначенный мед-друг не найден в системе."}

async def get_patient_info_for_friend(db: AsyncSession, med_friend: User) -> dict[str, str | None]:
    """Готовит данные о пациенте для ответа API."""
    patient = await crud_friend.get_patient_by_friend_id(db, med_friend.uuid) 
    if patient:
        return {"uuid": patient.uuid, "username": patient.username, "message": None}
    else:
        return {"uuid": None, "username": None, "message": "Пациент не назначен."}