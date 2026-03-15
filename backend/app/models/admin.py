from enum import Enum

from sqlalchemy import Column, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"


class Admin(BaseModel):
    __tablename__ = "admins"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default=AdminRole.ADMIN.value)
    is_active = Column(Boolean, default=True, nullable=False)
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)


class AdminInvite(BaseModel):
    __tablename__ = "admin_invites"

    email = Column(String(255), nullable=False, unique=True)
    token = Column(String(64), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted = Column(Boolean, default=False, nullable=False)
    role = Column(String(50), nullable=False, default=AdminRole.ADMIN.value)
    invited_by_admin_id = Column(ForeignKey("admins.id"), nullable=True)

    invited_by = relationship("Admin", foreign_keys=[invited_by_admin_id])


