"""
Скрипт для удаления старых уровней лояльности
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


def delete_old_loyalty_levels():
    """Удалить все старые уровни лояльности"""
    db: Session = SessionLocal()
    try:
        print("=" * 60)
        print("УДАЛЕНИЕ СТАРЫХ УРОВНЕЙ ЛОЯЛЬНОСТИ")
        print("=" * 60)
        
        # Получаем все уровни
        all_levels = db.query(LoyaltyLevel).all()
        
        if not all_levels:
            print("\n✅ Уровни лояльности не найдены в базе данных.")
            return
        
        print(f"\nНайдено уровней: {len(all_levels)}\n")
        print(f"{'ID':<5} {'Название':<15} {'min_bonuses':<15} {'Активен':<10}")
        print("-" * 50)
        
        for level in all_levels:
            status = "✅" if level.is_active else "❌"
            print(f"{level.id:<5} {level.name:<15} {level.min_bonuses:<15} {status:<10}")
        
        # Проверяем, есть ли пользователи с этими уровнями
        users_with_levels = db.query(User).filter(User.loyalty_level_id.isnot(None)).count()
        
        if users_with_levels > 0:
            print(f"\n⚠️  Внимание: {users_with_levels} пользователей имеют привязанные уровни.")
            print("Уровни будут сброшены у всех пользователей.")
        
        response = input("\nУдалить все уровни? (y/n): ")
        if response.lower() != 'y':
            print("Отменено.")
            return
        
        # Сбрасываем уровни у пользователей
        if users_with_levels > 0:
            db.query(User).update({User.loyalty_level_id: None})
            print(f"✅ Сброшены уровни у {users_with_levels} пользователей")
        
        # Удаляем все уровни
        deleted_count = 0
        for level in all_levels:
            db.delete(level)
            deleted_count += 1
        
        db.commit()
        
        print(f"\n✅ Удалено уровней: {deleted_count}")
        print("\nТеперь можно запустить init_loyalty_levels.py для создания новых уровней.")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    delete_old_loyalty_levels()

