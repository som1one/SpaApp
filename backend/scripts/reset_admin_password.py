"""Сброс пароля админа.

Запуск:
    python scripts/reset_admin_password.py [email] [новый_пароль]
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.admin import Admin

def main():
    db: Session = SessionLocal()
    try:
        # Получаем email и пароль из аргументов или запрашиваем
        if len(sys.argv) >= 3:
            email = sys.argv[1]
            new_password = sys.argv[2]
        else:
            email = input("Введите email админа: ").strip()
            import getpass
            new_password = getpass.getpass("Введите новый пароль: ").strip()
        
        if not email or not new_password:
            print("ОШИБКА: Email и пароль обязательны")
            return
        
        # Находим админа
        admin = db.query(Admin).filter(Admin.email == email).first()
        if not admin:
            print(f"ОШИБКА: Админ с email {email} не найден")
            return
        
        # Обновляем пароль
        admin.password_hash = get_password_hash(new_password)
        db.commit()
        
        print("=" * 60)
        print("OK: Пароль админа обновлён!")
        print("=" * 60)
        print(f"Email: {admin.email}")
        print(f"Роль: {admin.role}")
        print()
        print("Теперь можно войти с новым паролем.")
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

