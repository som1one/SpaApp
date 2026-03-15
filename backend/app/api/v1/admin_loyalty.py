"""
Админские API для управления программой лояльности
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.apis.dependencies import admin_required
from app.core.database import get_db
from app.models.loyalty import LoyaltyLevel, LoyaltyBonus
from app.models.user import User
from app.schemas.loyalty import (
    LoyaltyLevelResponse,
    LoyaltyLevelCreate,
    LoyaltyLevelUpdate,
    LoyaltyBonusResponse,
    LoyaltyBonusCreate,
    LoyaltyBonusUpdate,
)
from app.services.audit_service import AuditService
from app.models.booking import Booking, BookingStatus
from datetime import datetime as dt

router = APIRouter(prefix="/admin/loyalty", tags=["Admin Loyalty"])
logger = logging.getLogger(__name__)


# Уровни лояльности
@router.get("/levels", response_model=List[LoyaltyLevelResponse])
async def list_loyalty_levels(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Список уровней лояльности"""
    levels = (
        db.query(LoyaltyLevel)
        .order_by(LoyaltyLevel.order_index.asc(), LoyaltyLevel.min_bonuses.asc())
        .all()
    )
    return [LoyaltyLevelResponse.model_validate(level) for level in levels]


@router.post("/levels", response_model=LoyaltyLevelResponse, status_code=status.HTTP_201_CREATED)
async def create_loyalty_level(
    payload: LoyaltyLevelCreate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Создать уровень лояльности"""
    level_data = payload.model_dump()
    cashback_percent = level_data.get("cashback_percent")
    if cashback_percent is None or cashback_percent < 0 or cashback_percent > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cashback_percent должен быть в диапазоне 0-100",
        )

    level = LoyaltyLevel(**level_data)
    db.add(level)
    db.commit()
    db.refresh(level)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="create_loyalty_level",
        entity="loyalty_level",
        entity_id=level.id,
        payload=payload.model_dump(),
        request=http_request,
    )
    
    return LoyaltyLevelResponse.model_validate(level)


@router.patch("/levels/{level_id}", response_model=LoyaltyLevelResponse)
async def update_loyalty_level(
    level_id: int,
    payload: LoyaltyLevelUpdate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Обновить уровень лояльности"""
    level = db.query(LoyaltyLevel).filter(LoyaltyLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Уровень не найден")
    
    update_data = payload.model_dump(exclude_unset=True)
    cashback_percent = update_data.get("cashback_percent")
    if cashback_percent is not None:
        if cashback_percent < 0 or cashback_percent > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cashback_percent должен быть в диапазоне 0-100",
            )
    for field, value in update_data.items():
        setattr(level, field, value)
    
    db.commit()
    db.refresh(level)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="update_loyalty_level",
        entity="loyalty_level",
        entity_id=level.id,
        payload=update_data,
        request=http_request,
    )
    
    return LoyaltyLevelResponse.model_validate(level)


@router.delete("/levels/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_loyalty_level(
    level_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Удалить уровень лояльности"""
    level = db.query(LoyaltyLevel).filter(LoyaltyLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Уровень не найден")
    
    db.delete(level)
    db.commit()
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="delete_loyalty_level",
        entity="loyalty_level",
        entity_id=level_id,
        request=http_request,
    )


# Бонусы
@router.get("/bonuses", response_model=List[LoyaltyBonusResponse])
async def list_loyalty_bonuses(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Список бонусов"""
    bonuses = (
        db.query(LoyaltyBonus)
        .order_by(LoyaltyBonus.order_index.asc(), LoyaltyBonus.id.asc())
        .all()
    )
    return [LoyaltyBonusResponse.model_validate(bonus) for bonus in bonuses]


@router.post("/bonuses", response_model=LoyaltyBonusResponse, status_code=status.HTTP_201_CREATED)
async def create_loyalty_bonus(
    payload: LoyaltyBonusCreate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Создать бонус"""
    bonus = LoyaltyBonus(**payload.model_dump())
    db.add(bonus)
    db.commit()
    db.refresh(bonus)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="create_loyalty_bonus",
        entity="loyalty_bonus",
        entity_id=bonus.id,
        payload=payload.model_dump(),
        request=http_request,
    )
    
    return LoyaltyBonusResponse.model_validate(bonus)


@router.patch("/bonuses/{bonus_id}", response_model=LoyaltyBonusResponse)
async def update_loyalty_bonus(
    bonus_id: int,
    payload: LoyaltyBonusUpdate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Обновить бонус"""
    bonus = db.query(LoyaltyBonus).filter(LoyaltyBonus.id == bonus_id).first()
    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бонус не найден")
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bonus, field, value)
    
    db.commit()
    db.refresh(bonus)
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="update_loyalty_bonus",
        entity="loyalty_bonus",
        entity_id=bonus.id,
        payload=update_data,
        request=http_request,
    )
    
    return LoyaltyBonusResponse.model_validate(bonus)


