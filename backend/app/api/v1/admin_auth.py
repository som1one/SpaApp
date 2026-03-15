import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.apis.dependencies import admin_required, super_admin_required
from app.core.config import settings
from app.core.database import get_db
from app.schemas.admin import (
    AdminInviteRequest,
    AdminInviteResponse,
    AdminInviteListResponse,
    AdminInvitePublicResponse,
    AdminAcceptInviteRequest,
    AdminAcceptInviteResponse,
    AdminLoginRequest,
    AdminProfile,
)
from app.services.admin_service import AdminService
from app.services.audit_service import AuditService
from app.models.admin import AdminInvite
from app.utils.email import send_admin_invite_email

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])
logger = logging.getLogger(__name__)


def _serialize_invite(invite: AdminInvite) -> AdminInviteResponse:
    status_value = AdminService.invite_status(invite)
    return AdminInviteResponse(
        email=invite.email,
        role=invite.role,
        token=invite.token,
        status=status_value,
        expires_at=invite.expires_at,
        accepted=invite.accepted,
        invited_by_email=getattr(invite.invited_by, "email", None),
        created_at=invite.created_at,
    )


@router.post("/invite", response_model=AdminInviteResponse)
async def invite_admin(
    request: AdminInviteRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    db: Session = Depends(get_db),
    current_admin=Depends(super_admin_required),
):
    try:
        invite = AdminService.create_invite(db, request.email, request.role, current_admin)
        logger.info("Создано приглашение администратора", extra={"email": request.email})
        invite_link = f"{settings.ADMIN_PANEL_BASE_URL.rstrip('/')}/invite/{invite.token}"
        background_tasks.add_task(
            send_admin_invite_email,
            invite.email,
            invite_link,
            invite.role,
            getattr(current_admin, "email", None),
        )
        AuditService.log_action(
            db,
            admin_id=current_admin.id,
            action="invite_admin",
            entity="admin",
            entity_id=invite.id,
            payload={"email": request.email, "role": request.role},
            request=http_request,
        )
        return _serialize_invite(invite)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании приглашения: {e}", exc_info=True, extra={"email": request.email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания приглашения: {str(e)}"
        )


@router.get("/invites", response_model=AdminInviteListResponse)
async def list_invites(
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(super_admin_required),
):
    invites = AdminService.list_invites(db)
    return AdminInviteListResponse(invites=[_serialize_invite(inv) for inv in invites])


@router.get("/invite/{token}", response_model=AdminInvitePublicResponse)
async def get_invite_by_token(token: str, db: Session = Depends(get_db)):
    invite = AdminService.get_invite_by_token(db, token)
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Приглашение не найдено")
    status_value = AdminService.invite_status(invite)
    return AdminInvitePublicResponse(
        email=invite.email,
        role=invite.role,
        status=status_value,
        expires_at=invite.expires_at,
    )


@router.post("/accept", response_model=AdminAcceptInviteResponse)
async def accept_invite(request: AdminAcceptInviteRequest, db: Session = Depends(get_db)):
    try:
        admin, token = AdminService.accept_invite(db, request.token, request.password)
        logger.info("Администратор активирован", extra={"email": admin.email})
        profile = AdminProfile(id=admin.id, email=admin.email, role=admin.role, is_active=admin.is_active)
        return AdminAcceptInviteResponse(access_token=token, profile=profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при принятии приглашения: {e}", exc_info=True, extra={"token": request.token[:20] + "..."})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка принятия приглашения: {str(e)}"
        )


@router.post("/login")
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    try:
        token = AdminService.login(db, request.email, request.password)
        logger.info("Администратор вошёл", extra={"email": request.email})
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ошибка входа администратора", extra={"email": request.email, "error": str(e)}, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при входе"
        )


@router.get("/me", response_model=AdminProfile)
async def admin_me(admin=Depends(admin_required)):
    return AdminProfile(
        id=admin.id,
        email=admin.email,
        role=admin.role,
        is_active=admin.is_active,
    )


