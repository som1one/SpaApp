import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.apis.dependencies import admin_required, super_admin_required
from app.core.database import get_db
from app.models.notification_campaign import NotificationCampaign, NotificationStatus, NotificationChannel
from app.models.device_token import DeviceToken
from app.schemas.admin_notifications import (
    NotificationCreateRequest,
    NotificationListResponse,
    NotificationResponse,
)
from app.services.audit_service import AuditService
from app.services.fcm_client import FcmClient

router = APIRouter(prefix="/admin/notifications", tags=["Admin Notifications"])
logger = logging.getLogger(__name__)


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
    status_filter: Optional[NotificationStatus] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(NotificationCampaign).order_by(NotificationCampaign.created_at.desc())
    if status_filter:
        query = query.filter(NotificationCampaign.status == status_filter)

    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(item) for item in items],
        total=total,
    )


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    payload: NotificationCreateRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_required),
):
    campaign = NotificationCampaign(
        title=payload.title,
        message=payload.message,
        channel=payload.channel,
        audience=payload.audience,
        status=NotificationStatus.DRAFT,
        created_by_admin_id=admin.id,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="create_notification",
        entity="notification",
        entity_id=campaign.id,
        payload=payload.model_dump(mode='json'),
        request=http_request,
    )
    return NotificationResponse.model_validate(campaign)


@router.patch("/{campaign_id}", response_model=NotificationResponse)
async def update_notification_status(
    campaign_id: int,
    new_status: NotificationStatus,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_required),
):
    campaign = db.query(NotificationCampaign).filter(NotificationCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Кампания не найдена")

    campaign.status = new_status
    if new_status == NotificationStatus.SENT:
        from app.utils.timezone import moscow_now
        campaign.sent_at = campaign.sent_at or moscow_now()
        # Отправляем пуши только если канал включает push
        if campaign.channel in (NotificationChannel.PUSH, NotificationChannel.ALL):
            try:
                await _send_push_campaign(db, campaign)
            except Exception as e:
                logger.error(
                    "Failed to send push campaign",
                    extra={"campaign_id": campaign.id},
                    exc_info=True,
                )
                # Откатываем транзакцию, если отправка не удалась
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Не удалось отправить пуш-уведомления"
                ) from e
    try:
        db.commit()
        db.refresh(campaign)
    except Exception as e:
        db.rollback()
        logger.error(
            "Failed to commit campaign status update",
            extra={"campaign_id": campaign.id},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить статус кампании"
        ) from e

    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="update_notification",
        entity="notification",
        entity_id=campaign.id,
        payload={"status": new_status.value if hasattr(new_status, 'value') else str(new_status)},
        request=http_request,
    )
    return NotificationResponse.model_validate(campaign)


async def _send_push_campaign(db: Session, campaign: NotificationCampaign) -> None:
    """Выбор токенов и отправка кампании через FCM.

    Аудитории:
      - audience is None or 'all'  -> все активные устройства
      - 'vip'                      -> пользователи с loyalty_level >= 3
    """
    from app.models.user import User  # локальный импорт, чтобы избежать циклов

    query = db.query(DeviceToken.token).join(User, DeviceToken.user_id == User.id, isouter=True)
    query = query.filter(DeviceToken.is_active.is_(True))

    audience = (campaign.audience or "all").lower()
    if audience == "vip":
        query = query.filter(User.loyalty_level >= 3)

    tokens_query = query
    tokens = [row[0] for row in tokens_query.all()]
    tokens_count = len(tokens)
    
    logger.info(
        "Starting push campaign",
        extra={
            "campaign_id": campaign.id,
            "audience": audience,
            "tokens_count": tokens_count,
        }
    )
    
    if not tokens:
        logger.info("No device tokens for notification campaign", extra={"campaign_id": campaign.id})
        campaign.success_count = 0
        campaign.failure_count = 0
        return

    try:
        success, failure = await FcmClient.send_to_tokens(
            title=campaign.title,
            body=campaign.message,
            tokens=tokens,
            data={"campaign_id": str(campaign.id)},
        )
        logger.info(
            "Notification campaign completed",
            extra={
                "campaign_id": campaign.id,
                "tokens_count": tokens_count,
                "success": success,
                "failure": failure,
                "total_expected": tokens_count,
            }
        )
        
        # Проверяем, что количество успешных + неуспешных соответствует количеству токенов
        total_reported = success + failure
        if total_reported != tokens_count:
            logger.warning(
                "FCM result count mismatch",
                extra={
                    "campaign_id": campaign.id,
                    "tokens_count": tokens_count,
                    "reported_total": total_reported,
                    "success": success,
                    "failure": failure,
                }
            )
        
        campaign.success_count = success
        campaign.failure_count = failure
    except Exception as e:
        logger.error(
            "Failed to send notification campaign",
            extra={"campaign_id": campaign.id},
            exc_info=True,
        )
        campaign.failure_count = len(tokens)
        campaign.success_count = 0
        raise

