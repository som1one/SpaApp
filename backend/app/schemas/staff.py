"""
Схемы для мастеров и их расписания
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import time
import enum


class DayOfWeek(int, enum.Enum):
    """Дни недели"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class StaffResponse(BaseModel):
    """Ответ с информацией о мастере"""
    id: int
    name: str
    surname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    specialization: Optional[str] = None
    photo_url: Optional[str] = None
    description: Optional[str] = None
    yclients_staff_id: Optional[int] = None
    is_active: bool
    order_index: int

    class Config:
        from_attributes = True


class StaffScheduleResponse(BaseModel):
    """Ответ с расписанием мастера"""
    id: int
    staff_id: int
    day_of_week: int  # 0-6 (понедельник-воскресенье)
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    break_start: Optional[str] = None  # HH:MM
    break_end: Optional[str] = None  # HH:MM
    is_active: bool

    class Config:
        from_attributes = True


class StaffServiceResponse(BaseModel):
    """Ответ с привязкой мастера к услуге"""
    id: int
    staff_id: int
    service_id: int
    is_active: bool

    class Config:
        from_attributes = True


class StaffCreate(BaseModel):
    """Создание мастера"""
    name: str
    surname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    specialization: Optional[str] = None
    photo_url: Optional[str] = None
    description: Optional[str] = None
    yclients_staff_id: Optional[int] = None
    is_active: bool = True
    order_index: int = 0


class StaffUpdate(BaseModel):
    """Обновление мастера"""
    name: Optional[str] = None
    surname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    specialization: Optional[str] = None
    photo_url: Optional[str] = None
    description: Optional[str] = None
    yclients_staff_id: Optional[int] = None
    is_active: Optional[bool] = None
    order_index: Optional[int] = None


class StaffScheduleCreate(BaseModel):
    """Создание расписания"""
    staff_id: int
    day_of_week: int = Field(..., ge=0, le=6, description="День недели от 0 (понедельник) до 6 (воскресенье)")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Время начала в формате HH:MM (например, 09:00)")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Время окончания в формате HH:MM (например, 18:00)")
    break_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$", description="Начало перерыва в формате HH:MM")
    break_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$", description="Конец перерыва в формате HH:MM")
    is_active: bool = True


class StaffScheduleUpdate(BaseModel):
    """Обновление расписания"""
    staff_id: Optional[int] = None
    day_of_week: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    break_start: Optional[str] = None
    break_end: Optional[str] = None
    is_active: Optional[bool] = None


class StaffServiceCreate(BaseModel):
    """Создание привязки мастера к услуге"""
    staff_id: int
    service_id: int
    is_active: bool = True


class StaffServiceUpdate(BaseModel):
    """Обновление привязки мастера к услуге"""
    staff_id: Optional[int] = None
    service_id: Optional[int] = None
    is_active: Optional[bool] = None


class StaffWithScheduleResponse(StaffResponse):
    """Мастер с расписанием и услугами"""
    schedules: List[StaffScheduleResponse] = []
    services: List[int] = []  # Список ID услуг

