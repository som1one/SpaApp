"""
Pydantic схемы для записей на прием
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class BookingStatusEnum(str, Enum):
    """Статусы записи"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingCreate(BaseModel):
    """Схема для создания записи"""
    service_name: str = Field(..., min_length=1, max_length=200)
    service_duration: Optional[int] = Field(None, ge=0)  # Длительность в минутах
    service_price: Optional[int] = Field(None, ge=0)  # Цена в копейках
    appointment_datetime: datetime
    notes: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)

    @validator('appointment_datetime')
    def validate_future_datetime(cls, v):
        """Проверка, что дата в будущем"""
        from app.utils.timezone import moscow_now
        if v <= moscow_now():
            raise ValueError('Дата записи должна быть в будущем')
        return v


class BookingUpdate(BaseModel):
    """Схема для обновления записи"""
    service_name: Optional[str] = Field(None, min_length=1, max_length=200)
    service_duration: Optional[int] = Field(None, ge=0)
    service_price: Optional[int] = Field(None, ge=0)
    appointment_datetime: Optional[datetime] = None
    status: Optional[BookingStatusEnum] = None
    notes: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    cancelled_reason: Optional[str] = None

    @validator('appointment_datetime')
    def validate_future_datetime(cls, v):
        """Проверка, что дата в будущем"""
        from app.utils.timezone import moscow_now
        if v is not None and v <= moscow_now():
            raise ValueError('Дата записи должна быть в будущем')
        return v


class BookingResponse(BaseModel):
    """Схема ответа с записью"""
    id: int
    user_id: int
    service_name: str
    service_duration: Optional[int]
    service_price: Optional[int]
    appointment_datetime: datetime
    status: str
    notes: Optional[str]
    phone: Optional[str]
    cancelled_at: Optional[datetime]
    cancelled_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

