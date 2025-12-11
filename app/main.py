import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения
    """
    print("🚀 Запуск приложения...")
    
    # Инициализация базы данных (если метод существует)
    # УБРАЛИ: await db_helper.init_db() - заменили на проверку подключения
    try:
        # Проверяем, есть ли метод init_db
        if hasattr(db_helper, 'init_db'):
            await db_helper.init_db()
            print("✅ База данных инициализирована")
        else:
            # Просто проверяем подключение к БД
            from sqlalchemy import text
            async with db_helper.session() as session:
                await session.execute(text("SELECT 1"))
            print("✅ Подключение к базе данных установлено")
    except Exception as e:
        print(f"⚠️ Предупреждение при подключении к БД: {e}")
    
    # Запуск планировщика задач
    scheduler.add_job(
        cleanup_old_data,
        "interval",
        days=1,
        id="daily_cleanup",
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=1),
    )
    scheduler.start()
    print("✅ Планировщик задач запущен: daily_cleanup (ежедневно)")
    
    yield  # Приложение работает здесь
    
    # Остановка приложения
    print("🛑 Остановка приложения...")
    scheduler.shutdown()
    print("✅ Планировщик задач остановлен")
    print("👋 Приложение остановлено")


# Создаем приложение FastAPI
app = FastAPI(
    title="МАИ Таблетки API",
    description="API для мобильного приложения управления лекарствами",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ==================== CORS НАСТРОЙКИ ====================
# Критически важно для мобильных приложений!

# Разрешенные источники (origins)
ALLOWED_ORIGINS = [
    # Протоколы для Expo/React Native
    "exp://*",
    "http://localhost:*",
    "http://127.0.0.1:*",
    "http://192.168.*",  # Локальная сеть
    "http://10.0.2.2:*",  # Android эмулятор
    "capacitor://localhost",
    
    # Ваш VPS
    "http://158.160.68.214:*",
    "http://158.160.68.214",
    
    # Для разработки - разрешаем все (можно закомментировать в продакшене)
    "*",
]

# FastAPI CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # Разрешаем куки/авторизацию
    allow_methods=["*"],  # Разрешаем все HTTP методы
    allow_headers=["*"],  # Разрешаем все заголовки
    expose_headers=["*"],  # Делаем все заголовки видимыми для клиента
    max_age=600,  # Кешировать preflight запросы на 10 минут
)


# ==================== ОБРАБОТКА OPTIONS ЗАПРОСОВ ====================
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    """
    Middleware для обработки CORS заголовков
    """
    # Обработка OPTIONS (preflight) запросов
    if request.method == "OPTIONS":
        response = JSONResponse(
            content={"message": "Preflight OK"},
            status_code=200
        )
    else:
        response = await call_next(request)
    
    # Добавляем CORS заголовки
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response


# ==================== ПОДКЛЮЧЕНИЕ РОУТЕРОВ ====================
app.include_router(auth_router, prefix="/api/v1", tags=["Аутентификация"])
app.include_router(friend_router, prefix="/api/v1", tags=["Друзья"])
app.include_router(medication_router, prefix="/api/v1", tags=["Лекарства"])
app.include_router(intake_router, prefix="/api/v1", tags=["Прием лекарств"])
app.include_router(sync_router, prefix="/api/v1", tags=["Синхронизация"])


# ==================== ОСНОВНЫЕ ENDPOINTS ====================
@app.get("/", tags=["Информация"])
async def read_root():
    """
    Корневой endpoint для проверки работы API
    """
    return {
        "message": "Добро пожаловать в API МАИ Таблетки!",
        "version": "1.0.0",
        "docs": "/docs",
        "health_check": "/health",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health", tags=["Здоровье"])
async def health_check():
    """
    Health check endpoint для мониторинга
    """
    try:
        # Проверка подключения к БД
        from sqlalchemy import text
        async with db_helper.session() as session:
            await session.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "mai-pills-api",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "cors_enabled": True,
            "allowed_origins": ALLOWED_ORIGINS[:3]  # Показываем только первые 3
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )


@app.get("/test", tags=["Тестирование"])
async def test_endpoint(request: Request):
    """
    Endpoint для тестирования CORS и проверки подключения
    """
    client_ip = request.client.host if request.client else "unknown"
    
    return {
        "status": "success",
        "message": "API работает корректно!",
        "client_ip": client_ip,
        "user_agent": request.headers.get("user-agent", "unknown"),
        "origin": request.headers.get("origin", "not specified"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cors_test": {
            "allowed_origins": ALLOWED_ORIGINS,
            "note": "Если вы видите это сообщение, CORS настроен правильно"
        }
    }


# ==================== ОБРАБОТЧИКИ ОШИБОК ====================
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Обработчик HTTP исключений
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Обработчик ошибок валидации
    """
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "path": request.url.path,
            "method": request.method,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Глобальный обработчик исключений
    """
    import traceback
    print(f"❌ Необработанная ошибка: {exc}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "error": str(exc),
            "path": request.url.path,
            "method": request.method,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# ==================== ЗАПУСК СЕРВЕРА ====================
if __name__ == "__main__":
    # Параметры запуска
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print("=" * 50)
    print(f"🚀 Запуск сервера МАИ Таблетки")
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"🌐 CORS Origins: {ALLOWED_ORIGINS}")
    print("=" * 50)
    
    # Запуск сервера
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )
