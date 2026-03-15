import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.apis.dependencies import admin_required
from app.core.database import get_db
from app.models.user import User
from app.schemas.admin_users import AdminUserResponse, AdminUsersListResponse

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])
logger = logging.getLogger(__name__)


@router.get("", response_model=AdminUsersListResponse)
async def list_users(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
    search: Optional[str] = Query(None, description="Поиск по имени или email"),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    min_loyalty: Optional[int] = Query(None, ge=0),
    sort_by: str = Query("created_at", pattern="^(created_at|loyalty_level)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    # Построение базового запроса
    base_query = db.query(User)
    
    # Оптимизированный поиск
    if search:
        search_lower = search.lower().strip()
        if search_lower:
            # Поиск по имени, фамилии, email и уникальному коду
            search_filter = or_(
                User.email.ilike(f"%{search_lower}%"),
                User.name.ilike(f"%{search_lower}%"),
                User.surname.ilike(f"%{search_lower}%"),
                User.unique_code.ilike(f"%{search_lower.upper()}%"),  # Код всегда в верхнем регистре
            )
            base_query = base_query.filter(search_filter)

    # Применяем фильтры
    if is_active is not None:
        base_query = base_query.filter(User.is_active == is_active)
    if is_verified is not None:
        base_query = base_query.filter(User.is_verified == is_verified)
    if min_loyalty is not None:
        base_query = base_query.filter(User.loyalty_level >= min_loyalty)

    # Определяем сортировку
    if sort_by == "loyalty_level":
        order_col = User.loyalty_level
    else:
        order_col = User.created_at
    
    if sort_dir == "asc":
        base_query = base_query.order_by(order_col.asc())
    else:
        base_query = base_query.order_by(order_col.desc())

    # Оптимизация: подсчитываем total только если нужно (для первой страницы или если есть фильтры)
    # Для остальных страниц можно использовать приблизительное значение
    if offset == 0 or search or is_active is not None or is_verified is not None or min_loyalty is not None:
        # Точный подсчет только когда действительно нужно
        total = base_query.count()
    else:
        # Для последующих страниц без фильтров используем приблизительное значение
        # Это значительно быстрее при большом количестве записей
        total = db.query(func.count(User.id)).scalar()

    # Загружаем пользователей с ограничениями
    users = base_query.offset(offset).limit(limit).all()

    logger.debug("Loaded %s admin users (total: %s, offset: %s, limit: %s)", len(users), total, offset, limit)
    
    # Оптимизированная сериализация - используем from_attributes напрямую
    # Это намного быстрее чем ручное создание словарей
    try:
        # Используем list comprehension с обработкой ошибок для максимальной производительности
        items = []
        for user in users:
            try:
                # Используем model_validate напрямую - Pydantic автоматически извлекает данные
                # Схема настроена с from_attributes=True, поэтому это самый быстрый способ
                item = AdminUserResponse.model_validate(user)
                # Нормализуем surname: пустая строка -> None (для совместимости со схемой)
                if item.surname == "":
                    # Используем object.__setattr__ для обхода защиты Pydantic
                    object.__setattr__(item, 'surname', None)
                items.append(item)
            except Exception as e:
                # Логируем только в режиме отладки, чтобы не замедлять
                logger.debug("Error serializing user ID=%s: %s", getattr(user, 'id', 'unknown'), str(e))
                continue
        
        response = AdminUsersListResponse(
            items=items,
            total=total,
        )
        return response
    except Exception as e:
        logger.error("Error creating response: %s", str(e), exc_info=True)
        raise

