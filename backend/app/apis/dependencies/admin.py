import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.admin import Admin, AdminRole
from app.services.admin_service import AdminService

admin_security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


async def admin_required(
    credentials: HTTPAuthorizationCredentials = Depends(admin_security),
    db: Session = Depends(get_db),
):
    """Проверка токена администратора.

    Более «живучая» версия:
    - принимает любой валидный JWT с scope=admin (или без scope в dev);
    - аккуратно приводит sub к int;
    - даёт понятные логи, если что-то не так.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")

    payload = decode_token(credentials.credentials)
    if not payload:
        logger.warning("Admin token decode failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")

    scope = payload.get("scope")
    if scope not in (None, "admin"):
        logger.warning("Admin token has invalid scope: %s", scope)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")

    admin_id_raw = payload.get("sub")
    try:
        admin_id = int(admin_id_raw)
    except (TypeError, ValueError):
        logger.warning("Admin token has invalid sub: %r", admin_id_raw)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")

    admin = AdminService.get_current_admin(db, admin_id)
    return admin


async def super_admin_required(admin: Admin = Depends(admin_required)):
    if admin.role != AdminRole.SUPER_ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    return admin


