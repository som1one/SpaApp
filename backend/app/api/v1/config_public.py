"""
Публичные эндпоинты конфигурации (без секретов).
Используются для проверки настройки окружения (в т.ч. FCM) по API.
"""
from fastapi import APIRouter

from app.services.fcm_client import is_fcm_configured

router = APIRouter(prefix="/config", tags=["Config"])


@router.get("/push")
async def get_push_config():
    """
    Статус настройки push (FCM).
    Возвращает только флаг наличия ключа, без самого ключа.
    """
    fcm_configured = is_fcm_configured()
    return {
        "fcm_configured": fcm_configured,
        "message": (
            "FCM настроен, рассылки доступны"
            if fcm_configured
            else "Задайте FCM v1 (FCM_PROJECT_ID + GOOGLE_APPLICATION_CREDENTIALS или FCM_CREDENTIALS_JSON) или FCM_SERVER_KEY в .env (см. backend/ENV_SETUP.md)"
        ),
    }
