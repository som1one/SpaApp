from sqlalchemy import Column, String, Integer, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AdminAudit(BaseModel):
    __tablename__ = "admin_audit"

    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)
    payload = Column(JSON, nullable=True)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(64), nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    admin = relationship("Admin")

