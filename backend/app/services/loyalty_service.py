"""
Сервис для работы с программой лояльности на backend
"""
import logging
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.models.loyalty import LoyaltyLevel

logger = logging.getLogger(__name__)


def _get_user_total_spent_cents(db: Session, user: User) -> int:
    """
    Рассчитать фактические траты пользователя в копейках.
    Суммируем стоимость завершённых записей (COMPLETED).
    В поле service_price хранится итоговая цена после списания бонусов,
    поэтому траты не включают оплаченные бонусами суммы — это и требуется.
    """
    total = (
        db.query(Booking)
        .filter(
            Booking.user_id == user.id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.service_price.isnot(None),
        )
        .with_entities(Booking.service_price)
        .all()
    )
    return sum((row[0] or 0) for row in total)


def _get_user_loyalty_level(db: Session, user: User) -> Optional[LoyaltyLevel]:
    """
    Получить текущий уровень лояльности пользователя на основе его трат (в рублях).
    Порог уровня берём из LoyaltyLevel.min_bonuses, интерпретируя это как минимальные траты в рублях.
    """
    # Считаем траты пользователя (в копейках)
    total_spent_cents = _get_user_total_spent_cents(db, user)
    total_spent_rub = total_spent_cents // 100

    # Если трат нет — возвращаем уровень с порогом 0
    if total_spent_rub <= 0:
        return db.query(LoyaltyLevel).filter(LoyaltyLevel.min_bonuses == 0).first()

    # Находим самый высокий уровень, на который хватает трат
    level = (
        db.query(LoyaltyLevel)
        .filter(LoyaltyLevel.min_bonuses <= total_spent_rub)
        .filter(LoyaltyLevel.is_active == True)
        .order_by(LoyaltyLevel.min_bonuses.desc())
        .first()
    )
    
    return level


def _calculate_bonuses(db: Session, user: User, service_price_cents: Optional[int]) -> int:
    """
    Рассчитать количество бонусов для записи на основе уровня лояльности пользователя.
    
    Бонусы начисляются как процент от суммы услуги:
    - 1 уровень (Бронза): 3%
    - 2 уровень (Серебро): 5%
    - 3 уровень (Золото): 7%
    - 4 уровень (Алмаз): 10%
    """
    if not settings.LOYALTY_ENABLED:
        return 0

    if not service_price_cents or service_price_cents <= 0:
        return 0

    # Получаем текущий уровень пользователя
    level = _get_user_loyalty_level(db, user)
    if not level:
        # Если уровня нет, используем минимальный процент (1% для 0 уровня)
        cashback_percent = 1
    else:
        cashback_percent = level.cashback_percent

    # Переводим цену в рубли
    rub_amount = service_price_cents / 100.0
    if rub_amount <= 0:
        return 0

    # Рассчитываем бонусы как процент от суммы
    bonuses = int(rub_amount * cashback_percent / 100)
    return max(bonuses, 0)


def award_loyalty_for_booking(db: Session, user: User, booking: Booking) -> None:
    """
    Начислить бонусы лояльности за запись, если это возможно.

    - Только для завершённых записей (COMPLETED)
    - Только один раз на запись (флаг loyalty_bonuses_awarded)
    """
    if not settings.LOYALTY_ENABLED:
        return

    if booking.status != BookingStatus.COMPLETED:
        return

    if booking.loyalty_bonuses_awarded:
        return

    bonuses = _calculate_bonuses(db, user, booking.service_price)
    if bonuses <= 0:
        return

    # Обновляем пользователя и запись
    current_bonuses = user.loyalty_bonuses or 0
    user.loyalty_bonuses = current_bonuses + bonuses
    
    # Обновляем уровень пользователя на основе новых бонусов
    new_level = _get_user_loyalty_level(db, user)
    if new_level:
        user.loyalty_level_id = new_level.id

    booking.loyalty_bonuses_awarded = True
    booking.loyalty_bonuses_amount = bonuses

    logger.info(
        "Начислены бонусы лояльности",
        extra={
            "user_id": user.id,
            "booking_id": booking.id,
            "bonuses": bonuses,
            "cashback_percent": new_level.cashback_percent if new_level else 1,
            "total_bonuses": user.loyalty_bonuses,
        },
    )


