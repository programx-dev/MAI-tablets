from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
import os

from app.db.base import Base

# Получаем URL из переменной окружения (обязательно!)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("Environment variable DATABASE_URL is required for Alembic")

config = context.config

# Настройка логгирования
if config.config_file_name:
    fileConfig(config.config_file_name)

# Устанавливаем URL в конфиг (для совместимости, хотя не используется напрямую)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Создаём асинхронный движок напрямую из DATABASE_URL
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,  # важно для Alembic — нет пула
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())