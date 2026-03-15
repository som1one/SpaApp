"""
Скрипт для исправления колонок в таблице bookings
Добавляет недостающие колонки loyalty_bonuses_awarded и loyalty_bonuses_amount
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings


def main():
    """Исправление колонок в таблице bookings"""
    print("=" * 60)
    print("ИСПРАВЛЕНИЕ КОЛОНОК В ТАБЛИЦЕ bookings")
    print("=" * 60)
    
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.begin() as conn:
        # Проверяем существующие колонки
        columns = [col['name'] for col in inspector.get_columns('bookings')]
        print(f"\nТекущие колонки в bookings: {', '.join(columns)}")
        
        # Проверяем, какие колонки нужно добавить/переименовать
        needs_loyalty_bonuses_awarded = 'loyalty_bonuses_awarded' not in columns
        needs_loyalty_bonuses_amount = 'loyalty_bonuses_amount' not in columns
        has_loyalty_points_awarded = 'loyalty_points_awarded' in columns
        has_loyalty_points_amount = 'loyalty_points_amount' in columns
        
        print(f"\nПроверка колонок:")
        print(f"  loyalty_bonuses_awarded: {'есть' if not needs_loyalty_bonuses_awarded else 'нет'}")
        print(f"  loyalty_bonuses_amount: {'есть' if not needs_loyalty_bonuses_amount else 'нет'}")
        print(f"  loyalty_points_awarded: {'есть (нужно переименовать)' if has_loyalty_points_awarded else 'нет'}")
        print(f"  loyalty_points_amount: {'есть (нужно переименовать)' if has_loyalty_points_amount else 'нет'}")
        
        # Переименовываем или добавляем колонки
        if has_loyalty_points_awarded and needs_loyalty_bonuses_awarded:
            print("\nПереименовываем loyalty_points_awarded -> loyalty_bonuses_awarded")
            try:
                conn.execute(text("""
                    ALTER TABLE bookings 
                    RENAME COLUMN loyalty_points_awarded TO loyalty_bonuses_awarded
                """))
                print("Переименовано")
            except Exception as e:
                print(f"Ошибка при переименовании: {e}")
        elif needs_loyalty_bonuses_awarded:
            print("\nДобавляем колонку loyalty_bonuses_awarded")
            try:
                conn.execute(text("""
                    ALTER TABLE bookings 
                    ADD COLUMN loyalty_bonuses_awarded BOOLEAN NOT NULL DEFAULT FALSE
                """))
                print("Добавлено")
            except Exception as e:
                print(f"Ошибка при добавлении: {e}")
        
        if has_loyalty_points_amount and needs_loyalty_bonuses_amount:
            print("\nПереименовываем loyalty_points_amount -> loyalty_bonuses_amount")
            try:
                conn.execute(text("""
                    ALTER TABLE bookings 
                    RENAME COLUMN loyalty_points_amount TO loyalty_bonuses_amount
                """))
                print("Переименовано")
            except Exception as e:
                print(f"Ошибка при переименовании: {e}")
        elif needs_loyalty_bonuses_amount:
            print("\nДобавляем колонку loyalty_bonuses_amount")
            try:
                conn.execute(text("""
                    ALTER TABLE bookings 
                    ADD COLUMN loyalty_bonuses_amount INTEGER
                """))
                print("Добавлено")
            except Exception as e:
                print(f"Ошибка при добавлении: {e}")
        
        # Обновляем inspector и проверяем результат
        inspector = inspect(engine)
        columns_after = [col['name'] for col in inspector.get_columns('bookings')]
        print(f"\nКолонки после исправления: {', '.join(columns_after)}")
        
        has_bonuses_awarded = 'loyalty_bonuses_awarded' in columns_after
        has_bonuses_amount = 'loyalty_bonuses_amount' in columns_after
        
        if has_bonuses_awarded and has_bonuses_amount:
            print("\nВсе колонки на месте!")
        else:
            print("\nПроблема:")
            if not has_bonuses_awarded:
                print("  - loyalty_bonuses_awarded отсутствует")
            if not has_bonuses_amount:
                print("  - loyalty_bonuses_amount отсутствует")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

