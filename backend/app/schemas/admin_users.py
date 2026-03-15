from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AdminUserResponse(BaseModel):
    id: int
    name: str
    surname: Optional[str]
    email: str
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    loyalty_level: Optional[int] = Field(None, alias="loyalty_level_id")
    loyalty_bonuses: Optional[int] = None
    spent_bonuses: Optional[int] = None
    unique_code: Optional[str] = None
    auto_apply_loyalty_points: bool = False
    created_at: datetime
    cashback_percent: Optional[int] = None  # Процент кэшбэка текущего уровня (для расчета начисления)

    class Config:
        from_attributes = True
        populate_by_name = True


class AdminUsersListResponse(BaseModel):
    items: List[AdminUserResponse]
    total: int

