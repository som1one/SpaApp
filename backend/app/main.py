"""
Главный файл приложения FastAPI
"""
import logging
import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from contextlib import asynccontextmanager
from datetime import datetime

# Rate limiting и фоновые задачи YClients временно отключены для упрощения отладки
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.admin_service import AdminService
from app.api.v1.router import api_router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("Инициализация FastAPI приложения")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Упрощённый lifecycle: не трогаем БД и внешние сервисы на старте,
    # чтобы запуск и /health работали даже при упавшей БД или YClients.
    logger.info("Запуск приложения (lifespan старт)")

    # Настраиваем APScheduler для автоматической синхронизации YClients
    # Синхронизация записей отключена - записи не сохраняются в БД

    yield

    logger.info("Остановка приложения (lifespan shutdown)")


app = FastAPI(
    title="SPA Salon API",
    description="API для мобильного приложения SPA салона",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.debug_mode,
)

# CORS настройки для работы с Flutter приложением и админкой
cors_origins = settings.cors_origins_list
# Если есть wildcard в development, используем его
if not settings.is_production and "*" in cors_origins:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,  # Кэширование preflight запросов на 1 час
)

uploads_path = (project_root / settings.UPLOAD_DIR).resolve()
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации с детальным логированием"""
    # Пытаемся получить тело запроса, но обрабатываем случай, когда клиент отключился
    body_str = None
    try:
        body = await request.body()
        body_str = body.decode('utf-8') if body else None
    except Exception as e:
        # Клиент отключился или произошла другая ошибка при чтении тела
        logger.warning(f"Не удалось прочитать тело запроса: {e}")
    
    logger.error(f"Ошибка валидации для {request.method} {request.url.path}")
    logger.error(f"Детали ошибки: {exc.errors()}")
    if body_str:
        logger.error(f"Тело запроса: {body_str}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": body_str,
        },
    )


@app.get("/")
async def root():
    """Проверка доступности сервера"""
    logger.info("Обработан запрос GET /")
    return {
        "status": "ok",
        "message": "SPA Salon API is running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Обработан запрос GET /health")
    from app.utils.timezone import moscow_now
    return {
        "status": "healthy",
        "timestamp": moscow_now().isoformat(),
    }

