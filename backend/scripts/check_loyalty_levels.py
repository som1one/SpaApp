"""
Скрипт для проверки и отладки уровней лояльности
"""
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.loyalty import LoyaltyLevel
from app.models.user import User
from app.services.loyalty_service import _get_user_loyalty_level


def check_loyalty_levels():
    """Проверить уровни лояльности в базе данных"""
    db: Session = SessionLocal()
    try:
        print("=" * 60)
        print("ПРОВЕРКА УРОВНЕЙ ЛОЯЛЬНОСТИ")
        print("=" * 60)
        
        # Получаем все уровни
        levels = (
            db.query(LoyaltyLevel)
            .order_by(LoyaltyLevel.order_index.asc(), LoyaltyLevel.min_bonuses.asc())
            .all()
        )
        
        if not levels:
            print("❌ Уровни лояльности не найдены в базе данных!")
            return
        
        print(f"\nНайдено уровней: {len(levels)}\n")
        print(f"{'ID':<5} {'Название':<20} {'min_bonuses':<15} {'Кэшбэк %':<12} {'Активен':<10} {'Порядок':<10}")
        print("-" * 80)
        
        for level in levels:
            status = "✅" if level.is_active else "❌"
            print(
                f"{level.id:<5} {level.name:<20} {level.min_bonuses:<15} "
                f"{level.cashback_percent}%{'':<8} {status:<10} {level.order_index:<10}"
            )
        
        print("\n" + "=" * 60)
        print("ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 60)
        
        # Проверяем несколько пользователей с бонусами
        users = (
            db.query(User)
            .filter(User.loyalty_bonuses > 0)
            .order_by(User.loyalty_bonuses.desc())
            .limit(10)
            .all()
        )
        
        if not users:
            print("❌ Пользователи с бонусами не найдены!")
            return
        
        print(f"\nНайдено пользователей с бонусами: {len(users)}\n")
        print(f"{'ID':<8} {'Email':<30} {'Бонусы':<10} {'Уровень ID':<12} {'Должен быть':<15}")
        print("-" * 90)
        
        for user in users:
            current_level_id = user.loyalty_level_id
            calculated_level = _get_user_loyalty_level(db, user)
            calculated_level_id = calculated_level.id if calculated_level else None
            calculated_level_name = calculated_level.name if calculated_level else "Нет"
            
            match = "✅" if current_level_id == calculated_level_id else "❌"
            
            print(
                f"{user.id:<8} {user.email[:28]:<30} {user.loyalty_bonuses:<10} "
                f"{current_level_id or 'None':<12} {calculated_level_name:<15} {match}"
            )
            
            if current_level_id != calculated_level_id:
                print(f"  ⚠️  Несоответствие! Текущий уровень: {current_level_id}, должен быть: {calculated_level_id}")
        
        print("\n" + "=" * 60)
        print("РЕКОМЕНДАЦИИ")
        print("=" * 60)
        print("\nЕсли есть несоответствия, выполните обновление уровней для пользователей:")
        print("python scripts/update_user_loyalty_levels.py")
        
    finally:
        db.close()


if __name__ == "__main__":
    check_loyalty_levels()

