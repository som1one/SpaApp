"""
Скрипт для добавления колонки unique_code в таблицу users
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
import secrets


def generate_unique_code():
    """Генерация уникального кода"""
    return secrets.token_urlsafe(6)[:8].upper().replace('-', '').replace('_', '')


def main():
    """Добавление колонки unique_code"""
    print("=" * 60)
    print("ДОБАВЛЕНИЕ КОЛОНКИ unique_code В ТАБЛИЦУ users")
    print("=" * 60)
    
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.begin() as conn:
        # Проверяем существующие колонки через SQL запрос
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY column_name
        """))
        columns = [row[0] for row in result]
        print(f"\nТекущие колонки в users: {', '.join(columns)}")
        
        if 'unique_code' in columns:
            print("\nКолонка unique_code уже существует!")
        else:
            print("\nДобавляем колонку unique_code...")
            try:
                # Добавляем колонку
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN unique_code VARCHAR(20)
                """))
                print("Колонка добавлена")
                
                # Создаем индекс
                conn.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS ix_users_unique_code 
                    ON users(unique_code)
                """))
                print("Индекс создан")
                
                # Генерируем коды для существующих пользователей
                print("\nГенерируем коды для существующих пользователей...")
                users = conn.execute(text("SELECT id FROM users WHERE unique_code IS NULL")).fetchall()
                
                updated = 0
                for user_id, in users:
                    # Генерируем уникальный код
                    while True:
                        code = generate_unique_code()
                        # Проверяем уникальность
                        existing = conn.execute(
                            text("SELECT id FROM users WHERE unique_code = :code"),
                            {"code": code}
                        ).fetchone()
                        if not existing:
                            break
                    
                    # Обновляем пользователя
                    conn.execute(
                        text("UPDATE users SET unique_code = :code WHERE id = :user_id"),
                        {"code": code, "user_id": user_id}
                    )
                    updated += 1
                
                print(f"Обновлено {updated} пользователей")
                
                # Делаем колонку NOT NULL
                conn.execute(text("""
                    ALTER TABLE users 
                    ALTER COLUMN unique_code SET NOT NULL
                """))
                print("Колонка установлена как NOT NULL")
                
            except Exception as e:
                print(f"Ошибка: {e}")
                return
        
        # Проверяем результат внутри транзакции
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE unique_code IS NOT NULL")).scalar()
        total = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        print(f"\nПользователей с кодом: {result} из {total}")
        
        if result == total:
            print("Все пользователи имеют уникальный код!")
        else:
            print(f"Внимание: {total - result} пользователей без кода")
    
    # Финальная проверка после закрытия транзакции
    print("\n" + "=" * 60)
    print("Проверка завершена успешно!")
    print("=" * 60)


if __name__ == "__main__":
    main()

