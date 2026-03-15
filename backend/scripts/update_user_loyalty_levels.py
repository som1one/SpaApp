"""
Скрипт для обновления уровней лояльности всех пользователей
"""
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.services.loyalty_service import _get_user_loyalty_level


def update_all_user_levels():
    """Обновить уровни лояльности для всех пользователей"""
    db: Session = SessionLocal()
    try:
        print("=" * 60)
        print("ОБНОВЛЕНИЕ УРОВНЕЙ ЛОЯЛЬНОСТИ")
        print("=" * 60)
        
        users = db.query(User).all()
        updated_count = 0
        
        for user in users:
            old_level_id = user.loyalty_level_id
            new_level = _get_user_loyalty_level(db, user)
            new_level_id = new_level.id if new_level else None
            
            if old_level_id != new_level_id:
                user.loyalty_level_id = new_level_id
                updated_count += 1
                level_name = new_level.name if new_level else "Нет"
                print(
                    f"Пользователь {user.id} ({user.email}): "
                    f"уровень {old_level_id} -> {new_level_id} ({level_name}), "
                    f"бонусы: {user.loyalty_bonuses or 0}"
                )
        
        if updated_count > 0:
            db.commit()
            print(f"\n✅ Обновлено уровней: {updated_count}")
        else:
            print("\n✅ Все уровни актуальны, обновлений не требуется")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Ошибка: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_all_user_levels()

