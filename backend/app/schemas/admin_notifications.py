from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.notification_campaign import NotificationChannel, NotificationStatus


class NotificationCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=1)  # Уменьшено с 5 до 1 для более гибкой валидации
    channel: NotificationChannel = NotificationChannel.ALL
    audience: Optional[str] = None


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    channel: NotificationChannel
    audience: Optional[str]
    status: NotificationStatus
    sent_at: Optional[datetime]
    success_count: Optional[int]
    failure_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int

