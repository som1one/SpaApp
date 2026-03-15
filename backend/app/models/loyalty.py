"""
Модели для программы лояльности
"""
from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class LoyaltyLevel(BaseModel):
    """Уровень лояльности"""
    __tablename__ = "loyalty_levels"
    
    name = Column(String(100), nullable=False, unique=True)
    min_bonuses = Column(Integer, nullable=False)  # Минимальное количество бонусов для уровня
    cashback_percent = Column(Integer, nullable=False)  # Процент кэшбэка (1 уровень - 3%, 2 - 5%, 3 - 7%, 4 - 10%)
    color_start = Column(String(7), nullable=False)  # HEX цвет начала градиента
    color_end = Column(String(7), nullable=False)    # HEX цвет конца градиента
    icon = Column(String(50), default="eco", nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    bonuses = relationship(
        "LoyaltyBonus",
        foreign_keys="[LoyaltyBonus.level_id]",
        back_populates="level",
        cascade="all, delete-orphan",
        primaryjoin="LoyaltyLevel.id == LoyaltyBonus.level_id"
    )
    
    def __repr__(self):
        return f"<LoyaltyLevel {self.name}>"


class LoyaltyBonus(BaseModel):
    """Бонус программы лояльности"""
    __tablename__ = "loyalty_bonuses"
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), default="card_giftcard", nullable=False)
    level_id = Column(Integer, ForeignKey("loyalty_levels.id"), nullable=True)
    min_level_id = Column(Integer, ForeignKey("loyalty_levels.id"), nullable=True)  # Минимальный уровень для получения
    is_active = Column(Boolean, default=True, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    
    level = relationship("LoyaltyLevel", foreign_keys=[level_id], back_populates="bonuses")
    min_level = relationship("LoyaltyLevel", foreign_keys=[min_level_id])
    
    def __repr__(self):
        return f"<LoyaltyBonus {self.title}>"

