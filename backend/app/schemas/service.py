"""
Pydantic схемы для услуг и категорий
"""
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


AdditionalService = List[dict] | List[str] | None


class ServiceBase(BaseModel):
    name: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration: Optional[int] = None
    category_id: Optional[int] = Field(None, description="ID категории или подкатегории")
    image_url: Optional[str] = None
    detail_image_url: Optional[str] = None
    additional_services: Optional[List[dict]] = None
    highlights: Optional[List[str]] = None
    contact_link: Optional[str] = None
    contact_label: Optional[str] = None
    book_button_label: Optional[str] = None
    order_index: int = 0
    is_active: bool = True
    yclients_service_id: Optional[int] = None
    yclients_staff_id: Optional[int] = None


class ServiceCreate(ServiceBase):
    name: str = Field(..., min_length=2, max_length=200)


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    detail_image_url: Optional[str] = None
    additional_services: Optional[List[dict]] = None
    highlights: Optional[List[str]] = None
    contact_link: Optional[str] = None
    contact_label: Optional[str] = None
    book_button_label: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: int
    category: Optional[str] = None  # legacy field
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    yclients_service_id: Optional[int] = None
    yclients_staff_id: Optional[int] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ServiceCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = Field(None, description="ID родительской категории")
    order_index: int = 0
    is_active: bool = True


class ServiceCategoryCreate(ServiceCategoryBase):
    name: str = Field(..., min_length=2, max_length=200)


class ServiceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class ServiceCategoryResponse(ServiceCategoryBase):
    id: int

    class Config:
        from_attributes = True


class MenuTreeItem(ServiceCategoryResponse):
    id: Optional[int] = None  # Опциональный для виртуальных категорий (например, "Без категории")
    children: List["MenuTreeItem"] = Field(default_factory=list)
    services: List[ServiceResponse] = Field(default_factory=list)


MenuTreeItem.model_rebuild()


class ReorderItem(BaseModel):
    id: int
    order_index: int


class CategoryReorderRequest(BaseModel):
    parent_id: int | None = None
    items: List[ReorderItem]


class ServiceReorderRequest(BaseModel):
    category_id: int | None = None
    items: List[ReorderItem]


class ServicesBulkUpdateRequest(BaseModel):
    ids: List[int]
    is_active: Optional[bool] = None
    category_id: Optional[int] = None

