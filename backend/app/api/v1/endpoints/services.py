"""
API endpoints для услуг
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from decimal import Decimal
import logging

from app.models.service import Service
from app.schemas.service import ServiceResponse

router = APIRouter(prefix="/services", tags=["Services"])
logger = logging.getLogger(__name__)


def _serialize(service: Service) -> ServiceResponse:
    """Безопасная сериализация услуги с обработкой всех типов данных"""
    try:
        return ServiceResponse(
            id=service.id,
            name=service.name,
            subtitle=service.subtitle,
            description=service.description,
            price=float(service.price) if isinstance(service.price, Decimal) else service.price,
            duration=service.duration,
            category=service.category,
            category_id=service.category_id,
            image_url=service.image_url,
            detail_image_url=service.detail_image_url,
            additional_services=service.additional_services,
            highlights=service.highlights,
            contact_link=service.contact_link,
            contact_label=service.contact_label,
            book_button_label=service.book_button_label,
            order_index=service.order_index,
            is_active=bool(service.is_active),
            created_at=service.created_at.isoformat() if service.created_at else None,
            updated_at=service.updated_at.isoformat() if service.updated_at else None,
            yclients_service_id=service.yclients_service_id,
            yclients_staff_id=service.yclients_staff_id,
        )
    except Exception as e:
        logger.error(f"Ошибка сериализации услуги {service.id}: {str(e)}")
        raise


@router.get("", response_model=List[ServiceResponse])
async def get_services(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получить список услуг"""
    query = db.query(Service).filter(Service.is_active == True)
    
    if category:
        query = query.filter(Service.category == category)
    
    services = query.offset(skip).limit(limit).all()
    
    return [_serialize(service) for service in services]


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """Получить услугу по ID"""
    logger.info(f"Запрос услуги с ID: {service_id}")
    
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.is_active == True
    ).first()
    
    if not service:
        logger.warning(f"Услуга с ID {service_id} не найдена или неактивна")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    logger.info(f"Услуга найдена: {service.name}")
    
    try:
        result = _serialize(service)
        logger.info(f"Услуга успешно сериализована")
        return result
    except Exception as e:
        logger.error(f"Ошибка при сериализации услуги {service_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обработки данных услуги: {str(e)}"
        )

