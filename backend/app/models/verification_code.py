"""
Модель кода верификации
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from app.models.base import BaseModel


class VerificationCode(BaseModel):
    """Модель кода верификации email"""
    __tablename__ = "verification_codes"
    
    email = Column(String(255), index=True, nullable=False)
    code = Column(String(6), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    def __repr__(self):
        return f"<VerificationCode {self.email}>"

