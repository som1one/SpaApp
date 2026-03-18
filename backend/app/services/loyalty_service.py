"""
Сервис для работы с программой лояльности на backend
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.booking import Booking, BookingStatus
from app.models.loyalty import LoyaltyLevel, LoyaltyProgramSettings, LoyaltyTransaction
from app.models.user import User
from app.services.yclients_service import yclients_service

logger = logging.getLogger(__name__)

TRANSACTION_STATUS_ACTIVE = "active"
TRANSACTION_STATUS_EXPIRED = "expired"

TRANSACTION_TYPE_WELCOME = "welcome_bonus"
TRANSACTION_TYPE_BOOKING = "booking_cashback"
TRANSACTION_TYPE_MANUAL = "manual_award"
TRANSACTION_TYPE_BULK = "bulk_award"
TRANSACTION_TYPE_EXPIRE = "expire"


class LoyaltySettingsData:
    """Нормализованные настройки программы лояльности."""

    def __init__(
        self,
        loyalty_enabled: bool,
        points_per_100_rub: int,
        welcome_bonus_amount: int,
        bonus_expiry_days: int,
        yclients_bonus_field_id: Optional[str],
    ):
        self.loyalty_enabled = loyalty_enabled
        self.points_per_100_rub = points_per_100_rub
        self.welcome_bonus_amount = welcome_bonus_amount
        self.bonus_expiry_days = bonus_expiry_days
        self.yclients_bonus_field_id = yclients_bonus_field_id


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_loyalty_settings(db: Session) -> LoyaltySettingsData:
    """Получить настройки лояльности из БД с fallback на env."""
    stored = db.query(LoyaltyProgramSettings).order_by(LoyaltyProgramSettings.id.asc()).first()
    if not stored:
        stored = LoyaltyProgramSettings(
            loyalty_enabled=settings.LOYALTY_ENABLED,
            points_per_100_rub=settings.LOYALTY_POINTS_PER_100_RUB,
            welcome_bonus_amount=0,
            bonus_expiry_days=30,
        )
        db.add(stored)
        db.commit()
        db.refresh(stored)

    return LoyaltySettingsData(
        loyalty_enabled=stored.loyalty_enabled,
        points_per_100_rub=stored.points_per_100_rub,
        welcome_bonus_amount=stored.welcome_bonus_amount,
        bonus_expiry_days=stored.bonus_expiry_days,
        yclients_bonus_field_id=stored.yclients_bonus_field_id,
    )


def is_loyalty_enabled(db: Session) -> bool:
    return get_loyalty_settings(db).loyalty_enabled


def _sync_user_bonus_balance_to_yclients(db: Session, user: User) -> None:
    """Синхронизировать текущий баланс пользователя в кастомное поле YClients."""
    loyalty_settings = get_loyalty_settings(db)
    field_id = (loyalty_settings.yclients_bonus_field_id or "").strip()

    if not field_id:
        return
    if not settings.YCLIENTS_ENABLED or not settings.YCLIENTS_COMPANY_ID:
        return
    if not user.phone and not user.email:
        return

    try:
        yclients_service.configure(
            company_id=settings.YCLIENTS_COMPANY_ID,
            api_token=settings.YCLIENTS_API_TOKEN,
            user_token=settings.YCLIENTS_USER_TOKEN,
        )
        success = yclients_service.sync_bonus_balance_for_user(
            phone=user.phone,
            email=user.email,
            balance=user.loyalty_bonuses or 0,
            field_id=field_id,
        )
        if success:
            logger.info(
                "Синхронизирован бонусный баланс в YClients",
                extra={"user_id": user.id, "balance": user.loyalty_bonuses or 0},
            )
    except Exception:
        logger.exception(
            "Не удалось синхронизировать баланс пользователя в YClients",
            extra={"user_id": user.id},
        )


def _get_user_total_spent_cents(db: Session, user: User) -> int:
    """
    Рассчитать фактические траты пользователя в копейках.
    Суммируем стоимость завершённых записей (COMPLETED).
    В поле service_price хранится итоговая цена после списания бонусов,
    поэтому траты не включают оплаченные бонусами суммы.
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
    """Получить текущий уровень лояльности пользователя на основе его трат в рублях."""
    total_spent_cents = _get_user_total_spent_cents(db, user)
    total_spent_rub = total_spent_cents // 100

    if total_spent_rub <= 0:
        return db.query(LoyaltyLevel).filter(LoyaltyLevel.min_bonuses == 0).first()

    level = (
        db.query(LoyaltyLevel)
        .filter(LoyaltyLevel.min_bonuses <= total_spent_rub)
        .filter(LoyaltyLevel.is_active == True)
        .order_by(LoyaltyLevel.min_bonuses.desc())
        .first()
    )
    return level


