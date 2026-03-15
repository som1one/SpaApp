from typing import List, Optional
import time

from sqlalchemy.orm import Session, joinedload

from app.models.service import ServiceCategory
from app.schemas.service import MenuTreeItem, ServiceResponse


class MenuService:
    # простой in-memory кеш на уровне процесса
    _cache_tree: Optional[List[MenuTreeItem]] = None
    _cache_timestamp: float = 0.0
    _cache_ttl_seconds: int = 5  # Уменьшено до 5 секунд для быстрого обновления

    @staticmethod
    def _build_tree(categories: List[ServiceCategory], include_inactive: bool = False) -> List[MenuTreeItem]:
        tree: List[MenuTreeItem] = []
        for category in categories:
            children = MenuService._build_tree(
                sorted(
                    [child for child in category.children if (include_inactive or child.is_active)],
                    key=lambda c: c.order_index,
                ),
                include_inactive=include_inactive,
            )
            services = sorted(
                [service for service in category.services if (include_inactive or service.is_active)],
                key=lambda s: s.order_index,
            )
            # Безопасная сериализация услуг
            service_responses = []
            for service in services:
                try:
                    service_responses.append(ServiceResponse.model_validate(service))
                except Exception as e:
                    # Логируем ошибку, но продолжаем обработку
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Ошибка при сериализации услуги {service.id}: {e}")
                    continue
            
            tree.append(
                MenuTreeItem(
                    id=category.id,
                    name=category.name,
                    description=category.description,
                    image_url=category.image_url,
                    parent_id=category.parent_id,
                    order_index=category.order_index,
                    is_active=category.is_active,
                    children=children,
                    services=service_responses,
                )
            )
        return tree

    @classmethod
    def get_menu_tree(cls, db: Session, include_inactive: bool = False) -> List[MenuTreeItem]:
        now = time.time()
        # Кешируем только для публичного API (include_inactive=False)
        if not include_inactive and cls._cache_tree is not None and (now - cls._cache_timestamp) < cls._cache_ttl_seconds:
            return cls._cache_tree

        # Загружаем категории с услугами и подкатегориями (рекурсивно)
        # Используем selectinload для более эффективной загрузки вложенных данных
        from sqlalchemy.orm import selectinload
        
        query = db.query(ServiceCategory).options(
            selectinload(ServiceCategory.services),
            selectinload(ServiceCategory.children).selectinload(ServiceCategory.services),
            selectinload(ServiceCategory.children).selectinload(ServiceCategory.children).selectinload(ServiceCategory.services),
        ).filter(ServiceCategory.parent_id.is_(None))
        if not include_inactive:
            query = query.filter(ServiceCategory.is_active.is_(True))
        roots = query.order_by(ServiceCategory.order_index.asc(), ServiceCategory.id.asc()).all()
        
        tree = cls._build_tree(roots, include_inactive=include_inactive)
        
        # Для админки добавляем услуги без категорий
        if include_inactive:
            from app.models.service import Service
            services_without_category = db.query(Service).filter(Service.category_id.is_(None))
            if not include_inactive:
                services_without_category = services_without_category.filter(Service.is_active.is_(True))
            services_without_category = services_without_category.order_by(Service.order_index.asc(), Service.id.asc()).all()
            
            if services_without_category:
                # Создаем виртуальную категорию "Без категории"
                service_responses = []
                for service in services_without_category:
                    try:
                        service_responses.append(ServiceResponse.model_validate(service))
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Ошибка при сериализации услуги {service.id}: {e}")
                        continue
                
                uncategorized_category = MenuTreeItem(
                    id=None,  # Виртуальная категория, без ID
                    name="Без категории",
                    description="Услуги, не привязанные к категориям",
                    image_url=None,
                    parent_id=None,
                    order_index=999999,  # В конец списка
                    is_active=True,
                    children=[],
                    services=service_responses,
                )
                tree.append(uncategorized_category)
        
        # Кешируем только для публичного API
        if not include_inactive:
            cls._cache_tree = tree
            cls._cache_timestamp = now
        return tree

    @classmethod
    def invalidate_cache(cls) -> None:
        cls._cache_tree = None
        cls._cache_timestamp = 0.0

