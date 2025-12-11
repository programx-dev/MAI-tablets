import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone, timedelta
import os

from app.db.session import db_helper
from app.core.scheduler import scheduler
from app.auth.tasks.cleanup_tasks import cleanup_old_data

from app.auth.api.auth import router as auth_router
from app.auth.api.friend import router as friend_router
from app.medicines.api.medication import router as medication_router
from app.medicines.api.intake import router as intake_router
from app.medicines.api.sync import router as sync_router


# ==================== LIFESPAN ====================
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения
    """
    print("🚀 Запуск приложения МАИ Таблетки...")
    
    # Запуск планировщика задач
    scheduler.add_job(
        cleanup_old_data,
        "interval",
        days=1,
        id="daily_cleanup",
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=1),
    )
    scheduler.start()
    print("✅ Планировщик задач запущен")
    
    yield
    
    # Остановка приложения
    print("🛑 Остановка приложения...")
    scheduler.shutdown()
    print("✅ Планировщик задач остановлен")


# ==================== СОЗДАНИЕ ПРИЛОЖЕНИЯ ====================
app = FastAPI(
    title="МАИ Таблетки API",
    description="API для мобильного приложения управления лекарствами",
    version="1.0.0",
    lifespan=lifespan
)


# ==================== CORS НАСТРОЙКИ ====================
# Разрешаем ВСЕ для тестирования
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)


# ==================== DEPENDENCIES ====================
async def get_db() -> AsyncSession:
    """
    Dependency для получения сессии БД
    """
    async with db_helper.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# ==================== ОСНОВНЫЕ ENDPOINTS ====================
@app.get("/")
async def root():
    """
    Корневой endpoint
    """
    return {
        "message": "🚀 API МАИ Таблетки работает!",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check с проверкой базы данных
    """
    try:
        # Проверяем подключение к БД
        result = await db.execute(text("SELECT 1"))
        db_status = "connected" if result.scalar() == 1 else "error"
        
        return {
            "status": "healthy",
            "database": db_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "mai-pills-api",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@app.get("/test")
async def test_endpoint(request: Request):
    """
    Endpoint для тестирования CORS
    """
    return {
        "status": "success",
        "message": "CORS работает!",
        "client_ip": request.client.host if request.client else "unknown",
        "origin": request.headers.get("origin", "not specified"),
        "user_agent": request.headers.get("user-agent", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cors_enabled": True
    }


@app.options("/{path:path}")
async def options_handler():
    """
    Обработчик OPTIONS запросов для CORS
    """
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )


# ==================== MIDDLEWARE ДЛЯ CORS ====================
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """
    Middleware для добавления CORS заголовков
    """
    # Обработка preflight запросов
    if request.method == "OPTIONS":
        response = JSONResponse(content={"message": "OK"})
    else:
        response = await call_next(request)
    
    # Добавляем CORS заголовки
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    return response


# ==================== ПОДКЛЮЧЕНИЕ РОУТЕРОВ ====================
# Добавляем зависимости к роутерам если они их используют
app.include_router(auth_router)
app.include_router(friend_router)
app.include_router(medication_router)
app.include_router(intake_router)
app.include_router(sync_router)


# ==================== ОБРАБОТЧИКИ ОШИБОК ====================
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"❌ Необработанная ошибка: {exc}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "error": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# ==================== ЗАПУСК СЕРВЕРА ====================
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Запуск сервера МАИ Таблетки")
    print(f"📡 Хост: {os.getenv('HOST', '0.0.0.0')}")
    print(f"🔌 Порт: {os.getenv('PORT', 8000)}")
    print(f"🌐 CORS: Разрешены все источники (*)")
    print(f"🗄️  DB URL: {os.getenv('DATABASE_URL', 'Не настроена')}")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level="info",
        access_log=True
    )
