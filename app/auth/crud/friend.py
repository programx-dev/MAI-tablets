from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.auth.models.user import User

async def add_med_friend(db: AsyncSession, patient_id: int, friend_uuid: str) -> dict:
    # Найти мед-друга по uuid
    friend_user = await db.execute(select(User).where(User.uuid == friend_uuid))
    friend_user = friend_user.scalar_one_or_none()

    if not friend_user:
        return {"success": False, "message": "Med friend with this UUID does not exist"}

    # Проверить, не является ли уже кто-то другим пациентом этого мед-друга
    patient_check = await db.execute(select(User).where(User.relation_id == friend_user.id))
    existing_patient = patient_check.scalar_one_or_none()

    if existing_patient:
        return {
            "success": False,
            "message": "This med friend is already assigned to another patient. Remove that relationship first."
        }

    # Проверить, не пытается ли пользователь добавить **себя** как мед-друга
    if friend_user.id == patient_id:
        return {"success": False, "message": "You cannot add yourself as a med friend"}

    # Получить текущего пациента
    patient = await db.get(User, patient_id)
    if patient is None:  # defensive check
        return {"success": False, "message": "Patient not found"}

    # Проверить, есть ли уже у пациента мед-друг
    if patient.relation_id is not None:
        return {
            "success": False,
            "message": "Patient already has a med friend. Remove that relationship first."
        }

    patient.relation_id = friend_user.id
    await db.commit()
    return {"success": True, "message": "Med friend added successfully"}

async def remove_med_friend(db: AsyncSession, patient_id: int):
    patient = await db.get(User, patient_id)
    if patient is None:  # defensive check
        return {"success": False, "message": "Patient not found"}
    if patient.relation_id is not None:
        patient.relation_id = None
        await db.commit()
        return {"success": True, "message": "Med friend removed successfully"}
    else:
        return {"success": True, "message": "No med friend was assigned to remove"}

async def get_med_friend(db: AsyncSession, patient_id: int):
    patient = await db.get(User, patient_id)
    if patient is None:  # defensive check
        return {"uuid": None, "message": "Patient not found"}
    if patient.relation_id is not None:
        friend = await db.get(User, patient.relation_id)
        if friend is None:  # defensive check
            return {"uuid": None, "message": "Med friend not found in database"}
        return {"uuid": friend.uuid, "message": None}
    else:
        return {"uuid": None, "message": "No med friend assigned"}

async def get_patient(db: AsyncSession, friend_uuid: str):
    # Найти пользователя с таким uuid
    friend_user = await db.execute(select(User).where(User.uuid == friend_uuid))
    friend_user = friend_user.scalar_one_or_none()

    if not friend_user:
        return {"uuid": None, "message": "Med friend UUID not found"}

    # Найти пациента, у которого relation_id == id мед-друга
    stmt = select(User).where(User.relation_id == friend_user.id)
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()

    if patient:
        return {"uuid": patient.uuid, "message": None}
    else:
        return {"uuid": None, "message": "No patient assigned to this med friend"}