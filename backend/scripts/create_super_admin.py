"""Создание супер-админа для админ-панели.

Запуск:
    python scripts/create_super_admin.py

Создаёт супер-админа с email и паролем из .env (SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD)
или запрашивает их интерактивно.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.admin import Admin, AdminRole

def main():
    db: Session = SessionLocal()
    try:
        # Проверяем, есть ли уже супер-админ
        existing = db.query(Admin).filter(Admin.role == AdminRole.SUPER_ADMIN.value).first()
        if existing:
            print(f"Супер-админ уже существует: {existing.email}")
            print("Используй этот email для входа.")
            return
        
        # Получаем email и пароль
        email = settings.SUPER_ADMIN_EMAIL
        password = settings.SUPER_ADMIN_PASSWORD
        
        if not email:
            email = input("Введите email супер-админа: ").strip()
        
        if not password:
            import getpass
            password = getpass.getpass("Введите пароль супер-админа: ").strip()
        
        if not email or not password:
            print("ОШИБКА: Email и пароль обязательны")
            return
        
        # Проверяем, не существует ли уже админ с таким email
        existing_admin = db.query(Admin).filter(Admin.email == email).first()
        if existing_admin:
            print(f"Админ с email {email} уже существует!")
            print("Используй этот email для входа или создай другого админа.")
            return
        
        # Создаём супер-админа
        admin = Admin(
            email=email,
            password_hash=get_password_hash(password),
            role=AdminRole.SUPER_ADMIN.value,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("=" * 60)
        print("OK: Супер-админ создан успешно!")
        print("=" * 60)
        print(f"Email: {admin.email}")
        print(f"Роль: {admin.role}")
        print(f"ID: {admin.id}")
        print()
        print("Теперь можно войти в админ-панель с этими данными.")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()

