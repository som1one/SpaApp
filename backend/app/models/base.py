"""
Базовый класс для всех моделей
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, func
from app.core.database import Base


class BaseModel(Base):
    """Абстрактная базовая модель с общими полями"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

