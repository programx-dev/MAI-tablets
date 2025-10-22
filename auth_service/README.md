# Auth Service
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

## Alembic

```bash
alembic revision --autogenerate -m ""
```

```bash
alembic upgrade head
```

```bash
alembic downgrade -1
```
