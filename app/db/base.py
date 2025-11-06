from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Импорт моделей — обязателен!
from app.auth.models.user import User
from app.medicines.models.medication import Medication
from app.medicines.models.intake import IntakeHistory
