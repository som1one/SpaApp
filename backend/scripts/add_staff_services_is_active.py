"""
Скрипт для добавления колонки is_active в таблицу staff_services
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_is_active_column():
    """Добавить колонку is_active в таблицу staff_services"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Проверяем, существует ли колонка
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'staff_services' AND column_name = 'is_active';
        """))
        
        if result.fetchone():
            print("✓ Колонка is_active уже существует в таблице staff_services")
        else:
            # Добавляем колонку
            conn.execute(text("""
                ALTER TABLE staff_services 
                ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;
            """))
            conn.commit()
            print("✓ Колонка is_active добавлена в таблицу staff_services")
        
        print("\nПроверка завершена!")

if __name__ == "__main__":
    try:
        add_is_active_column()
    except Exception as e:
        print(f"\n✗ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