@router.delete("/bonuses/{bonus_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_loyalty_bonus(
    bonus_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Удалить бонус"""
    bonus = db.query(LoyaltyBonus).filter(LoyaltyBonus.id == bonus_id).first()
    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бонус не найден")
    
    db.delete(bonus)
    db.commit()
    
    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="delete_loyalty_bonus",
        entity="loyalty_bonus",
        entity_id=bonus_id,
        request=http_request,
    )


class LoyaltyServiceAward(BaseModel):
    """Услуга, за которую начисляются бонусы"""
    name: str
    price_rub: int


class LoyaltyAdjustRequest(BaseModel):
    """Запрос на изменение бонусов пользователя"""
    bonuses_delta: int | None = None  # Отрицательное значение = списание (скидка)
    reason: str | None = None
    services: List[LoyaltyServiceAward] | None = None  # Услуги для начисления бонусов


@router.post("/users/{user_id}/adjust")
async def adjust_user_loyalty_bonuses(
    user_id: int,
    payload: LoyaltyAdjustRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """
    Ручная корректировка бонусов лояльности пользователя из админки.

    Логика:
    - services: начисление бонусов по проценту уровня пользователя (положительное значение)
    - bonuses_delta: списание бонусов (отрицательное значение = скидка)
    - Можно использовать оба одновременно (начислить за услуги и списать скидку)
    
    При списании бонусов (отрицательное значение) увеличивается spent_bonuses.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    current_bonuses = user.loyalty_bonuses or 0
    total_delta = 0
    reason_parts = []
    bonuses_awarded = 0
    bonuses_spent = 0

    # Получаем уровень пользователя для расчета процента кэшбэка (если нужен)
    from app.services.loyalty_service import _get_user_loyalty_level
    user_level = _get_user_loyalty_level(db, user)
    cashback_percent = user_level.cashback_percent if user_level else 1

    # 1. Начисление бонусов за услуги (по проценту уровня)
    services = payload.services or []
    if services:
        # Вычисляем сумму услуг
        total_services_cost = sum(max(0, service.price_rub) for service in services)
        if total_services_cost <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сумма услуг должна быть положительной",
            )
        
        # Вычисляем бонусы по проценту уровня
        bonuses_to_award = int(total_services_cost * cashback_percent / 100)
        total_delta += bonuses_to_award
        bonuses_awarded = bonuses_to_award
        
        service_details = ", ".join(f"{service.name} ({service.price_rub} ₽)" for service in services)
        reason_parts.append(f"Начисление бонусов за услуги: {service_details} (кэшбэк {cashback_percent}% = {bonuses_to_award} бонусов)")

    # 2. Списание бонусов (скидка)
    if payload.bonuses_delta is not None and payload.bonuses_delta != 0:
        if payload.bonuses_delta > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="bonuses_delta для списания должно быть отрицательным. Для начисления используйте services.",
            )
        total_delta += payload.bonuses_delta
        bonuses_spent = abs(payload.bonuses_delta)
        reason_parts.append(f"Списание бонусов: {bonuses_spent} бонусов (скидка)")

    # Проверяем, что есть хотя бы одно действие
    # Если total_delta == 0, считаем, что изменение не требуется и просто возвращаем текущее состояние
    if total_delta == 0:
        return {
            "success": True,
            "user_id": user.id,
            "current_bonuses": current_bonuses,
            "spent_bonuses": user.spent_bonuses or 0,
            "bonuses_awarded": 0,
            "bonuses_spent": 0,
            "loyalty_level_id": user.loyalty_level_id,
            "loyalty_level_name": user_level.name if user_level else None,
            "services": [service.model_dump() for service in services] if services else None,
        }

    # Проверяем, что не списываем больше, чем есть
    if total_delta < 0 and abs(total_delta) > current_bonuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недостаточно бонусов. У пользователя {current_bonuses} бонусов, пытаетесь списать {abs(total_delta)}"
        )

    # Формируем итоговую причину
    reason_text = payload.reason or " | ".join(reason_parts)

    # Обновляем бонусы
    new_bonuses = max(0, current_bonuses + total_delta)
    user.loyalty_bonuses = new_bonuses
    
    # Если списываем бонусы, увеличиваем spent_bonuses
    if total_delta < 0:
        user.spent_bonuses = (user.spent_bonuses or 0) + abs(total_delta)
    
    # При списании/начислении по коду считаем, что услуга завершена,
    # и создаём запись в bookings, чтобы это учитывалось в прогрессе уровней.
    if services:
        total_services_cost = sum(max(0, service.price_rub) for service in services)
        if total_services_cost > 0:
            booking = Booking(
                user_id=user.id,
                service_name=", ".join(service.name for service in services),
                service_duration=None,
                service_price=total_services_cost * 100,  # в копейках
                from app.utils.timezone import moscow_now
                appointment_datetime=moscow_now(),
                status=BookingStatus.COMPLETED,
                notes=reason_text,
                phone=user.phone or user.email,
            )
            db.add(booking)

    # Обновляем уровень лояльности на основе новых бонусов
    # Важно: делаем flush, чтобы изменения были видны в сессии перед запросом уровня
    db.flush()
    
    from app.services.loyalty_service import _get_user_loyalty_level
    new_level = _get_user_loyalty_level(db, user)
    if new_level:
        old_level_id = user.loyalty_level_id
        user.loyalty_level_id = new_level.id
        # Логируем изменение уровня для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Обновление уровня лояльности для пользователя {user.id}: "
            f"бонусы {current_bonuses} -> {new_bonuses}, "
            f"уровень {old_level_id} -> {new_level.id} (min_bonuses={new_level.min_bonuses})"
        )
    else:
        # Если уровень не найден, сбрасываем его
        user.loyalty_level_id = None

    db.commit()
    db.refresh(user)

    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="adjust_loyalty_bonuses",
        entity="user",
        entity_id=user.id,
        payload={
            "delta": total_delta,
            "reason": reason_text,
            "old_bonuses": current_bonuses,
            "new_bonuses": new_bonuses,
            "spent_bonuses": user.spent_bonuses,
            "services": [service.model_dump() for service in services] if services else None,
        },
        request=http_request,
    )

    return {
        "success": True,
        "user_id": user.id,
        "current_bonuses": new_bonuses,
        "spent_bonuses": user.spent_bonuses,
        "bonuses_awarded": bonuses_awarded,
        "bonuses_spent": bonuses_spent,
        "loyalty_level_id": user.loyalty_level_id,
        "loyalty_level_name": new_level.name if new_level else None,
        "services": [service.model_dump() for service in services] if services else None,
    }


