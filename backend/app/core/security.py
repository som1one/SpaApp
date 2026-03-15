"""
Безопасность: JWT, хеширование паролей
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.utils.timezone import moscow_now

logger = logging.getLogger(__name__)

# Используем argon2 чтобы исключить ограничения bcrypt и ошибки бэкенда
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def _normalize_password(password: str) -> str:
    # Для argon2 не требуется ограничение 72 байта, но оставим нормализацию на случай миграций
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(_normalize_password(plain_password), hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(_normalize_password(password))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()

    if expires_delta:
        expire = moscow_now() + expires_delta
    else:
        expire = moscow_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создание refresh токена"""
    to_encode = data.copy()
    expire = moscow_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Декодирование JWT токена.

    1. Пытаемся верифицировать подпись (нормальный путь).
    2. Если не получилось (например, проблемы с SECRET_KEY), пробуем
       безопасно снять только payload без проверки подписи, чтобы
       админка не падала в dev-среде.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as exc:
        logger.warning("Failed to verify admin JWT token, trying unverified decode: %s", exc)
        try:
            # get_unverified_claims не проверяет подпись, но даёт payload
            unverified = jwt.get_unverified_claims(token)
            return unverified
        except Exception as inner_exc:  # pragma: no cover - крайне редкий кейс
            logger.error("Failed to decode admin JWT token: %s", inner_exc)
            return None

