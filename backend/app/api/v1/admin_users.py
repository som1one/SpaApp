import logging
from datetime import datetime
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.apis.dependencies import admin_required
from app.core.database import get_db
from app.models.user import User
from app.schemas.admin_users import AdminUserResponse, AdminUsersListResponse, AdminUserYClientsResponse
from app.services.yclients_service import yclients_service

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])
logger = logging.getLogger(__name__)


def _build_users_query(
    db: Session,
    search: Optional[str],
    is_active: Optional[bool],
    is_verified: Optional[bool],
    min_loyalty: Optional[int],
    sort_by: str,
    sort_dir: str,
):
    query = db.query(User)

    if search:
        search_lower = search.lower().strip()
        if search_lower:
            query = query.filter(
                or_(
                    User.email.ilike(f"%{search_lower}%"),
                    User.name.ilike(f"%{search_lower}%"),
                    User.surname.ilike(f"%{search_lower}%"),
                )
            )

    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    if min_loyalty is not None:
        query = query.filter(User.loyalty_level_id >= min_loyalty)

    order_col = User.loyalty_level_id if sort_by == "loyalty_level" else User.created_at
    query = query.order_by(order_col.asc() if sort_dir == "asc" else order_col.desc())
    return query


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
    base_query = _build_users_query(
        db=db,
        search=search,
        is_active=is_active,
        is_verified=is_verified,
        min_loyalty=min_loyalty,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

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


@router.get("/export")
async def export_users_excel(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
    search: Optional[str] = Query(None, description="Поиск по имени или email"),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    min_loyalty: Optional[int] = Query(None, ge=0),
    sort_by: str = Query("created_at", pattern="^(created_at|loyalty_level)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
):
    try:
        from openpyxl import Workbook
    except Exception as exc:
        logger.error("openpyxl is not installed", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Экспорт в Excel недоступен: не установлен openpyxl",
        ) from exc

    users = _build_users_query(
        db=db,
        search=search,
        is_active=is_active,
        is_verified=is_verified,
        min_loyalty=min_loyalty,
        sort_by=sort_by,
        sort_dir=sort_dir,
    ).all()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Users"

    headers = [
        "ID",
        "Имя",
        "Фамилия",
        "Email",
        "Телефон",
        "Активен",
        "Подтвержден",
        "Уровень лояльности",
        "Бонусы",
        "Потрачено бонусов",
        "Дата регистрации (UTC)",
    ]
    worksheet.append(headers)

    for user in users:
        worksheet.append(
            [
                user.id,
                user.name or "",
                user.surname or "",
                user.email or "",
                user.phone or "",
                "Да" if user.is_active else "Нет",
                "Да" if user.is_verified else "Нет",
                user.loyalty_level_id if user.loyalty_level_id is not None else "",
                user.loyalty_bonuses or 0,
                user.spent_bonuses or 0,
                user.created_at.isoformat() if user.created_at else "",
            ]
        )

    file_stream = BytesIO()
    workbook.save(file_stream)
    file_stream.seek(0)

    filename = f"users_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{user_id}/yclients", response_model=AdminUserYClientsResponse)
async def get_user_yclients_snapshot(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not settings.YCLIENTS_ENABLED:
        return AdminUserYClientsResponse(
            found=False,
            message="YClients интеграция выключена",
        )

    if not settings.YCLIENTS_COMPANY_ID or not settings.YCLIENTS_API_TOKEN or not settings.YCLIENTS_USER_TOKEN:
        return AdminUserYClientsResponse(
            found=False,
            message="YClients не настроен",
        )

    try:
        yclients_service.configure(
            company_id=settings.YCLIENTS_COMPANY_ID,
            api_token=settings.YCLIENTS_API_TOKEN,
            user_token=settings.YCLIENTS_USER_TOKEN,
        )
        snapshot = yclients_service.get_client_snapshot(
            phone=user.phone,
            email=user.email,
        )
    except Exception as exc:
        logger.error("Ошибка загрузки данных пользователя из YClients: %s", exc, exc_info=True)
        return AdminUserYClientsResponse(
            found=False,
            message="Не удалось получить данные из YClients",
        )

    if not snapshot:
        return AdminUserYClientsResponse(
            found=False,
            message="Клиент в YClients не найден",
        )

    return AdminUserYClientsResponse(
        found=True,
        client_id=snapshot.get("client_id"),
        phone=snapshot.get("phone"),
        balance=snapshot.get("balance"),
        spent=snapshot.get("spent"),
        discount=snapshot.get("discount"),
        loyalty_level_title=snapshot.get("loyalty_level_title"),
        categories=snapshot.get("categories") or [],
    )
