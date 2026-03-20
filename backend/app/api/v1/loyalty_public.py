"""
Публичные API для программы лояльности
"""
import logging
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.loyalty import LoyaltyLevel, LoyaltyTransaction
from pydantic import BaseModel
from app.schemas.loyalty import (
    LoyaltyHistoryResponse,
    LoyaltyInfoResponse,
    LoyaltyLevelResponse,
    LoyaltyTransactionResponse,
)
from app.services.loyalty_service import (
    expire_loyalty_transactions,
    get_user_total_spent_cents,
    refresh_user_loyalty_level,
)

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
    expire_loyalty_transactions(db, user)
    db.commit()
    db.refresh(user)

    bonuses = user.loyalty_bonuses or 0
    spent_bonuses = user.spent_bonuses or 0
    total_spent_cents = get_user_total_spent_cents(db, user)
    total_spent_rub = total_spent_cents // 100
    current_level = refresh_user_loyalty_level(db, user)
    db.commit()
    db.refresh(user)
    
    logger.debug(
        "Траты пользователя рассчитаны для экрана лояльности",
        extra={
            "user_id": user.id,
            "total_spent_cents": total_spent_cents,
            "total_spent_rub": total_spent_rub,
            "current_level_id": current_level.id if current_level else None,
        },
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
    
    return LoyaltyInfoResponse(
        current_bonuses=bonuses,
        spent_bonuses=spent_bonuses,
        current_level=LoyaltyLevelResponse.model_validate(current_level) if current_level else None,
        next_level=LoyaltyLevelResponse.model_validate(next_level) if next_level else None,
        bonuses_to_next=max(0, amount_to_next),  # Поле совместимости — теперь это рубли до следующего уровня
        progress=progress,
        available_bonuses=[],
        levels=[LoyaltyLevelResponse.model_validate(level) for level in all_levels],
    )


@router.get("/history", response_model=LoyaltyHistoryResponse)
async def get_loyalty_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получить историю начислений и сгораний бонусов."""
    expire_loyalty_transactions(db, user)
    db.commit()
    db.refresh(user)

    transactions = (
        db.query(LoyaltyTransaction)
        .filter(LoyaltyTransaction.user_id == user.id)
        .order_by(LoyaltyTransaction.created_at.desc(), LoyaltyTransaction.id.desc())
        .all()
    )

    items = [
        LoyaltyTransactionResponse(
            id=item.id,
            amount=item.amount,
            transaction_type=item.transaction_type,
            status=item.status,
            title=item.title,
            description=item.description,
            reason=item.reason,
            expires_at=item.expires_at.isoformat() if item.expires_at else None,
            expired_at=item.expired_at.isoformat() if item.expired_at else None,
            created_at=item.created_at.isoformat(),
        )
        for item in transactions
    ]
    return LoyaltyHistoryResponse(items=items)


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
