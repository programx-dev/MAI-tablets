import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # создаём таблицы при старте
    yield
    # можно добавить логику при завершении


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)