"""Конфигурация приложения
"""
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Admin invites
    ADMIN_INVITE_EXPIRATION_MINUTES: int = 30
    SUPER_ADMIN_EMAIL: str | None = None
    SUPER_ADMIN_PASSWORD: str | None = None
    ADMIN_PANEL_BASE_URL: str = "http://localhost:3001"
    # База данных
    # В development можно оставить дефолт, в production ОБЯЗАТЕЛЬНО переопределить через .env
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/spa_db"

    # Безопасность
    # В .env должен быть задан непустой и достаточно длинный SECRET_KEY
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email — вся конфигурация должна приходить из .env (см. env.template),
    # здесь только безопасные дефолты для локальной разработки.
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_USE_TLS: bool = True
    EMAIL_USE_SSL: bool = False
    # Пустое значение по умолчанию — чтобы письма шли на фактический адрес пользователя.
    EMAIL_DEBUG_RECIPIENT: str = ""
    
    # Приложение
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development, production
    DEBUG: bool = Field(default=True)
    
    @property
    def is_production(self) -> bool:
        """Проверка, что приложение в production режиме"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def debug_mode(self) -> bool:
        """Режим отладки (отключен в production)"""
        return self.DEBUG and not self.is_production
    
    # CORS (парсится из строки, разделенной запятыми)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080,*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Преобразует строку CORS_ORIGINS в список"""
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        # В development режиме разрешаем все источники
        if not self.is_production:
            if "*" in origins:
                return ["*"]
        # В production убираем wildcard
        elif "*" in origins:
            origins.remove("*")
        return origins
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Verification Code
    # Для продакшена рекомендуется значение 3–10 минут, см. env.template
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 10
    VERIFICATION_CODE_LENGTH: int = 6
    
    # Google OAuth
    # В production ОБЯЗАТЕЛЬНО задать GOOGLE_CLIENT_ID в .env
    GOOGLE_CLIENT_ID: str = ""
    
    # VK ID OAuth
    # В production ОБЯЗАТЕЛЬНО задать VK_APP_ID и VK_SECRET_KEY в .env
    VK_APP_ID: str = ""
    VK_SECRET_KEY: str = ""
    
    # YClients Booking Forms
    # URL формы для онлайн-записи (например: https://n239661.yclients.com)
    # Если не указан, будет использован стандартный виджет
    YCLIENTS_BOOKING_FORM_URL: str = ""
    # URL формы сети (опционально, если есть несколько филиалов)
    YCLIENTS_NETWORK_FORM_URL: str = ""
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    UPLOAD_DIR: str = "uploads"
    
    # Booking Settings
    MIN_BOOKING_ADVANCE_HOURS: int = 2
    MAX_BOOKING_ADVANCE_DAYS: int = 30
    CANCELLATION_HOURS_BEFORE: int = 24

    # Loyalty Program
    LOYALTY_ENABLED: bool = True
    # Сколько баллов начислять за каждые 100 рублей стоимости услуги
    LOYALTY_POINTS_PER_100_RUB: int = 5
    
    # Firebase / Push
    FCM_SERVER_KEY: str = ""
    FCM_API_URL: str = "https://fcm.googleapis.com/fcm/send"
    
    # YClients Integration
    # ВРЕМЕННО ОТКЛЮЧЕНО для тестирования остальной функциональности
    # Чтобы включить YClients: установите YCLIENTS_ENABLED=True в .env файле
    YCLIENTS_COMPANY_ID: int | None = None
    YCLIENTS_API_TOKEN: str = ""
    YCLIENTS_USER_TOKEN: str = ""
    YCLIENTS_ENABLED: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()

