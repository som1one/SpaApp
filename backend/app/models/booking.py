"""
Модель записи на прием
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import BaseModel


class BookingStatus(enum.Enum):
    """Статусы записи"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(BaseModel):
    """Модель записи на прием"""
    __tablename__ = "bookings"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    service_name = Column(String(200), nullable=False)  # Название услуги
    service_duration = Column(Integer, nullable=True)  # Длительность в минутах
    service_price = Column(Integer, nullable=True)  # Цена услуги в копейках
    appointment_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)  # Дополнительные заметки
    phone = Column(String(20), nullable=True)  # Контактный телефон
    cancelled_at = Column(DateTime(timezone=True), nullable=True)  # Дата отмены
    cancelled_reason = Column(Text, nullable=True)  # Причина отмены
    # Лояльность
    loyalty_bonuses_awarded = Column(Boolean, nullable=False, default=False)
    loyalty_bonuses_amount = Column(Integer, nullable=True)  # Сколько бонусов начислено за эту запись
    
    # Связь с пользователем
    user = relationship("User", backref="bookings")
    
    def __repr__(self):
        return f"<Booking {self.id} - {self.service_name} at {self.appointment_datetime}>"