def refresh_user_loyalty_level(db: Session, user: User) -> Optional[LoyaltyLevel]:
    level = _get_user_loyalty_level(db, user)
    user.loyalty_level_id = level.id if level else None
    return level


def _calculate_bonuses(db: Session, user: User, service_price_cents: Optional[int]) -> int:
    """Рассчитать количество бонусов для записи на основе уровня лояльности пользователя."""
    if not is_loyalty_enabled(db):
        return 0

    if not service_price_cents or service_price_cents <= 0:
        return 0

    level = _get_user_loyalty_level(db, user)
    cashback_percent = level.cashback_percent if level else 1
    rub_amount = service_price_cents / 100.0
    if rub_amount <= 0:
        return 0
    bonuses = int(rub_amount * cashback_percent / 100)
    return max(bonuses, 0)


def expire_loyalty_transactions(db: Session, user: User) -> int:
    """Списать просроченные бонусы пользователя и записать это в историю."""
    now = _utcnow()
    expired_total = 0
    expirable_transactions = (
        db.query(LoyaltyTransaction)
        .filter(LoyaltyTransaction.user_id == user.id)
        .filter(LoyaltyTransaction.amount > 0)
        .filter(LoyaltyTransaction.status == TRANSACTION_STATUS_ACTIVE)
        .filter(LoyaltyTransaction.expires_at.isnot(None))
        .filter(LoyaltyTransaction.expires_at <= now)
        .all()
    )

    for transaction in expirable_transactions:
        already_expired = (
            db.query(LoyaltyTransaction)
            .filter(LoyaltyTransaction.source_transaction_id == transaction.id)
            .filter(LoyaltyTransaction.transaction_type == TRANSACTION_TYPE_EXPIRE)
            .first()
        )
        if already_expired:
            transaction.status = TRANSACTION_STATUS_EXPIRED
            transaction.expired_at = already_expired.created_at
            continue

        expired_amount = max(transaction.amount, 0)
        if expired_amount <= 0:
            transaction.status = TRANSACTION_STATUS_EXPIRED
            transaction.expired_at = now
            continue

        user.loyalty_bonuses = max(0, (user.loyalty_bonuses or 0) - expired_amount)
        expire_row = LoyaltyTransaction(
            user_id=user.id,
            amount=-expired_amount,
            transaction_type=TRANSACTION_TYPE_EXPIRE,
            status=TRANSACTION_STATUS_ACTIVE,
            title="Сгорание бонусов",
            description="Срок действия бонусов истёк",
            reason=f"Истёк срок действия начисления #{transaction.id}",
            source_transaction_id=transaction.id,
        )
        db.add(expire_row)
        transaction.status = TRANSACTION_STATUS_EXPIRED
        transaction.expired_at = now
        expired_total += expired_amount

    if expired_total > 0:
        refresh_user_loyalty_level(db, user)
        db.flush()
        _sync_user_bonus_balance_to_yclients(db, user)

    return expired_total


