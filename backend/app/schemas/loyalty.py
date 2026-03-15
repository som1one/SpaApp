"""
Схемы для программы лояльности
"""
from pydantic import BaseModel
from typing import Optional, List


class LoyaltyLevelResponse(BaseModel):
    id: int
    name: str
    min_bonuses: int  # Минимальное количество бонусов для уровня
    cashback_percent: int  # Процент кэшбэка (только для чтения)
    color_start: str
    color_end: str
    icon: str
    order_index: int
    is_active: bool

    class Config:
        from_attributes = True


class LoyaltyBonusResponse(BaseModel):
    id: int
    title: str
    description: str
    icon: str
    min_level_id: Optional[int] = None
    order_index: int

    class Config:
        from_attributes = True


class LoyaltyInfoResponse(BaseModel):
    """Информация о лояльности пользователя"""
    current_bonuses: int  # Текущее количество бонусов
    spent_bonuses: int  # Потраченные бонусы
    current_level: Optional[LoyaltyLevelResponse] = None
    next_level: Optional[LoyaltyLevelResponse] = None
    bonuses_to_next: int  # Бонусов до следующего уровня
    progress: float  # 0.0 - 1.0
    available_bonuses: List[LoyaltyBonusResponse] = []
    levels: List[LoyaltyLevelResponse] = []  # Все активные уровни


class LoyaltyLevelCreate(BaseModel):
    name: str
    min_bonuses: int  # Минимальное количество бонусов для уровня
    cashback_percent: int  # Процент кэшбэка для уровня
    color_start: str
    color_end: str
    icon: str = "eco"
    order_index: int = 0
    is_active: bool = True


class LoyaltyLevelUpdate(BaseModel):
    name: Optional[str] = None
    min_bonuses: Optional[int] = None  # Минимальное количество бонусов для уровня
    cashback_percent: Optional[int] = None
    color_start: Optional[str] = None
    color_end: Optional[str] = None
    icon: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class LoyaltyBonusCreate(BaseModel):
    title: str
    description: str
    icon: str = "card_giftcard"
    level_id: Optional[int] = None
    min_level_id: Optional[int] = None
    order_index: int = 0


class LoyaltyBonusUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    level_id: Optional[int] = None
    min_level_id: Optional[int] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None

