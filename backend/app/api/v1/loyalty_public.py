"""
Публичные API для программы лояльности
"""
import logging
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.models.loyalty import LoyaltyLevel, LoyaltyBonus
from pydantic import BaseModel
from app.schemas.loyalty import LoyaltyInfoResponse, LoyaltyLevelResponse, LoyaltyBonusResponse

router = APIRouter(prefix="/loyalty", tags=["Loyalty"])
logger = logging.getLogger(__name__)


class UpdateAutoApplyRequest(BaseModel):
    auto_apply: bool


@router.get("/info", response_model=LoyaltyInfoResponse)
async def get_loyalty_info(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получить информацию о лояльности текущего пользователя"""
    bonuses = user.loyalty_bonuses or 0
    spent_bonuses = user.spent_bonuses or 0
    
    # Считаем траты пользователя (рубли) по всем НЕотменённым записям.
    # Раньше учитывались только COMPLETED, из‑за чего прогресс часто был 0.
    bookings = (
        db.query(Booking)
        .filter(
            Booking.user_id == user.id,
            Booking.status != BookingStatus.CANCELLED,
            Booking.service_price.isnot(None),
        )
        .all()
    )
    
    total_spent_cents = sum((booking.service_price or 0) for booking in bookings)
    total_spent_rub = total_spent_cents // 100
    
    logger.debug(
        f"Траты пользователя {user.id}: "
        f"записей={len(bookings)}, "
        f"total_spent_cents={total_spent_cents}, "
        f"total_spent_rub={total_spent_rub}"
    )
    
    # Находим текущий уровень по тратам
    current_level = (
        db.query(LoyaltyLevel)
        .filter(
            LoyaltyLevel.is_active == True,
            LoyaltyLevel.min_bonuses <= total_spent_rub,
        )
        .order_by(LoyaltyLevel.min_bonuses.desc())
        .first()
    )
    
    # Находим следующий уровень
    next_level = None
    if current_level:
        next_level = (
            db.query(LoyaltyLevel)
            .filter(
                LoyaltyLevel.is_active == True,
                LoyaltyLevel.min_bonuses > current_level.min_bonuses,
            )
            .order_by(LoyaltyLevel.min_bonuses.asc())
            .first()
        )
    else:
        # Если нет текущего уровня, берём первый
        next_level = (
            db.query(LoyaltyLevel)
            .filter(LoyaltyLevel.is_active == True)
            .order_by(LoyaltyLevel.min_bonuses.asc())
            .first()
        )
    
    # Получаем все активные уровни
    all_levels = (
        db.query(LoyaltyLevel)
        .filter(LoyaltyLevel.is_active == True)
        .order_by(LoyaltyLevel.order_index.asc(), LoyaltyLevel.min_bonuses.asc())
        .all()
    )

    # Рассчитываем прогресс и сколько осталось до следующего уровня
    # Интерпретируем LoyaltyLevel.min_bonuses как минимальные траты в рублях
    amount_to_next = 0
    progress = 0.0
    
    logger.debug(
        f"Расчёт прогресса для user_id={user.id}: "
        f"total_spent_rub={total_spent_rub}, "
        f"current_level={current_level.min_bonuses if current_level else None}, "
        f"next_level={next_level.min_bonuses if next_level else None}"
    )
    
    if current_level and next_level:
        # Есть текущий и следующий уровень
        amount_to_next = max(0, next_level.min_bonuses - total_spent_rub)
        range_amount = next_level.min_bonuses - current_level.min_bonuses
        if range_amount > 0:
            # Прогресс от текущего уровня до следующего
            progress = max(0.0, min(1.0, (total_spent_rub - current_level.min_bonuses) / range_amount))
        else:
            # Если уровни одинаковые (максимальный уровень), прогресс = 1.0
            progress = 1.0
    elif not current_level and next_level:
        # Нет текущего уровня, но есть следующий (начало пути)
        amount_to_next = max(0, next_level.min_bonuses - total_spent_rub)
        if next_level.min_bonuses > 0:
            progress = max(0.0, min(1.0, total_spent_rub / next_level.min_bonuses))
        else:
            progress = 0.0
    elif current_level and not next_level:
        # Достигнут максимальный уровень
        amount_to_next = 0
        progress = 1.0
    else:
        # Нет уровней вообще
        amount_to_next = 0
        progress = 0.0
    
    logger.debug(
        f"Результат расчёта: amount_to_next={amount_to_next}, progress={progress}"
    )
    
    # Получаем доступные бонусы
    # Бонусы, которые доступны для текущего уровня или ниже
    available_bonuses = []
    if current_level:
        bonuses_list = (
            db.query(LoyaltyBonus)
            .filter(
                LoyaltyBonus.is_active == True,
                (LoyaltyBonus.min_level_id.is_(None)) | (LoyaltyBonus.min_level_id <= current_level.id),
            )
            .order_by(LoyaltyBonus.order_index.asc(), LoyaltyBonus.id.asc())
            .all()
        )
        available_bonuses = [LoyaltyBonusResponse.model_validate(b) for b in bonuses_list]
    
    return LoyaltyInfoResponse(
        current_bonuses=bonuses,
        spent_bonuses=spent_bonuses,
        current_level=LoyaltyLevelResponse.model_validate(current_level) if current_level else None,
        next_level=LoyaltyLevelResponse.model_validate(next_level) if next_level else None,
        bonuses_to_next=max(0, amount_to_next),  # Поле совместимости — теперь это рубли до следующего уровня
        progress=progress,
        available_bonuses=available_bonuses,
        levels=[LoyaltyLevelResponse.model_validate(level) for level in all_levels],
    )


@router.patch("/auto-apply")
async def update_auto_apply_loyalty(
    payload: UpdateAutoApplyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновить настройку автоматического применения баллов лояльности"""
    user.auto_apply_loyalty_points = payload.auto_apply
    db.commit()
    db.refresh(user)
    logger.info("Обновлена настройка auto_apply_loyalty_points", extra={"user_id": user.id, "value": payload.auto_apply})
    return {"success": True, "auto_apply_loyalty_points": user.auto_apply_loyalty_points}