def add_loyalty_transaction(
    db: Session,
    user: User,
    amount: int,
    transaction_type: str,
    title: str,
    description: Optional[str] = None,
    reason: Optional[str] = None,
    booking: Optional[Booking] = None,
    expires_in_days: Optional[int] = None,
    source_transaction_id: Optional[int] = None,
    sync_yclients: bool = True,
) -> Optional[LoyaltyTransaction]:
    """Создать запись в истории бонусов и обновить баланс пользователя."""
    if amount == 0:
        return None

    expire_loyalty_transactions(db, user)

    if amount < 0 and (user.loyalty_bonuses or 0) + amount < 0:
        raise ValueError("Недостаточно бонусов для списания")

    expires_at = None
    if amount > 0 and expires_in_days:
        expires_at = _utcnow() + timedelta(days=expires_in_days)

    transaction = LoyaltyTransaction(
        user_id=user.id,
        booking_id=booking.id if booking else None,
        source_transaction_id=source_transaction_id,
        amount=amount,
        transaction_type=transaction_type,
        status=TRANSACTION_STATUS_ACTIVE,
        title=title,
        description=description,
        reason=reason,
        expires_at=expires_at,
    )
    db.add(transaction)

    user.loyalty_bonuses = max(0, (user.loyalty_bonuses or 0) + amount)
    if amount < 0 and transaction_type == "spend_bonus":
        user.spent_bonuses = (user.spent_bonuses or 0) + abs(amount)

    refresh_user_loyalty_level(db, user)
    db.flush()

    if sync_yclients:
        _sync_user_bonus_balance_to_yclients(db, user)

    return transaction


def grant_welcome_bonus(db: Session, user: User) -> Optional[LoyaltyTransaction]:
    """Начислить приветственный бонус после регистрации, если он настроен."""
    loyalty_settings = get_loyalty_settings(db)
    if not loyalty_settings.loyalty_enabled:
        return None
    if loyalty_settings.welcome_bonus_amount <= 0:
        return None

    existing = (
        db.query(LoyaltyTransaction)
        .filter(LoyaltyTransaction.user_id == user.id)
        .filter(LoyaltyTransaction.transaction_type == TRANSACTION_TYPE_WELCOME)
        .first()
    )
    if existing:
        return None

    return add_loyalty_transaction(
        db=db,
        user=user,
        amount=loyalty_settings.welcome_bonus_amount,
        transaction_type=TRANSACTION_TYPE_WELCOME,
        title="Приветственный бонус",
        description="Бонус за регистрацию в приложении",
        reason="Автоматическое начисление после регистрации",
        expires_in_days=loyalty_settings.bonus_expiry_days,
    )


def award_loyalty_for_booking(db: Session, user: User, booking: Booking) -> None:
    """Начислить бонусы лояльности за завершённую запись."""
    if not is_loyalty_enabled(db):
        return
    if booking.status != BookingStatus.COMPLETED:
        return
    if booking.loyalty_bonuses_awarded:
        return

    bonuses = _calculate_bonuses(db, user, booking.service_price)
    if bonuses <= 0:
        return

    loyalty_settings = get_loyalty_settings(db)
    add_loyalty_transaction(
        db=db,
        user=user,
        amount=bonuses,
        transaction_type=TRANSACTION_TYPE_BOOKING,
        title="Кэшбэк за визит",
        description=f"Начисление за услугу «{booking.service_name}»",
        reason=f"Завершённая запись #{booking.id}",
        booking=booking,
        expires_in_days=loyalty_settings.bonus_expiry_days,
        sync_yclients=False,  # синхронизируем один раз после обновления booking флагов
    )

    booking.loyalty_bonuses_awarded = True
    booking.loyalty_bonuses_amount = bonuses
    _sync_user_bonus_balance_to_yclients(db, user)

    logger.info(
        "Начислены бонусы лояльности",
        extra={
            "user_id": user.id,
            "booking_id": booking.id,
            "bonuses": bonuses,
            "total_bonuses": user.loyalty_bonuses,
        },
    )
