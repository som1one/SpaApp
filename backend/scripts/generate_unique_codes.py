"""
Скрипт для генерации уникальных кодов для существующих пользователей
"""
import sys
import os
import secrets

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings


def generate_unique_code():
    """Генерация уникального кода"""
    return secrets.token_urlsafe(6)[:8].upper().replace('-', '').replace('_', '')


def main():
    """Генерация уникальных кодов для всех пользователей без кода"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        # Получаем всех пользователей без кода
        users = conn.execute(text("SELECT id FROM users WHERE unique_code IS NULL")).fetchall()
        
        if not users:
            print("✅ Все пользователи уже имеют уникальные коды")
            return
        
        print(f"📋 Найдено {len(users)} пользователей без уникального кода")
        
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
            print(f"  ✓ Пользователь {user_id}: {code}")
        
        print(f"\n✅ Обновлено {updated} пользователей")


if __name__ == "__main__":
    main()

