from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class AdminAuditResponse(BaseModel):
    id: int
    admin_id: int
    action: str
    entity: Optional[str]
    entity_id: Optional[int]
    payload: Optional[dict]
    user_agent: Optional[str]
    ip_address: Optional[str]
    executed_at: datetime

    class Config:
        from_attributes = True


class AdminAuditListResponse(BaseModel):
    items: List[AdminAuditResponse]
    total: int

