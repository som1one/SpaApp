import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.apis.dependencies import super_admin_required
from app.core.database import get_db
from app.models.admin_audit import AdminAudit
from app.schemas.admin_audit import AdminAuditListResponse, AdminAuditResponse

router = APIRouter(prefix="/admin/audit", tags=["Admin Audit"])
logger = logging.getLogger(__name__)


@router.get("", response_model=AdminAuditListResponse)
async def list_audit(
    db: Session = Depends(get_db),
    _: dict = Depends(super_admin_required),
    action: Optional[str] = Query(None),
    admin_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(AdminAudit).order_by(AdminAudit.executed_at.desc())
    if action:
        query = query.filter(AdminAudit.action == action)
    if admin_id:
        query = query.filter(AdminAudit.admin_id == admin_id)

    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return AdminAuditListResponse(
        items=[AdminAuditResponse.model_validate(item) for item in items],
        total=total,
    )

