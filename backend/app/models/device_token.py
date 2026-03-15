from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class DevicePlatform:
  ANDROID = "android"
  IOS = "ios"


class DeviceToken(BaseModel):
  __tablename__ = "device_tokens"

  user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
  token = Column(String(512), nullable=False, unique=True, index=True)
  platform = Column(String(20), nullable=False)  # android / ios
  is_active = Column(Boolean, nullable=False, default=True)

  user = relationship("User", backref="device_tokens")


