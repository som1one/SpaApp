"""
Админские API для управления программой лояльности
"""
import logging
from datetime import datetime as dt
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.apis.dependencies import admin_required
from app.core.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.loyalty import LoyaltyBonus, LoyaltyLevel, LoyaltyProgramSettings
from app.models.user import User
from app.schemas.loyalty import (
    LoyaltyBonusCreate,
    LoyaltyBonusResponse,
    LoyaltyBonusUpdate,
    LoyaltyLevelCreate,
    LoyaltyLevelResponse,
    LoyaltyLevelUpdate,
    LoyaltySettingsResponse,
    LoyaltySettingsUpdate,
)
from app.services.audit_service import AuditService
from app.services.loyalty_service import (
    TRANSACTION_TYPE_BULK,
    TRANSACTION_TYPE_MANUAL,
    TRANSACTION_TYPE_TEMPORARY,
    add_loyalty_transaction,
    get_loyalty_settings,
    get_user_loyalty_level,
    refresh_user_loyalty_level,
)

router = APIRouter(prefix="/admin/loyalty", tags=["Admin Loyalty"])
logger = logging.getLogger(__name__)


@router.get("/levels", response_model=List[LoyaltyLevelResponse])
async def list_loyalty_levels(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Список уровней лояльности."""
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
    """Создать уровень лояльности."""
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
    """Обновить уровень лояльности."""
    level = db.query(LoyaltyLevel).filter(LoyaltyLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Уровень не найден")

    update_data = payload.model_dump(exclude_unset=True)
    cashback_percent = update_data.get("cashback_percent")
    if cashback_percent is not None and (cashback_percent < 0 or cashback_percent > 100):
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
    """Удалить уровень лояльности."""
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


@router.get("/bonuses", response_model=List[LoyaltyBonusResponse])
async def list_loyalty_bonuses(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Список бонусов и привилегий."""
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
    """Создать бонус."""
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
    """Обновить бонус."""
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
    """Удалить бонус."""
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
    """Услуга, за которую начисляются бонусы."""
    name: str
    price_rub: int


class LoyaltyAdjustRequest(BaseModel):
    """Запрос на ручное начисление бонусов пользователю."""
    bonuses_delta: int | None = None
    reason: str | None = None
    services: List[LoyaltyServiceAward] | None = None
    expires_in_days: int | None = None


class BulkAwardRequest(BaseModel):
    bonuses_amount: int
    reason: str | None = None
    expires_in_days: int | None = None


@router.post("/users/{user_id}/adjust")
async def adjust_user_loyalty_bonuses(
    user_id: int,
    payload: LoyaltyAdjustRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Ручная корректировка бонусов пользователя из админки."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    current_bonuses = user.loyalty_bonuses or 0
    total_delta = 0
    reason_parts = []
    bonuses_awarded = 0

    user_level = get_user_loyalty_level(db, user)
    cashback_percent = user_level.cashback_percent if user_level else 1
    loyalty_settings = get_loyalty_settings(db)
    expires_in_days = payload.expires_in_days
    if expires_in_days is not None and expires_in_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Срок действия временных бонусов должен быть больше 0 дней",
        )

    services = payload.services or []
    if services:
        total_services_cost = sum(max(0, service.price_rub) for service in services)
        if total_services_cost <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сумма услуг должна быть положительной",
            )

        bonuses_to_award = int(total_services_cost * cashback_percent / 100)
        total_delta += bonuses_to_award
        bonuses_awarded += bonuses_to_award
        service_details = ", ".join(f"{service.name} ({service.price_rub} ₽)" for service in services)
        reason_parts.append(
            f"Начисление за услуги: {service_details} (кэшбэк {cashback_percent}% = {bonuses_to_award} бонусов)"
        )

    if payload.bonuses_delta is not None and payload.bonuses_delta != 0:
        if payload.bonuses_delta < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Списание бонусов отключено. Используйте только положительные значения.",
            )
        total_delta += payload.bonuses_delta
        bonuses_awarded += payload.bonuses_delta
        reason_parts.append(f"Ручное начисление: +{payload.bonuses_delta}")

    if total_delta == 0:
        return {
            "success": True,
            "user_id": user.id,
            "current_bonuses": current_bonuses,
            "spent_bonuses": user.spent_bonuses or 0,
            "bonuses_awarded": 0,
            "loyalty_level_id": user.loyalty_level_id,
            "loyalty_level_name": user_level.name if user_level else None,
            "services": [service.model_dump() for service in services] if services else None,
        }

    reason_text = payload.reason or " | ".join(reason_parts) or "Ручное начисление бонусов"

    booking = None
    if services:
        total_services_cost = sum(max(0, service.price_rub) for service in services)
        booking = Booking(
            user_id=user.id,
            service_name=", ".join(service.name for service in services),
            service_duration=None,
            service_price=total_services_cost * 100,
            appointment_datetime=dt.utcnow(),
            status=BookingStatus.COMPLETED,
            notes=reason_text,
            phone=user.phone or user.email,
        )
        db.add(booking)
        db.flush()

    add_loyalty_transaction(
        db=db,
        user=user,
        amount=total_delta,
        transaction_type=TRANSACTION_TYPE_TEMPORARY if expires_in_days else TRANSACTION_TYPE_MANUAL,
        title="Временное начисление" if expires_in_days else "Ручное начисление",
        description=reason_text,
        reason=reason_text,
        booking=booking,
        expires_in_days=expires_in_days if expires_in_days is not None else loyalty_settings.bonus_expiry_days,
    )

    new_level = refresh_user_loyalty_level(db, user)
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
            "expires_in_days": expires_in_days,
            "old_bonuses": current_bonuses,
            "new_bonuses": user.loyalty_bonuses,
            "services": [service.model_dump() for service in services] if services else None,
        },
        request=http_request,
    )

    return {
        "success": True,
        "user_id": user.id,
        "current_bonuses": user.loyalty_bonuses,
        "spent_bonuses": user.spent_bonuses,
        "bonuses_awarded": bonuses_awarded,
        "loyalty_level_id": user.loyalty_level_id,
        "loyalty_level_name": new_level.name if new_level else None,
        "services": [service.model_dump() for service in services] if services else None,
    }


