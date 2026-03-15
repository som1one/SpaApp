from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, TypeDecorator
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class NotificationChannel(enum.Enum):
    PUSH = "push"
    EMAIL = "email"
    ALL = "all"


class NotificationStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    CANCELLED = "cancelled"


class EnumType(TypeDecorator):
    impl = String
    cache_ok = True

    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_class(value)


class NotificationCampaign(BaseModel):
    __tablename__ = "notification_campaigns"

    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(EnumType(NotificationChannel, 50), default=NotificationChannel.ALL, nullable=False)
    audience = Column(String(200), nullable=True)
    status = Column(EnumType(NotificationStatus, 50), default=NotificationStatus.DRAFT, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    success_count = Column(Integer, nullable=True)
    failure_count = Column(Integer, nullable=True)
    created_by_admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)

    created_by = relationship("Admin")

