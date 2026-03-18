"""
Backfill для лояльности:
1) заполняет unique_code у пользователей, где он пустой;
2) доначисляет бонусы за completed-записи, где ещё не стоял флаг начисления;
3) пересчитывает loyalty_level_id по текущим тратам.

Примеры:
  python scripts/backfill_loyalty_data.py --dry-run
  python scripts/backfill_loyalty_data.py --apply
  python scripts/backfill_loyalty_data.py --apply --limit 200
"""
import argparse
import sys
from pathlib import Path

from sqlalchemy.orm import Session

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.services.loyalty_service import _get_user_loyalty_level, award_loyalty_for_booking
from app.utils.user_code import ensure_user_unique_code


def run_backfill(*, apply: bool, limit: int | None) -> None:
    db: Session = SessionLocal()
    try:
        users_without_code = (
            db.query(User)
            .filter((User.unique_code.is_(None)) | (User.unique_code == ""))
            .all()
        )
        completed_without_award_q = (
            db.query(Booking)
            .filter(Booking.status == BookingStatus.COMPLETED)
            .filter(Booking.loyalty_bonuses_awarded.is_(False))
            .filter(Booking.service_price.isnot(None))
            .order_by(Booking.id.asc())
        )
        if limit and limit > 0:
            completed_without_award_q = completed_without_award_q.limit(limit)
        completed_without_award = completed_without_award_q.all()

        print("=" * 70)
        print("BACKFILL LOYALTY DATA")
        print("=" * 70)
        print(f"Режим: {'APPLY' if apply else 'DRY-RUN'}")
        print(f"Пользователей без unique_code: {len(users_without_code)}")
        print(f"Completed-записей без начисления: {len(completed_without_award)}")

        generated_codes = 0
        awarded_count = 0
        awarded_bonuses_total = 0
        levels_updated = 0

        # 1) Заполняем unique_code
        for user in users_without_code:
            changed = ensure_user_unique_code(db, user)
            if changed:
                generated_codes += 1

        # 2) Доначисляем бонусы по completed-записям
        for booking in completed_without_award:
            user = booking.user or db.query(User).filter(User.id == booking.user_id).first()
            if not user:
                continue
            # Для надёжной привязки в будущих синках/вебхуках
            ensure_user_unique_code(db, user)

            before = user.loyalty_bonuses or 0
            award_loyalty_for_booking(db, user, booking)
            after = user.loyalty_bonuses or 0
            delta = max(0, after - before)
            if delta > 0:
                awarded_count += 1
                awarded_bonuses_total += delta

        # 3) Пересчитываем уровни
        all_users = db.query(User).all()
        for user in all_users:
            old_level = user.loyalty_level_id
            new_level = _get_user_loyalty_level(db, user)
            new_level_id = new_level.id if new_level else None
            if old_level != new_level_id:
                user.loyalty_level_id = new_level_id
                levels_updated += 1

        print("-" * 70)
        print(f"Сгенерировано unique_code: {generated_codes}")
        print(f"Начислено записей: {awarded_count}")
        print(f"Начислено бонусов суммарно: {awarded_bonuses_total}")
        print(f"Обновлено уровней пользователей: {levels_updated}")

        if apply:
            db.commit()
            print("\n✅ Изменения применены.")
        else:
            db.rollback()
            print("\nℹ️ Dry-run завершён. Изменения не сохранены.")
    except Exception as exc:
        db.rollback()
        print(f"\n❌ Ошибка выполнения backfill: {exc}")
        raise
    finally:
        db.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill данных лояльности")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Применить изменения в БД")
    mode.add_argument("--dry-run", action="store_true", help="Пробный запуск без сохранения (по умолчанию)")
    parser.add_argument("--limit", type=int, default=None, help="Лимит записей bookings для обработки")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    # По умолчанию безопасный режим
    apply_mode = bool(args.apply and not args.dry_run)
    run_backfill(apply=apply_mode, limit=args.limit)
