from typing import Any, Dict, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.admin_audit import AdminAudit


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        *,
        admin_id: int,
        action: str,
        entity: Optional[str] = None,
        entity_id: Optional[int] = None,
        payload: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> None:
        user_agent = request.headers.get("User-Agent") if request else None
        ip_address = request.client.host if request and request.client else None

        audit = AdminAudit(
            admin_id=admin_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            payload=payload,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db.add(audit)
        db.commit()

