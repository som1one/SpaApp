"""
Админские API для управления кастомными блоками контента
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.apis.dependencies import admin_required
from app.core.database import get_db
from app.models.custom_content import ContentBlockType, CustomContentBlock
from app.schemas.custom_content import (
    CustomContentBlockResponse,
    CustomContentBlockCreate,
    CustomContentBlockUpdate,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin/custom-content", tags=["Admin Custom Content"])
logger = logging.getLogger(__name__)

SPA_THERAPY_SLOTS = {
    0: "Подарочные сертификаты",
    1: "Спа-меню",
    2: "Каталог товаров",
}


def _is_spa_therapy_type(value) -> bool:
    if isinstance(value, ContentBlockType):
        return value == ContentBlockType.SPA_THERAPY_FEATURE
    return value == ContentBlockType.SPA_THERAPY_FEATURE.value


def _normalize_spa_therapy_payload(
    db: Session,
    payload_data: dict,
    current_block_id: int | None = None,
) -> dict:
    """Защищает 3 фиксированные карточки SPA-терапии от удаления/переименования."""
    order_index = payload_data.get("order_index", 0)
    if order_index not in SPA_THERAPY_SLOTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Для SPA-терапии доступны только 3 слота: 0, 1 и 2.",
        )

    duplicate = (
        db.query(CustomContentBlock)
        .filter(
            CustomContentBlock.block_type == ContentBlockType.SPA_THERAPY_FEATURE,
            CustomContentBlock.order_index == order_index,
        )
        .first()
    )
    if duplicate and duplicate.id != current_block_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот слот SPA-терапии уже занят. Отредактируйте существующую карточку.",
        )

    payload_data["title"] = SPA_THERAPY_SLOTS[order_index]
    payload_data["is_active"] = True
    return payload_data


@router.get("", response_model=List[CustomContentBlockResponse])
async def list_custom_content_blocks(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Список всех кастомных блоков контента"""
    blocks = (
        db.query(CustomContentBlock)
        .order_by(CustomContentBlock.order_index.asc(), CustomContentBlock.id.asc())
        .all()
    )
    return [CustomContentBlockResponse.model_validate(block) for block in blocks]


@router.post("", response_model=CustomContentBlockResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_content_block(
    payload: CustomContentBlockCreate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Создать новый блок контента"""
    payload_data = payload.model_dump()
    if _is_spa_therapy_type(payload_data.get("block_type")):
        payload_data = _normalize_spa_therapy_payload(db, payload_data)

    block = CustomContentBlock(**payload_data)
    db.add(block)
    db.commit()
    db.refresh(block)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="create_custom_content_block",
        entity="custom_content_block",
        entity_id=block.id,
        payload=payload_data,
        request=http_request,
    )
    
    return CustomContentBlockResponse.model_validate(block)


@router.get("/{block_id}", response_model=CustomContentBlockResponse)
async def get_custom_content_block(
    block_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Получить блок контента по ID"""
    block = db.query(CustomContentBlock).filter(CustomContentBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Блок не найден")
    return CustomContentBlockResponse.model_validate(block)


@router.patch("/{block_id}", response_model=CustomContentBlockResponse)
async def update_custom_content_block(
    block_id: int,
    payload: CustomContentBlockUpdate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Обновить блок контента"""
    block = db.query(CustomContentBlock).filter(CustomContentBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Блок не найден")
    
    update_data = payload.model_dump(exclude_unset=True)
    is_spa_therapy_block = block.block_type == ContentBlockType.SPA_THERAPY_FEATURE

    if (
        is_spa_therapy_block
        and "block_type" in update_data
        and not _is_spa_therapy_type(update_data["block_type"])
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Фиксированную карточку SPA-терапии нельзя перевести в другой тип.",
        )

    next_block_type = update_data.get("block_type", block.block_type)
    if _is_spa_therapy_type(next_block_type):
        current_order = update_data.get("order_index", block.order_index)
        update_data = _normalize_spa_therapy_payload(
            db,
            {
                **update_data,
                "order_index": current_order,
            },
            current_block_id=block.id,
        )

    for field, value in update_data.items():
        setattr(block, field, value)
    
    db.commit()
    db.refresh(block)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="update_custom_content_block",
        entity="custom_content_block",
        entity_id=block.id,
        payload=update_data,
        request=http_request,
    )
    
    return CustomContentBlockResponse.model_validate(block)


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_content_block(
    block_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Удалить блок контента"""
    block = db.query(CustomContentBlock).filter(CustomContentBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Блок не найден")
    if block.block_type == ContentBlockType.SPA_THERAPY_FEATURE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Фиксированные карточки SPA-терапии нельзя удалять.",
        )
    
    db.delete(block)
    db.commit()
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="delete_custom_content_block",
        entity="custom_content_block",
        entity_id=block_id,
        request=http_request,
    )
