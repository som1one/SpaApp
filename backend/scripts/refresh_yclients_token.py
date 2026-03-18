"""
Скрипт для обновления User Token YClients
Помогает получить новый токен если старый истек
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
import asyncio
import httpx

async def test_current_token():
    """Тестирует текущий User Token"""
    print("=" * 60)
    print("🔍 Проверка текущего User Token")
    print("=" * 60)
    print()
    
    if not settings.YCLIENTS_API_TOKEN or not settings.YCLIENTS_USER_TOKEN:
        print("❌ Токены не настроены в .env")
        return False
    
    # Пробуем сначала без lang=ru (как в рабочем примере test_yclients_auth.py)
    url = f"https://api.yclients.com/api/v1/company/{settings.YCLIENTS_COMPANY_ID}/services"
    
    headers = {
        "Authorization": (
            f"Bearer {settings.YCLIENTS_API_TOKEN}, User {settings.YCLIENTS_USER_TOKEN}"
        ),
        "User-Token": settings.YCLIENTS_USER_TOKEN,
        "Accept": "application/vnd.api.v2+json",
        "Content-Type": "application/json",
    }
    
    print("📡 Тестирую текущий токен...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            
            # Если не работает, пробуем с lang=ru
            if response.status_code != 200:
                print(f"   ⚠️ Без lang=ru: {response.status_code}, пробуем с lang=ru...")
                url_with_lang = f"{url}?lang=ru"
                response = await client.get(url_with_lang, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    print(f"   ✅ Токен работает! Найдено {len(data['data'])} услуг")
                    return True
                else:
                    print("   ⚠️ Токен работает, но услуги не найдены")
                    return True
            else:
                print(f"   ❌ Ошибка {response.status_code}: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

async def get_new_token(login: str, password: str):
    """Получает новый User Token"""
    print()
    print("=" * 60)
    print("🔄 Получение нового User Token")
    print("=" * 60)
    print()
    
    url = "https://api.yclients.com/api/v1/auth"
    
    headers = {
        "Authorization": f"Bearer {settings.YCLIENTS_API_TOKEN}",
        "Accept": "application/vnd.api.v2+json",
        "Content-Type": "application/json",
    }
    
    payload = {
        "login": login,
        "password": password,
    }
    
    print(f"📧 Логин: {login}")
    print("🔒 Отправка запроса...")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            # YClients может возвращать 200 или 201 при успешном создании
            if response.status_code in [200, 201]:
                data = response.json()
                
                # Проверяем success флаг
                if not data.get("success", False):
                    print(f"❌ API вернул success=false: {response.text}")
                    return None
                
                user_token = data.get("data", {}).get("user_token") or data.get("user_token")
                token_type = data.get("data", {}).get("type") or "employee"
                
                if user_token:
                    print("✅ User Token получен!")
                    print()
                    print(f"📋 User Token: {user_token}")
                    print(f"📋 Тип токена: {token_type}")
                    print()
                    
                    # Проверяем, отличается ли токен от текущего
                    if user_token == settings.YCLIENTS_USER_TOKEN:
                        print("⚠️ ВНИМАНИЕ: Полученный токен совпадает с текущим!")
                        print("   Это означает, что проблема не в истечении токена.")
                        print()
                        print("💡 Возможные причины проблемы 401:")
                        print("   1. Токен не имеет нужных прав доступа")
                        print("   2. Проблема с форматом заголовков")
                        print("   3. Проблема с Company ID")
                        print()
                        print("🔍 Проверьте:")
                        print("   - Права доступа пользователя в YClients")
                        print("   - Правильность Company ID")
                        print("   - Формат заголовков в запросах")
                        print()
                    else:
                        print("=" * 60)
                        print("📝 Инструкция по обновлению")
                        print("=" * 60)
                        print()
                        print("1. Откройте файл backend/.env")
                        print()
                        print("2. Найдите строку YCLIENTS_USER_TOKEN")
                        print()
                        print("3. Замените значение на новый токен:")
                        print(f"   YCLIENTS_USER_TOKEN={user_token}")
                        print()
                        print("4. Сохраните файл и перезапустите backend")
                        print()
                    
                    # Сохраняем в файл для удобства
                    with open("new_user_token.txt", "w", encoding="utf-8") as f:
                        f.write(f"YCLIENTS_USER_TOKEN={user_token}\n")
                    
                    print("💾 Токен также сохранен в new_user_token.txt")
                    return user_token
                else:
                    print("❌ User Token не найден в ответе")
                    print(f"Ответ: {data}")
                    return None
            else:
                print(f"❌ Ошибка {response.status_code}: {response.text}")
                return None
    except Exception as e:
        print(f"❌ Ошибка получения токена: {e}")
        return None

def main():
    print("=" * 60)
    print("🔄 Обновление User Token YClients")
    print("=" * 60)
    print()
    
    # Проверяем текущий токен
    current_works = asyncio.run(test_current_token())
    
    if current_works:
        print()
        print("✅ Текущий токен работает! Обновление не требуется.")
        print()
        response = input("Все равно получить новый токен? (y/n): ")
        if response.lower() != 'y':
            return
    
    print()
    print("📋 Для получения нового токена нужны:")
    print("   - Логин (email или телефон сотрудника)")
    print("   - Пароль")
    print()
    
    login = input("Введите логин: ").strip()
    if not login:
        print("❌ Логин не может быть пустым")
        return
    
    password = input("Введите пароль: ").strip()
    if not password:
        print("❌ Пароль не может быть пустым")
        return
    
    print()
    asyncio.run(get_new_token(login, password))

if __name__ == "__main__":
    main()