@router.post("/award-all")
async def bulk_award_loyalty_bonuses(
    payload: BulkAwardRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Массовое начисление бонусов всем пользователям."""
    if payload.bonuses_amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Количество бонусов должно быть больше 0")
    if payload.expires_in_days is not None and payload.expires_in_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Срок действия временных бонусов должен быть больше 0 дней",
        )

    from app.services.loyalty_service import get_loyalty_settings

    loyalty_settings = get_loyalty_settings(db)
    users = db.query(User).filter(User.is_active == True).all()
    if not users:
        return {"success": True, "processed_users": 0}

    reason_text = payload.reason or f"Массовое начисление {payload.bonuses_amount} бонусов"
    for user in users:
        add_loyalty_transaction(
            db=db,
            user=user,
            amount=payload.bonuses_amount,
            transaction_type=TRANSACTION_TYPE_TEMPORARY if payload.expires_in_days else TRANSACTION_TYPE_BULK,
            title="Временное массовое начисление" if payload.expires_in_days else "Массовое начисление",
            description=reason_text,
            reason=reason_text,
            expires_in_days=payload.expires_in_days if payload.expires_in_days is not None else loyalty_settings.bonus_expiry_days,
        )

    db.commit()

    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="bulk_award_loyalty_bonuses",
        entity="user",
        payload={
            "bonuses_amount": payload.bonuses_amount,
            "reason": reason_text,
            "expires_in_days": payload.expires_in_days,
            "processed_users": len(users),
        },
        request=http_request,
    )

    return {
        "success": True,
        "processed_users": len(users),
        "bonuses_amount": payload.bonuses_amount,
        "expires_in_days": payload.expires_in_days,
    }


@router.get("/users/by-code/{unique_code}")
async def get_user_by_code(
    unique_code: str,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Найти пользователя по уникальному коду для начисления бонусов в админке."""
    user = db.query(User).filter(User.unique_code == unique_code.upper()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с кодом {unique_code} не найден",
        )

    from app.schemas.admin_users import AdminUserResponse

    user_level = get_user_loyalty_level(db, user)
    cashback_percent = user_level.cashback_percent if user_level else 1

    user_data = AdminUserResponse.model_validate(user)
    user_data.cashback_percent = cashback_percent
    return user_data


@router.post("/recalculate-levels")
async def recalculate_loyalty_levels(
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Пересчитать уровни лояльности всем пользователям по завершённым визитам."""
    users = db.query(User).all()
    updated = 0

    for user in users:
        before = user.loyalty_level_id
        level = refresh_user_loyalty_level(db, user)
        after = level.id if level else None
        if before != after:
            updated += 1

    db.commit()

    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="recalculate_loyalty_levels",
        entity="loyalty_level",
        payload={"processed_users": len(users), "updated_users": updated},
        request=http_request,
    )

    return {
        "success": True,
        "processed_users": len(users),
        "updated_users": updated,
    }


def _get_or_create_loyalty_settings_model(db: Session) -> LoyaltyProgramSettings:
    settings_model = db.query(LoyaltyProgramSettings).order_by(LoyaltyProgramSettings.id.asc()).first()
    if not settings_model:
        current = get_loyalty_settings(db)
        settings_model = LoyaltyProgramSettings(
            loyalty_enabled=current.loyalty_enabled,
            points_per_100_rub=current.points_per_100_rub,
            welcome_bonus_amount=current.welcome_bonus_amount,
            bonus_expiry_days=current.bonus_expiry_days,
            yclients_bonus_field_id=current.yclients_bonus_field_id,
        )
        db.add(settings_model)
        db.commit()
        db.refresh(settings_model)
    return settings_model


@router.get("/settings", response_model=LoyaltySettingsResponse)
async def get_loyalty_settings_endpoint(
    db: Session = Depends(get_db),
    _: dict = Depends(admin_required),
):
    """Получить текущие настройки программы лояльности."""
    loyalty_settings = get_loyalty_settings(db)
    return LoyaltySettingsResponse(
        loyalty_enabled=loyalty_settings.loyalty_enabled,
        points_per_100_rub=loyalty_settings.points_per_100_rub,
        welcome_bonus_amount=loyalty_settings.welcome_bonus_amount,
        bonus_expiry_days=loyalty_settings.bonus_expiry_days,
        yclients_bonus_field_id=loyalty_settings.yclients_bonus_field_id,
    )


@router.patch("/settings")
async def update_loyalty_settings(
    payload: LoyaltySettingsUpdate,
    http_request: Request,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):
    """Обновить настройки программы лояльности и сохранить их в БД."""
    settings_model = _get_or_create_loyalty_settings_model(db)
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет данных для обновления")

    if "points_per_100_rub" in update_data and update_data["points_per_100_rub"] < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Количество баллов не может быть отрицательным")
    if "welcome_bonus_amount" in update_data and update_data["welcome_bonus_amount"] < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Приветственный бонус не может быть отрицательным")
    if "bonus_expiry_days" in update_data and update_data["bonus_expiry_days"] <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Срок действия бонусов должен быть больше 0")

    changed_fields = {}
    for field, value in update_data.items():
        changed_fields[field] = {"old": getattr(settings_model, field), "new": value}
        setattr(settings_model, field, value)

    db.commit()
    db.refresh(settings_model)

    AuditService.log_action(
        db,
        admin_id=admin.id,
        action="update_loyalty_settings",
        entity="loyalty_program_settings",
        entity_id=settings_model.id,
        payload=changed_fields,
        request=http_request,
    )

    logger.info("Обновлены настройки лояльности", extra={"admin_id": admin.id, **changed_fields})

    return {
        "success": True,
        "loyalty_enabled": settings_model.loyalty_enabled,
        "points_per_100_rub": settings_model.points_per_100_rub,
        "welcome_bonus_amount": settings_model.welcome_bonus_amount,
        "bonus_expiry_days": settings_model.bonus_expiry_days,
        "yclients_bonus_field_id": settings_model.yclients_bonus_field_id,
    }
