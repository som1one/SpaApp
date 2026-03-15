"""
Схемы для кастомных блоков контента
"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ContentBlockTypeEnum(str, Enum):
    """Типы блоков контента"""
    SPA_TRAVEL = "spa_travel"
    PROMOTION = "promotion"
    BANNER = "banner"
    CUSTOM = "custom"


class CustomContentBlockResponse(BaseModel):
    """Ответ с информацией о блоке контента"""
    id: int
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    block_type: str
    order_index: int
    is_active: bool
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    gradient_start: Optional[str] = None
    gradient_end: Optional[str] = None

    class Config:
        from_attributes = True


class CustomContentBlockCreate(BaseModel):
    """Создание нового блока контента"""
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    block_type: ContentBlockTypeEnum = ContentBlockTypeEnum.CUSTOM
    order_index: int = 0
    is_active: bool = True
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    gradient_start: Optional[str] = None
    gradient_end: Optional[str] = None


class CustomContentBlockUpdate(BaseModel):
    """Обновление блока контента"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    block_type: Optional[ContentBlockTypeEnum] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    gradient_start: Optional[str] = None
    gradient_end: Optional[str] = None

