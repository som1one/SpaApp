"""
Скрипт для добавления колонок role и invited_by_admin_id в таблицу admin_invites
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

def add_missing_columns():
    """Добавляет недостающие колонки в таблицу admin_invites"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    print("=" * 60)
    print("Проверка и добавление колонок в admin_invites")
    print("=" * 60)
    
    # Проверяем существование таблицы
    if 'admin_invites' not in inspector.get_table_names():
        print("ERROR: Таблица admin_invites не существует!")
        return False
    
    # Получаем список колонок
    columns = [col['name'] for col in inspector.get_columns('admin_invites')]
    print(f"\nТекущие колонки: {', '.join(columns)}")
    
    with engine.begin() as conn:
        # Добавляем колонку role, если её нет
        if 'role' not in columns:
            print("\nДобавляю колонку role...")
            conn.execute(text("""
                ALTER TABLE admin_invites 
                ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'admin'
            """))
            conn.execute(text("""
                ALTER TABLE admin_invites 
                ALTER COLUMN role DROP DEFAULT
            """))
            print("✅ Колонка role добавлена")
        else:
            print("✅ Колонка role уже существует")
        
        # Добавляем колонку invited_by_admin_id, если её нет
        if 'invited_by_admin_id' not in columns:
            print("\nДобавляю колонку invited_by_admin_id...")
            conn.execute(text("""
                ALTER TABLE admin_invites 
                ADD COLUMN invited_by_admin_id INTEGER
            """))
            print("✅ Колонка invited_by_admin_id добавлена")
        else:
            print("✅ Колонка invited_by_admin_id уже существует")
        
        # Проверяем и добавляем foreign key
        foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('admin_invites')]
        if 'fk_admin_invites_invited_by' not in foreign_keys:
            print("\nДобавляю foreign key...")
            conn.execute(text("""
                ALTER TABLE admin_invites
                ADD CONSTRAINT fk_admin_invites_invited_by
                FOREIGN KEY (invited_by_admin_id) 
                REFERENCES admins(id) 
                ON DELETE SET NULL
            """))
            print("✅ Foreign key добавлен")
        else:
            print("✅ Foreign key уже существует")
    
    print("\n" + "=" * 60)
    print("✅ Готово! Колонки добавлены.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        add_missing_columns()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

