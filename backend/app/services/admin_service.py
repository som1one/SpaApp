import secrets
import logging
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.admin import Admin, AdminInvite, AdminRole
from app.utils.timezone import moscow_now

logger = logging.getLogger(__name__)


class AdminService:
    @staticmethod
    def create_super_admin_if_missing(db: Session):
        if not settings.SUPER_ADMIN_EMAIL or not settings.SUPER_ADMIN_PASSWORD:
            return
        exists = db.query(Admin).filter(Admin.role == AdminRole.SUPER_ADMIN.value).first()
        if not exists:
            admin = Admin(
                email=settings.SUPER_ADMIN_EMAIL,
                password_hash=get_password_hash(settings.SUPER_ADMIN_PASSWORD),
                role=AdminRole.SUPER_ADMIN.value,
                is_active=True,
            )
            db.add(admin)
            db.commit()

    @staticmethod
    def create_invite(
        db: Session,
        email: str,
        role: str = AdminRole.ADMIN.value,
        invited_by: Admin | None = None,
    ) -> AdminInvite:
        if role not in (AdminRole.ADMIN.value, AdminRole.SUPER_ADMIN.value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Некорректная роль")
        if role == AdminRole.SUPER_ADMIN.value and invited_by and invited_by.role != AdminRole.SUPER_ADMIN.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав для роли")

        # Проверяем, не существует ли уже админ с таким email
        existing_admin = db.query(Admin).filter(Admin.email == email).first()
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Администратор с email {email} уже существует"
            )

        token = secrets.token_hex(32)
        expires_at = moscow_now() + timedelta(minutes=settings.ADMIN_INVITE_EXPIRATION_MINUTES)
        
        # Проверяем, есть ли уже приглашение для этого email
        invite = db.query(AdminInvite).filter(AdminInvite.email == email).first()
        if not invite:
            invite = AdminInvite(email=email)
            db.add(invite)
        else:
            # Если приглашение уже принято, не позволяем создать новое
            if invite.accepted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Приглашение для {email} уже было принято"
                )

        invite.token = token
        invite.expires_at = expires_at
        invite.accepted = False
        invite.role = role
        invite.invited_by_admin_id = invited_by.id if invited_by else None

        try:
            db.commit()
            db.refresh(invite)
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Ошибка создания приглашения: {e}", exc_info=True)
            # Проверяем, какое именно ограничение нарушено
            error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'email' in error_str.lower() or 'unique' in error_str.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Приглашение для {email} уже существует"
                )
            elif 'token' in error_str.lower():
                # Если токен дублируется (крайне маловероятно), генерируем новый
                logger.warning("Дубликат токена, генерируем новый")
                invite.token = secrets.token_hex(32)
                db.commit()
                db.refresh(invite)
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Ошибка создания приглашения"
                )
        except Exception as e:
            db.rollback()
            logger.error(f"Неожиданная ошибка при создании приглашения: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка создания приглашения"
            )
        
        return invite

    @staticmethod
    def accept_invite(db: Session, token: str, password: str) -> tuple[Admin, str]:
        invite = (
            db.query(AdminInvite)
            .filter(AdminInvite.token == token, AdminInvite.accepted == False)
            .first()
        )
        if not invite:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Приглашение не найдено")
        
        if invite.expires_at < moscow_now():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Приглашение истекло")

        admin = db.query(Admin).filter(Admin.email == invite.email).first()
        if not admin:
            admin = Admin(email=invite.email, role=invite.role, is_active=True)
            db.add(admin)
        else:
            # Если админ уже существует, проверяем, не принято ли уже приглашение
            if invite.accepted:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Приглашение уже было принято")

        admin.role = invite.role
        admin.password_hash = get_password_hash(password)
        admin.is_active = True
        invite.accepted = True
        
        try:
            db.commit()
            db.refresh(admin)
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Ошибка при принятии приглашения: {e}", exc_info=True)
            error_str = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'email' in error_str.lower() or 'unique' in error_str.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Администратор с email {invite.email} уже существует"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при принятии приглашения"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Неожиданная ошибка при принятии приглашения: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при принятии приглашения"
            )

        token_value = create_access_token({"sub": admin.id, "role": admin.role, "scope": "admin"})
        return admin, token_value

    @staticmethod
    def login(db: Session, email: str, password: str) -> str:
        admin = db.query(Admin).filter(Admin.email == email, Admin.is_active == True).first()
        if not admin or not admin.password_hash or not verify_password(password, admin.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

        token = create_access_token({"sub": admin.id, "role": admin.role, "scope": "admin"})
        admin.last_login_at = moscow_now()
        db.commit()
        return token

    @staticmethod
    def get_current_admin(db: Session, admin_id: int) -> Admin:
        admin = db.query(Admin).filter(Admin.id == admin_id, Admin.is_active == True).first()
        if not admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован")
        return admin

    @staticmethod
    def list_invites(db: Session) -> list[AdminInvite]:
        return db.query(AdminInvite).order_by(AdminInvite.created_at.desc()).all()

    @staticmethod
    def get_invite_by_token(db: Session, token: str) -> AdminInvite | None:
        return db.query(AdminInvite).filter(AdminInvite.token == token).first()

    @staticmethod
    def invite_status(invite: AdminInvite) -> str:
        if invite.accepted:
            return "accepted"
        if invite.expires_at < moscow_now():
            return "expired"
        return "active"


