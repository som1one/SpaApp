"""
Скрипт для исправления колонок в таблице users
Переименовывает loyalty_points в loyalty_bonuses и добавляет spent_bonuses
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings


def main():
    """Исправление колонок в таблице users"""
    print("=" * 60)
    print("ИСПРАВЛЕНИЕ КОЛОНОК В ТАБЛИЦЕ users")
    print("=" * 60)
    
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.begin() as conn:
        # Проверяем существующие колонки
        columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"\nТекущие колонки в users: {', '.join(columns)}")
        
        # Проверяем, какие колонки нужно добавить/переименовать
        needs_loyalty_bonuses = 'loyalty_bonuses' not in columns
        needs_spent_bonuses = 'spent_bonuses' not in columns
        has_loyalty_points = 'loyalty_points' in columns
        
        print(f"\nПроверка колонок:")
        print(f"  loyalty_bonuses: {'есть' if not needs_loyalty_bonuses else 'нет'}")
        print(f"  spent_bonuses: {'есть' if not needs_spent_bonuses else 'нет'}")
        print(f"  loyalty_points: {'есть (нужно переименовать)' if has_loyalty_points else 'нет'}")
        
        # Переименовываем или добавляем колонки
        if has_loyalty_points and needs_loyalty_bonuses:
            print("\nПереименовываем loyalty_points -> loyalty_bonuses")
            try:
                conn.execute(text("""
                    ALTER TABLE users 
                    RENAME COLUMN loyalty_points TO loyalty_bonuses
                """))
                print("Переименовано")
            except Exception as e:
                print(f"Ошибка при переименовании: {e}")
        elif needs_loyalty_bonuses:
            print("\nДобавляем колонку loyalty_bonuses")
            try:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN loyalty_bonuses INTEGER NOT NULL DEFAULT 0
                """))
                print("Добавлено")
            except Exception as e:
                print(f"Ошибка при добавлении: {e}")
        
        if needs_spent_bonuses:
            print("\nДобавляем колонку spent_bonuses")
            try:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN spent_bonuses INTEGER NOT NULL DEFAULT 0
                """))
                print("Добавлено")
            except Exception as e:
                print(f"Ошибка при добавлении: {e}")
        
        # Обновляем inspector и проверяем результат
        inspector = inspect(engine)
        columns_after = [col['name'] for col in inspector.get_columns('users')]
        print(f"\nКолонки после исправления: {', '.join(columns_after)}")
        
        has_bonuses = 'loyalty_bonuses' in columns_after
        has_spent = 'spent_bonuses' in columns_after
        
        if has_bonuses and has_spent:
            print("\nВсе колонки на месте!")
        else:
            print("\nПроблема:")
            if not has_bonuses:
                print("  - loyalty_bonuses отсутствует")
            if not has_spent:
                print("  - spent_bonuses отсутствует")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

