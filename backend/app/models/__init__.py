"""
Модели базы данных
"""
from app.models.base import BaseModel
from app.models.user import User
from app.models.verification_code import VerificationCode
from app.models.booking import Booking, BookingStatus
from app.models.service import Service, ServiceCategory
from app.models.admin import Admin, AdminInvite
from app.models.admin_audit import AdminAudit
from app.models.notification_campaign import NotificationCampaign, NotificationChannel, NotificationStatus
from app.models.device_token import DeviceToken
from app.models.loyalty import LoyaltyLevel, LoyaltyBonus
from app.models.staff import Staff, StaffSchedule, StaffService
from app.models.custom_content import CustomContentBlock, ContentBlockType

__all__ = [
    "BaseModel",
    "User",
    "VerificationCode",
    "Booking",
    "BookingStatus",
    "Service",
    "ServiceCategory",
    "Admin",
    "AdminInvite",
    "AdminAudit",
    "NotificationCampaign",
    "NotificationChannel",
    "NotificationStatus",
    "DeviceToken",
    "LoyaltyLevel",
    "LoyaltyBonus",
    "Staff",
    "StaffSchedule",
    "StaffService",
    "CustomContentBlock",
    "ContentBlockType",
]

