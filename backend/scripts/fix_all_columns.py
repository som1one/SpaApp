"""
Скрипт для исправления всех колонок (users, bookings, loyalty_levels)
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings


def main():
    """Исправление всех колонок"""
    print("=" * 60)
    print("ИСПРАВЛЕНИЕ ВСЕХ КОЛОНОК")
    print("=" * 60)
    
    engine = create_engine(settings.DATABASE_URL)
    
    # Читаем SQL скрипт
    sql_file = os.path.join(os.path.dirname(__file__), 'fix_all_columns.sql')
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    with engine.begin() as conn:
        print("\nВыполняем SQL скрипт...")
        try:
            conn.execute(text(sql_script))
            print("SQL скрипт выполнен успешно")
        except Exception as e:
            print(f"Ошибка при выполнении SQL: {e}")
            return
    
    print("\n" + "=" * 60)
    print("Проверка результата...")
    
    # Проверяем результат
    with engine.connect() as conn:
        # Проверяем users
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('loyalty_bonuses', 'spent_bonuses', 'loyalty_points')
            ORDER BY column_name
        """))
        user_cols = [row[0] for row in result]
        print(f"\nКолонки в users: {', '.join(user_cols)}")
        
        # Проверяем bookings
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'bookings' 
            AND column_name IN ('loyalty_bonuses_awarded', 'loyalty_bonuses_amount', 'loyalty_points_awarded', 'loyalty_points_amount')
            ORDER BY column_name
        """))
        booking_cols = [row[0] for row in result]
        print(f"Колонки в bookings: {', '.join(booking_cols)}")
        
        # Проверяем loyalty_levels
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'loyalty_levels' 
            AND column_name IN ('min_bonuses', 'min_points')
            ORDER BY column_name
        """))
        level_cols = [row[0] for row in result]
        print(f"Колонки в loyalty_levels: {', '.join(level_cols)}")
        
        # Итоговая проверка
        all_ok = (
            'loyalty_bonuses' in user_cols and 'spent_bonuses' in user_cols and 'loyalty_points' not in user_cols and
            'loyalty_bonuses_awarded' in booking_cols and 'loyalty_bonuses_amount' in booking_cols and
            'loyalty_points_awarded' not in booking_cols and 'loyalty_points_amount' not in booking_cols and
            'min_bonuses' in level_cols and 'min_points' not in level_cols
        )
        
        if all_ok:
            print("\nВсе колонки исправлены!")
        else:
            print("\nЕсть проблемы с колонками")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

