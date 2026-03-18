import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.apis.dependencies import admin_required, super_admin_required
from app.core.database import get_db
from app.models.notification_campaign import (
    NotificationCampaign,
    NotificationCategory,
    NotificationChannel,
    NotificationStatus,
)
from app.schemas.admin_notifications import (
    NotificationCreateRequest,
    NotificationListResponse,
    NotificationResponse,
)
from app.services.audit_service import AuditService
from app.services.notification_campaign_service import (
    normalize_scheduled_at_to_utc,
    process_due_scheduled_campaigns,
    send_push_campaign,
)

router = APIRouter(prefix="/admin/notifications", tags=["Admin Notifications"])
logger = logging.getLogger(__name__)


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
    status_filter: Optional[NotificationStatus] = Query(None),
    category_filter: Optional[NotificationCategory] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    await process_due_scheduled_campaigns(db)

    query = db.query(NotificationCampaign).order_by(NotificationCampaign.created_at.desc())
    if status_filter:
        query = query.filter(NotificationCampaign.status == status_filter)
    if category_filter:
        query = query.filter(NotificationCampaign.category == category_filter)

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
    scheduled_at = normalize_scheduled_at_to_utc(payload.scheduled_at)
    initial_status = NotificationStatus.SCHEDULED if scheduled_at else NotificationStatus.DRAFT

    campaign = NotificationCampaign(
        title=payload.title,
        message=payload.message,
        category=payload.category,
        channel=payload.channel,
        audience=payload.audience,
        status=initial_status,
        scheduled_at=scheduled_at,
        created_by_admin_id=admin.id,
    )
    db.add(campaign)
    db.commit()

    # Если время уже наступило — отправим в рамках этого же запроса.
    if campaign.status == NotificationStatus.SCHEDULED:
        await process_due_scheduled_campaigns(db)

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

    if new_status == NotificationStatus.SCHEDULED and not campaign.scheduled_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя запланировать кампанию без даты и времени",
        )

    campaign.status = new_status
    if new_status == NotificationStatus.SENT:
        campaign.sent_at = campaign.sent_at or datetime.now(timezone.utc)
        campaign.scheduled_at = None
        # Отправляем пуши только если канал включает push
        if campaign.channel in (NotificationChannel.PUSH, NotificationChannel.ALL):
            try:
                await send_push_campaign(db, campaign)
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
