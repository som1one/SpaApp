"""
Админские API для управления кастомными блоками контента
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.apis.dependencies import admin_required
from app.core.database import get_db
from app.models.custom_content import CustomContentBlock
from app.schemas.custom_content import (
    CustomContentBlockResponse,
    CustomContentBlockCreate,
    CustomContentBlockUpdate,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin/custom-content", tags=["Admin Custom Content"])
logger = logging.getLogger(__name__)


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
    block = CustomContentBlock(**payload.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="create_custom_content_block",
        entity="custom_content_block",
        entity_id=block.id,
        payload=payload.model_dump(),
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

