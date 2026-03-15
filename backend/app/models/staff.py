"""
Модели для мастеров и их расписания
"""
from sqlalchemy import Column, String, Integer, Boolean, Time, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class DayOfWeek(enum.IntEnum):
    """Дни недели"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Staff(BaseModel):
    """Модель мастера"""
    __tablename__ = "staff"
    
    name = Column(String(200), nullable=False)
    surname = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    specialization = Column(String(500), nullable=True)  # Специализация (массаж, SPA, косметология и т.д.)
    photo_url = Column(String(500), nullable=True)
    description = Column(String(1000), nullable=True)  # Описание мастера
    yclients_staff_id = Column(Integer, nullable=True, unique=True)  # ID мастера в YClients (если синхронизирован)
    is_active = Column(Boolean, default=True, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    
    # Связи
    schedules = relationship("StaffSchedule", back_populates="staff", cascade="all, delete-orphan")
    service_assignments = relationship("StaffService", back_populates="staff", cascade="all, delete-orphan")
    
    def __repr__(self):
        full_name = f"{self.name} {self.surname or ''}".strip()
        return f"<Staff {full_name}>"


class StaffSchedule(BaseModel):
    """Расписание работы мастера"""
    __tablename__ = "staff_schedules"
    
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # День недели (0-6, Monday-Sunday)
    start_time = Column(Time, nullable=False)  # Время начала работы (например, 09:00)
    end_time = Column(Time, nullable=False)  # Время окончания работы (например, 18:00)
    break_start = Column(Time, nullable=True)  # Начало обеденного перерыва (опционально)
    break_end = Column(Time, nullable=True)  # Конец обеденного перерыва (опционально)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Связи
    staff = relationship("Staff", back_populates="schedules")
    
    def __repr__(self):
        return f"<StaffSchedule staff_id={self.staff_id} day={self.day_of_week.name}>"


class StaffService(BaseModel):
    """Привязка мастера к услуге (какие услуги может выполнять мастер)"""
    __tablename__ = "staff_services"
    
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Связи
    staff = relationship("Staff", back_populates="service_assignments")
    
    def __repr__(self):
        return f"<StaffService staff_id={self.staff_id} service_id={self.service_id}>"

