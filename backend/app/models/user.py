"""
Модель пользователя
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """Модель пользователя"""
    __tablename__ = "users"
    
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    loyalty_bonuses = Column(Integer, default=0, nullable=False)  # Количество бонусов лояльности
    spent_bonuses = Column(Integer, default=0, nullable=False)  # Количество потраченных бонусов
    loyalty_level_id = Column(Integer, ForeignKey("loyalty_levels.id"), nullable=True)  # Текущий уровень
    auto_apply_loyalty_points = Column(Boolean, default=False, nullable=False)
    unique_code = Column(String(20), unique=True, index=True, nullable=True)  # Уникальный код для привязки записей из YClients
    
    loyalty_level_obj = relationship("LoyaltyLevel", foreign_keys=[loyalty_level_id])
    
    def __repr__(self):
        return f"<User {self.email}>"

