"""
Скрипт для инициализации уровней лояльности в базе данных
"""
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.loyalty import LoyaltyLevel


def init_loyalty_levels():
    """Создать стандартные уровни лояльности"""
    db: Session = SessionLocal()
    try:
        print("=" * 60)
        print("ИНИЦИАЛИЗАЦИЯ УРОВНЕЙ ЛОЯЛЬНОСТИ")
        print("=" * 60)
        
        # Проверяем, есть ли уже уровни
        existing_levels = db.query(LoyaltyLevel).count()
        if existing_levels > 0:
            print(f"\n⚠️  В базе уже есть {existing_levels} уровней.")
            response = input("Продолжить и добавить новые уровни? (y/n): ")
            if response.lower() != 'y':
                print("Отменено.")
                return
        
        # Стандартные уровни лояльности
        # Градиенты из цветов приложения (AppColors)
        levels_data = [
            {
                "name": "0",
                "min_bonuses": 0,
                "cashback_percent": 1,
                "color_start": "#5A7C4A",  # primary
                "color_end": "#7A9C6A",    # primaryLight
                "icon": "eco",
                "order_index": 0,
                "is_active": True,
            },
            {
                "name": "1",
                "min_bonuses": 30000,
                "cashback_percent": 3,
                "color_start": "#5A7C4A",  # primary
                "color_end": "#7A9C6A",    # primaryLight
                "icon": "eco",
                "order_index": 1,
                "is_active": True,
            },
            {
                "name": "2",
                "min_bonuses": 100000,
                "cashback_percent": 5,
                "color_start": "#7A9C6A",  # primaryLight
                "color_end": "#5A7C4A",    # primary
                "icon": "eco",
                "order_index": 2,
                "is_active": True,
            },
            {
                "name": "3",
                "min_bonuses": 200000,
                "cashback_percent": 7,
                "color_start": "#5A7C4A",  # primary
                "color_end": "#4A6C3A",    # primaryDark
                "icon": "eco",
                "order_index": 3,
                "is_active": True,
            },
            {
                "name": "4",
                "min_bonuses": 300000,
                "cashback_percent": 10,
                "color_start": "#4A6C3A",  # primaryDark
                "color_end": "#3A5C2A",    # primaryDarker
                "icon": "eco",
                "order_index": 4,
                "is_active": True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for level_data in levels_data:
            # Проверяем, существует ли уровень с таким именем
            existing = db.query(LoyaltyLevel).filter(LoyaltyLevel.name == level_data["name"]).first()
            
            if existing:
                # Обновляем существующий уровень
                for key, value in level_data.items():
                    setattr(existing, key, value)
                updated_count += 1
                print(f"✅ Обновлен уровень: {level_data['name']} (min_bonuses={level_data['min_bonuses']}, cashback={level_data['cashback_percent']}%)")
            else:
                # Создаем новый уровень
                level = LoyaltyLevel(**level_data)
                db.add(level)
                created_count += 1
                print(f"✅ Создан уровень: {level_data['name']} (min_bonuses={level_data['min_bonuses']}, cashback={level_data['cashback_percent']}%)")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Готово! Создано: {created_count}, обновлено: {updated_count}")
        print("=" * 60)
        
        # Показываем итоговый список
        print("\nТекущие уровни в базе:")
        all_levels = (
            db.query(LoyaltyLevel)
            .order_by(LoyaltyLevel.order_index.asc(), LoyaltyLevel.min_bonuses.asc())
            .all()
        )
        
        print(f"\n{'ID':<5} {'Название':<15} {'min_bonuses':<15} {'Кэшбэк %':<12} {'Активен':<10}")
        print("-" * 70)
        for level in all_levels:
            status = "✅" if level.is_active else "❌"
            print(
                f"{level.id:<5} {level.name:<15} {level.min_bonuses:<15} "
                f"{level.cashback_percent}%{'':<8} {status:<10}"
            )
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_loyalty_levels()

