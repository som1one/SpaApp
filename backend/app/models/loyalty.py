"""
Модели для программы лояльности
"""
from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey, DateTime
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


class LoyaltyProgramSettings(BaseModel):
    """Постоянные настройки программы лояльности"""
    __tablename__ = "loyalty_program_settings"

    loyalty_enabled = Column(Boolean, default=True, nullable=False)
    points_per_100_rub = Column(Integer, default=5, nullable=False)
    welcome_bonus_amount = Column(Integer, default=0, nullable=False)
    bonus_expiry_days = Column(Integer, default=30, nullable=False)
    yclients_bonus_field_id = Column(String(100), nullable=True)

    def __repr__(self):
        return (
            "<LoyaltyProgramSettings "
            f"enabled={self.loyalty_enabled} "
            f"points_per_100_rub={self.points_per_100_rub}>"
        )


class LoyaltyTransaction(BaseModel):
    """История операций по бонусам"""
    __tablename__ = "loyalty_transactions"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True, index=True)
    source_transaction_id = Column(
        Integer,
        ForeignKey("loyalty_transactions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    amount = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False, index=True)
    status = Column(String(30), default="active", nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    expired_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="loyalty_transactions")
    booking = relationship("Booking", backref="loyalty_transactions")
    source_transaction = relationship("LoyaltyTransaction", remote_side="LoyaltyTransaction.id")

    def __repr__(self):
        return (
            f"<LoyaltyTransaction user_id={self.user_id} "
            f"type={self.transaction_type} amount={self.amount}>"
        )
