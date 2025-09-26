FROM python:3.13-slim

WORKDIR /app

# Копируем зависимости
COPY pyproject.toml poetry.lock* ./

# Устанавливаем Poetry и зависимости
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Копируем весь проект
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