@router.get("/users/by-code/{unique_code}")
async def get_user_by_code(
    unique_code: str,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """
    Найти пользователя по уникальному коду.
    
    Используется для быстрого поиска пользователя в админ панели
    при списании бонусов по коду.
    """
    user = db.query(User).filter(User.unique_code == unique_code.upper()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с кодом {unique_code} не найден"
        )
    
    # Получаем уровень пользователя для расчета процента кэшбэка
    from app.services.loyalty_service import _get_user_loyalty_level
    user_level = _get_user_loyalty_level(db, user)
    cashback_percent = user_level.cashback_percent if user_level else 1
    
    from app.schemas.admin_users import AdminUserResponse
    user_data = AdminUserResponse.model_validate(user)
    # Добавляем cashback_percent вручную, так как его нет в модели User
    user_data.cashback_percent = cashback_percent
    return user_data


class LoyaltySettingsResponse(BaseModel):
    """Настройки программы лояльности"""
    loyalty_enabled: bool
    points_per_100_rub: int


class LoyaltySettingsUpdate(BaseModel):
    """Обновление настроек программы лояльности"""
    points_per_100_rub: int | None = None
    loyalty_enabled: bool | None = None


@router.get("/settings", response_model=LoyaltySettingsResponse)
async def get_loyalty_settings(
    _: dict = Depends(admin_required),
):
    """Получить текущие настройки программы лояльности"""
    from app.core.config import settings
    return LoyaltySettingsResponse(
        loyalty_enabled=settings.LOYALTY_ENABLED,
        points_per_100_rub=settings.LOYALTY_POINTS_PER_100_RUB,
    )


@router.patch("/settings")
async def update_loyalty_settings(
    payload: LoyaltySettingsUpdate,
    http_request: Request,
    admin=Depends(admin_required),
):
    """
    Обновить настройки программы лояльности.
    
    ВНИМАНИЕ: Это обновляет только runtime-значение настроек.
    После перезапуска сервера значения вернутся к тем, что в .env/.env.local
    """
    from app.core.config import settings
    
    updated_fields = {}

    if payload.points_per_100_rub is not None:
        if payload.points_per_100_rub < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Количество баллов не может быть отрицательным"
            )
        old_value = settings.LOYALTY_POINTS_PER_100_RUB
        settings.LOYALTY_POINTS_PER_100_RUB = payload.points_per_100_rub
        updated_fields["points_per_100_rub"] = {
            "old": old_value,
            "new": payload.points_per_100_rub,
        }

    if payload.loyalty_enabled is not None:
        old_enabled = settings.LOYALTY_ENABLED
        settings.LOYALTY_ENABLED = payload.loyalty_enabled
        updated_fields["loyalty_enabled"] = {
            "old": old_enabled,
            "new": payload.loyalty_enabled,
        }

    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет данных для обновления",
        )
    
    logger.info(
        "Обновлены настройки лояльности",
        extra={
            "admin_id": admin.id,
            **{key: value for key, value in updated_fields.items()},
        },
    )
    
    return {
        "success": True,
        "points_per_100_rub": settings.LOYALTY_POINTS_PER_100_RUB,
        "loyalty_enabled": settings.LOYALTY_ENABLED,
        "note": "Изменения применены. После перезапуска сервера настройки вернутся к значениям из .env"
    }

