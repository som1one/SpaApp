"""
Публичные API для получения кастомных блоков контента
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.custom_content import CustomContentBlock
from app.schemas.custom_content import CustomContentBlockResponse

router = APIRouter(prefix="/custom-content", tags=["Custom Content"])


@router.get("", response_model=List[CustomContentBlockResponse])
async def get_custom_content_blocks(
    db: Session = Depends(get_db),
):
    """Получить все активные кастомные блоки контента для главного экрана"""
    blocks = (
        db.query(CustomContentBlock)
        .filter(CustomContentBlock.is_active == True)
        .order_by(CustomContentBlock.order_index.asc(), CustomContentBlock.id.asc())
        .all()
    )
    return [CustomContentBlockResponse.model_validate(block) for block in blocks]

