import logging
from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.device_token import DeviceToken
from app.models.notification_campaign import NotificationCampaign, NotificationChannel, NotificationStatus
from app.services.fcm_client import FcmClient

logger = logging.getLogger(__name__)
KAMCHATKA_TZ = ZoneInfo("Asia/Kamchatka")


def normalize_scheduled_at_to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Интерпретирует вход как время Камчатки и возвращает UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KAMCHATKA_TZ)
    else:
        dt = dt.astimezone(KAMCHATKA_TZ)
    return dt.astimezone(timezone.utc)


async def send_push_campaign(db: Session, campaign: NotificationCampaign) -> None:
    """Отправить push-кампанию по аудитории."""
    from app.models.user import User  # локальный импорт, чтобы избежать циклов

    query = db.query(DeviceToken.token).join(User, DeviceToken.user_id == User.id, isouter=True)
    query = query.filter(DeviceToken.is_active.is_(True))

    audience = (campaign.audience or "all").lower()
    if audience == "vip":
        query = query.filter(User.loyalty_level_id.isnot(None)).filter(User.loyalty_level_id >= 3)

    tokens = [row[0] for row in query.all()]
    tokens_count = len(tokens)

    logger.info(
        "Starting push campaign",
        extra={"campaign_id": campaign.id, "audience": audience, "tokens_count": tokens_count},
    )

    if not tokens:
        campaign.success_count = 0
        campaign.failure_count = 0
        return

    success, failure = await FcmClient.send_to_tokens(
        title=campaign.title,
        body=campaign.message,
        tokens=tokens,
        data={"campaign_id": str(campaign.id)},
    )
    campaign.success_count = success
    campaign.failure_count = failure


async def process_due_scheduled_campaigns(db: Session) -> int:
    """Отправляет все запланированные кампании, чей срок уже наступил."""
    now_utc = datetime.now(timezone.utc)
    due_campaigns = (
        db.query(NotificationCampaign)
        .filter(NotificationCampaign.status == NotificationStatus.SCHEDULED)
        .filter(NotificationCampaign.scheduled_at.isnot(None))
        .filter(NotificationCampaign.scheduled_at <= now_utc)
        .order_by(NotificationCampaign.scheduled_at.asc())
        .all()
    )
    if not due_campaigns:
        return 0

    processed = 0
    for campaign in due_campaigns:
        try:
            if campaign.channel in (NotificationChannel.PUSH, NotificationChannel.ALL):
                await send_push_campaign(db, campaign)
            campaign.status = NotificationStatus.SENT
            campaign.sent_at = datetime.now(timezone.utc)
            db.commit()
            processed += 1
        except Exception:
            db.rollback()
            logger.error(
                "Failed to process scheduled campaign",
                extra={"campaign_id": campaign.id},
                exc_info=True,
            )
    return processed
