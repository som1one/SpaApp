import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from sqlalchemy.orm import Session

from app.apis.dependencies import admin_required, super_admin_required
from app.core.database import get_db
from app.models.service import Service, ServiceCategory
from app.schemas.service import (
    MenuTreeItem,
    ServiceCategoryCreate,
    ServiceCategoryResponse,
    ServiceCategoryUpdate,
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
    CategoryReorderRequest,
    ServiceReorderRequest,
    ServicesBulkUpdateRequest,
)
from app.services.menu_service import MenuService
from app.services.storage_service import StorageService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin/menu", tags=["Admin Menu"])
logger = logging.getLogger(__name__)


@router.get("/tree", response_model=List[MenuTreeItem])
async def get_menu_tree(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    # В админке показываем все услуги, включая скрытые
    return MenuService.get_menu_tree(db, include_inactive=True)


@router.post("/categories", response_model=ServiceCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: ServiceCategoryCreate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_required),
):
    if payload.parent_id:
        parent = db.query(ServiceCategory).filter(ServiceCategory.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Родительская категория не найдена")

    category = ServiceCategory(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    MenuService.invalidate_cache()
    logger.info("Создана категория меню", extra={"category_id": category.id, "category_name": category.name})
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="create_category",
        entity="service_category",
        entity_id=category.id,
        payload=payload.model_dump(),
        request=http_request,
    )
    return ServiceCategoryResponse.model_validate(category)


@router.patch("/categories/{category_id}", response_model=ServiceCategoryResponse)
async def update_category(
    category_id: int,
    payload: ServiceCategoryUpdate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_required),
):
    category = db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    update_data = payload.model_dump(exclude_unset=True)
    if "parent_id" in update_data and update_data["parent_id"]:
        if update_data["parent_id"] == category.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Категория не может быть сама себе родителем")
        parent = db.query(ServiceCategory).filter(ServiceCategory.id == update_data["parent_id"]).first()
        if not parent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Родительская категория не найдена")

    for field, value in update_data.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    MenuService.invalidate_cache()
    logger.info("Категория обновлена", extra={"category_id": category.id})
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="update_category",
        entity="service_category",
        entity_id=category.id,
        payload=payload.model_dump(exclude_unset=True),
        request=http_request,
    )
    return ServiceCategoryResponse.model_validate(category)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_required),
):
    category = db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    if category.children:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Удалите подразделы перед удалением")
    if category.services:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="В категории есть услуги")

    db.delete(category)
    db.commit()
    MenuService.invalidate_cache()
    logger.info("Категория удалена", extra={"category_id": category_id})
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="delete_category",
        entity="service_category",
        entity_id=category_id,
        request=http_request,
    )


@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    payload: ServiceCreate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_required),
):
    if payload.category_id:
        category = db.query(ServiceCategory).filter(ServiceCategory.id == payload.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    service = Service(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    MenuService.invalidate_cache()
    logger.info("Создана услуга", extra={"service_id": service.id, "service_name": service.name})
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="create_service",
        entity="service",
        entity_id=service.id,
        payload=payload.model_dump(),
        request=http_request,
    )
    return ServiceResponse.model_validate(service)


@router.patch("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    payload: ServiceUpdate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_required),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")

    update_data = payload.model_dump(exclude_unset=True)
    if "category_id" in update_data and update_data["category_id"]:
        category = db.query(ServiceCategory).filter(ServiceCategory.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    for field, value in update_data.items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    MenuService.invalidate_cache()
    logger.info("Услуга обновлена", extra={"service_id": service.id})
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="update_service",
        entity="service",
        entity_id=service.id,
        payload=payload.model_dump(exclude_unset=True),
        request=http_request,
    )
    return ServiceResponse.model_validate(service)


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_required),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")

    db.delete(service)
    db.commit()
    MenuService.invalidate_cache()
    logger.info("Услуга удалена", extra={"service_id": service_id})
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="delete_service",
        entity="service",
        entity_id=service_id,
        request=http_request,
    )


@router.post("/upload")
async def upload_menu_image(
    file: UploadFile = File(...),
    _: dict = Depends(super_admin_required),
):
    url = StorageService.save_menu_image(file)
    logger.info("Загружено изображение меню", extra={"url": url})
    return {"url": url}


@router.post("/categories/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_categories(
    payload: CategoryReorderRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(super_admin_required),
):
    ids = [item.id for item in payload.items]
    if not ids:
        return

    categories = (
        db.query(ServiceCategory)
        .filter(ServiceCategory.id.in_(ids))
        .all()
    )
    categories_map = {category.id: category for category in categories}

    for item in payload.items:
        category = categories_map.get(item.id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Категория {item.id} не найдена")
        if category.parent_id != payload.parent_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Все категории должны принадлежать одному уровню")
        category.order_index = item.order_index

    db.commit()
    MenuService.invalidate_cache()


@router.post("/services/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_services(
    payload: ServiceReorderRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(super_admin_required),
):
    ids = [item.id for item in payload.items]
    if not ids:
        return

    services = (
        db.query(Service)
        .filter(Service.id.in_(ids))
        .all()
    )
    services_map = {service.id: service for service in services}

    for item in payload.items:
        service = services_map.get(item.id)
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Услуга {item.id} не найдена")
        if service.category_id != payload.category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Все услуги должны принадлежать одной категории")
        service.order_index = item.order_index

    db.commit()
    MenuService.invalidate_cache()


@router.post("/services/bulk", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_update_services(
    payload: ServicesBulkUpdateRequest,
    db: Session = Depends(get_db),
    admin=Depends(super_admin_required),
):
    if not payload.ids:
        return

    services = db.query(Service).filter(Service.id.in_(payload.ids)).all()
    if not services:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуги не найдены")

    if payload.category_id:
        category = db.query(ServiceCategory).filter(ServiceCategory.id == payload.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")

    for service in services:
        if payload.is_active is not None:
            service.is_active = payload.is_active
        if payload.category_id is not None:
            service.category_id = payload.category_id

    db.commit()
    MenuService.invalidate_cache()
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="bulk_update_services",
        entity="service",
        entity_id=None,
        payload=payload.model_dump(),
    )

