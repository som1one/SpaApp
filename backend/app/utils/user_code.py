"""Утилиты для работы с уникальным кодом пользователя."""
import secrets

from sqlalchemy.orm import Session

from app.models.user import User


def generate_unique_user_code(db: Session, attempts: int = 20) -> str:
    """Сгенерировать уникальный код пользователя."""
    for _ in range(attempts):
        candidate = secrets.token_urlsafe(6)[:8].upper().replace("-", "").replace("_", "")
        exists = db.query(User.id).filter(User.unique_code == candidate).first()
        if not exists:
            return candidate
    raise RuntimeError("Не удалось сгенерировать уникальный код пользователя")


def ensure_user_unique_code(db: Session, user: User) -> bool:
    """
    Гарантировать наличие unique_code у пользователя.

    Возвращает True, если код был создан.
    """
    if user.unique_code:
        return False
    user.unique_code = generate_unique_user_code(db)
    return True
