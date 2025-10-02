# Auth Service

Микросервис авторизации для проекта.  
Реализует регистрацию и аутентификацию пользователей с использованием **FastAPI**, **SQLAlchemy 2.0 (async)** и **Pydantic v2**.

---

## 🚀 Возможности

- **Регистрация пользователя**:
  - Клиент указывает только `role` (`patient` или `guardian`);
  - Сервис сам генерирует `uuid` и случайный пароль;
  - Возвращает пользователю `{uuid, role, password, created_at}`;
  - В БД сохраняется `{id, uuid, role, hash_password, created_at}`.

- **Авторизация пользователя**:
  - Получает `uuid`, `password`, `role`;
  - Проверяет пароль;
  - Возвращает `{success: true/false}`.

---

## 🛠️ Стек технологий

- [FastAPI](https://fastapi.tiangolo.com/) (async роутеры)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) (async ORM)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Passlib](https://passlib.readthedocs.io/en/stable/) (bcrypt)
- [SQLite + aiosqlite](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#asyncio)

---

## 📂 Структура проекта

```bash
auth_service/
├── app/
│ ├── main.py # FastAPI приложение (запуск через uvicorn.run)
│ ├── api/
│ │ └── auth.py # роуты: /auth/register, /auth/login
│ ├── core/
│ │ └── config.py # конфигурация (DATABASE_URL)
│ ├── db/
│ │ ├── base.py # DeclarativeBase()
│ │ └── session.py # Async engine, sessionmaker
│ ├── models/
│ │ └── user.py # ORM модель User
│ ├── schemas/
│ │ └── auth.py # Pydantic-схемы
│ ├── crud/
│ │ └── user.py # CRUD-операции для User
│ └── utils/
│ └── password.py # hash / verify
```

---

## ⚙️ Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/yourname/auth_service.git
cd auth_service
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install poetry

poetry install
```

3. Установить зависимости

4. Запустить сервис

```bash
python app/main.py
```

Приложение поднимется на: http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs

## 📌 Примеры API-запросов

### 1. Регистрация

POST `/auth/register`

Request:
```json
{
  "role": "patient"
}
```

Response:
```json
{
  "uuid": "c1d3d62a-02c4-4f2c-bc44-65d9fbf98e32",
  "role": "patient",
  "password": "NnCwQYx9lDk",
  "created_at": "2025-10-02T19:30:12.123456"
}
```

2. Авторизация

POST `/auth/login`

Request:
```
{
  "uuid": "c1d3d62a-02c4-4f2c-bc44-65d9fbf98e32",
  "password": "NnCwQYx9lDk",
  "role": "patient"
}
```

Response:
```
{
  "success": true
}
```