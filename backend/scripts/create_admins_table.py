"""Создание таблиц admins и admin_invites, если их нет.

Запуск:
    python scripts/create_admins_table.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import create_engine, text
from app.core.config import settings

def main():
    # Создаём таблицы admins и admin_invites
    sql_file = BASE_DIR / "scripts" / "create_admins_table.sql"
    
    with open(sql_file, "r", encoding="utf-8") as f:
        sql = f.read()
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        conn.execute(text(sql))
    
    print("OK: Таблицы admins и admin_invites созданы успешно!")
    
    # Создаём таблицу admin_audit
    audit_sql_file = BASE_DIR / "scripts" / "create_admin_audit_table.sql"
    
    if audit_sql_file.exists():
        with open(audit_sql_file, "r", encoding="utf-8") as f:
            audit_sql = f.read()
        
        with engine.begin() as conn:
            conn.execute(text(audit_sql))
        
        print("OK: Таблица admin_audit создана успешно!")

if __name__ == "__main__":
    main()

