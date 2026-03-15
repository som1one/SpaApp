"""
Модели меню и услуг
"""
from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    Numeric,
    Boolean,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ServiceCategory(BaseModel):
    """Категория/подкатегория услуг"""

    __tablename__ = "service_categories"

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    parent_id = Column(ForeignKey("service_categories.id"), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)

    parent = relationship("ServiceCategory", remote_side="ServiceCategory.id", backref="children")
    services = relationship("Service", back_populates="category_rel")

    def __repr__(self):
        return f"<ServiceCategory {self.name}>"


class Service(BaseModel):
    """Модель услуги SPA"""

    __tablename__ = "services"

    name = Column(String(200), nullable=False)
    subtitle = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)  # Цена в рублях
    duration = Column(Integer, nullable=True)  # Длительность в минутах
    category = Column(String(100), nullable=True)  # DEPRECATED строковое имя категории
    category_id = Column(ForeignKey("service_categories.id"), nullable=True)
    image_url = Column(String(500), nullable=True)
    detail_image_url = Column(String(500), nullable=True)
    additional_services = Column(JSON, nullable=True)
    highlights = Column(JSON, nullable=True)
    contact_link = Column(String(500), nullable=True)
    contact_label = Column(String(100), nullable=True)
    book_button_label = Column(String(100), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    yclients_service_id = Column(Integer, nullable=True)  # ID услуги в YClients
    yclients_staff_id = Column(Integer, nullable=True)  # ID мастера в YClients (опционально)

    category_rel = relationship("ServiceCategory", back_populates="services")

    def __repr__(self):
        return f"<Service {self.name}>"

