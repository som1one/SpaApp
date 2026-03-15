"""
Модель для кастомных блоков контента на главном экране
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, Enum as SQLEnum
from app.models.base import BaseModel
import enum


class ContentBlockType(enum.Enum):
    """Типы блоков контента"""
    SPA_TRAVEL = "spa_travel"  # Spa-путешествия
    PROMOTION = "promotion"  # Акция
    BANNER = "banner"  # Баннер
    CUSTOM = "custom"  # Кастомный блок


class CustomContentBlock(BaseModel):
    """Кастомный блок контента для главного экрана"""
    __tablename__ = "custom_content_blocks"
    
    title = Column(String(200), nullable=False)  # Заголовок блока
    subtitle = Column(String(300), nullable=True)  # Подзаголовок
    description = Column(Text, nullable=True)  # Описание (может быть HTML)
    image_url = Column(String(500), nullable=True)  # URL изображения
    action_url = Column(String(500), nullable=True)  # URL для действия (ссылка)
    action_text = Column(String(100), nullable=True)  # Текст кнопки действия
    block_type = Column(SQLEnum(ContentBlockType), default=ContentBlockType.CUSTOM, nullable=False)  # Тип блока
    order_index = Column(Integer, default=0, nullable=False)  # Порядок отображения
    is_active = Column(Boolean, default=True, nullable=False)  # Активен ли блок
    background_color = Column(String(7), nullable=True)  # HEX цвет фона
    text_color = Column(String(7), nullable=True)  # HEX цвет текста
    gradient_start = Column(String(7), nullable=True)  # HEX цвет начала градиента
    gradient_end = Column(String(7), nullable=True)  # HEX цвет конца градиента
    
    def __repr__(self):
        return f"<CustomContentBlock {self.title}>"

