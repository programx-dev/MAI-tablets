import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.session import db_helper
from app.auth.models.base import Base


from app.auth.api.auth import router as auth_router
from app.auth.api.friend import router as friend_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # создаём таблицы при старте
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # можно добавить логику при завершении


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(friend_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
