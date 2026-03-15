"""Получение User Token YClients через логин и пароль.

Запуск:
    python scripts/get_yclients_user_token.py

Запрашивает логин и пароль, делает запрос к YClients API и возвращает User Token.
"""

from __future__ import annotations

import asyncio
import httpx
import json
import sys
from pathlib import Path

# Обеспечиваем доступность backend/ в sys.path при запуске напрямую
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings


async def get_user_token(login: str, password: str, api_token: str = None) -> None:
    """Получает User Token через логин и пароль.
    
    Args:
        login: Email или телефон сотрудника
        password: Пароль
        api_token: Partner Token (API Token). Если не указан, берётся из settings
    """
    
    print("=" * 60)
    print("🔐 Получение User Token YClients")
    print("=" * 60)
    print()
    
    # Используем API Token из настроек, если не указан явно
    if not api_token:
        api_token = settings.YCLIENTS_API_TOKEN if hasattr(settings, 'YCLIENTS_API_TOKEN') else None
    
    if not api_token:
        print("❌ API Token не найден!")
        print("💡 Укажи API Token в .env как YCLIENTS_API_TOKEN")
        print("   или передай его как третий параметр: python scripts/get_yclients_user_token.py login password api_token")
        return
    
    url = "https://api.yclients.com/api/v1/auth"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/vnd.api.v2+json",
        "Content-Type": "application/json",
    }
    
    payload = {
        "login": login,
        "password": password,
    }
    
    print(f"📧 Логин: {login}")
    print(f"🔒 Отправка запроса...")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )
            
            print(f"📡 Статус ответа: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                
                user_token = data.get("data", {}).get("user_token") or data.get("user_token")
                token_type = data.get("data", {}).get("type") or data.get("type", "unknown")
                user_name = data.get("data", {}).get("name") or data.get("name") or data.get("data", {}).get("login") or data.get("login", "N/A")
                
                if user_token:
                    print("=" * 60)
                    print("✅ УСПЕХ! User Token получен")
                    print("=" * 60)
                    print()
                    print(f"👤 Имя пользователя: {user_name}")
                    print(f"📋 Тип токена: {token_type}")
                    print()
                    print(f"🔑 User Token:")
                    print(f"{user_token}")
                    print()
                    print("=" * 60)
                    print("💡 Скопируй этот токен в .env файл:")
                    print(f"   YCLIENTS_USER_TOKEN={user_token}")
                    print("=" * 60)
                    
                    if token_type not in ("employee", "admin"):
                        print()
                        print("⚠️ ВНИМАНИЕ!")
                        print(f"Токен имеет тип '{token_type}', но нужен 'employee' или 'admin'")
                        print("Этот токен может не работать для получения расписания мастеров.")
                        print()
                else:
                    print("❌ ОШИБКА: User Token не найден в ответе")
                    print(f"Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                error_text = response.text
                print(f"❌ ОШИБКА HTTP {response.status_code}")
                print(f"Ответ: {error_text}")
                
                try:
                    error_data = response.json()
                    error_message = error_data.get("meta", {}).get("message") or error_data.get("message") or error_text
                    print(f"\n💡 Сообщение об ошибке: {error_message}")
                except:
                    pass
                    
    except httpx.TimeoutException:
        print("❌ ОШИБКА: Таймаут запроса")
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")


async def main():
    """Основная функция."""
    
    # Пробуем получить логин, пароль и API токен из аргументов командной строки
    if len(sys.argv) >= 3:
        login = sys.argv[1]
        password = sys.argv[2]
        api_token = sys.argv[3] if len(sys.argv) >= 4 else None
    else:
        # Или запрашиваем у пользователя
        print("Введите данные для входа в YClients:")
        print()
        login = input("📧 Email или телефон: ").strip()
        password = input("🔒 Пароль: ").strip()
        api_token = None
        print()
    
    if not login or not password:
        print("❌ Логин и пароль обязательны")
        print()
        print("💡 Пример использования:")
        print("   python scripts/get_yclients_user_token.py +79149979707 prirodaecospa2018")
        return
    
    await get_user_token(login, password, api_token)


if __name__ == "__main__":
    asyncio.run(main())

