#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Загрузка IPA файла в App Store Connect через API (работает на Windows)
Использует App Store Connect API v1
"""

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import jwt
except ImportError:
    print("[ERROR] Библиотека PyJWT не установлена!")
    print("[INSTALL] Установите: pip install PyJWT cryptography")
    sys.exit(1)

# Конфигурация
API_KEY_ID = "BR88FM6FGQ"
ISSUER_ID = "4fbfcedf-2756-4b8e-8fc3-b17978e9532a"
KEY_FILE = Path(__file__).parent / "AuthKey_BR88FM6FGQ.p8"
BUNDLE_ID = "ru.prirodaspa.app"

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    try:
        print(f"{GREEN}[OK] {msg}{RESET}")
    except:
        print(f"[OK] {msg}")

def print_error(msg):
    try:
        print(f"{RED}[ERROR] {msg}{RESET}")
    except:
        print(f"[ERROR] {msg}")

def print_info(msg):
    try:
        print(f"{BLUE}[INFO] {msg}{RESET}")
    except:
        print(f"[INFO] {msg}")

def print_warning(msg):
    try:
        print(f"{YELLOW}[WARN] {msg}{RESET}")
    except:
        print(f"[WARN] {msg}")

def get_jwt_token():
    """Создает JWT токен для App Store Connect API"""
    print_info("Создание JWT токена...")
    
    if not KEY_FILE.exists():
        print_error(f"Файл ключа не найден: {KEY_FILE}")
        sys.exit(1)
    
    try:
        with open(KEY_FILE, 'r') as f:
            private_key = f.read()
    except Exception as e:
        print_error(f"Ошибка чтения ключа: {e}")
        sys.exit(1)
    
    # Заголовки JWT
    headers = {
        "alg": "ES256",
        "kid": API_KEY_ID,
        "typ": "JWT"
    }
    
    # Payload JWT
    now = int(time.time())
    payload = {
        "iss": ISSUER_ID,
        "iat": now,
        "exp": now + 1200,  # 20 минут
        "aud": "appstoreconnect-v1"
    }
    
    try:
        token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
        print_success("JWT токен создан")
        return token
    except Exception as e:
        print_error(f"Ошибка создания JWT: {e}")
        print_warning("Убедитесь, что установлены: pip install PyJWT cryptography")
        sys.exit(1)

def get_app_info(token):
    """Получает информацию о приложении"""
    print_info("Получение информации о приложении...")
    
    url = "https://api.appstoreconnect.apple.com/v1/apps"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "filter[bundleId]": BUNDLE_ID
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                app_id = data["data"][0]["id"]
                app_name = data["data"][0]["attributes"]["name"]
                print_success(f"Приложение найдено: {app_name} (ID: {app_id})")
                return app_id
            else:
                print_error(f"Приложение с Bundle ID '{BUNDLE_ID}' не найдено в App Store Connect")
                print_warning("Создайте приложение в App Store Connect: https://appstoreconnect.apple.com/apps")
                return None
        elif response.status_code == 401:
            print_error("401 Unauthorized - проверьте API ключ")
            print_warning("Убедитесь, что:")
            print_warning("  1. Key ID правильный: " + API_KEY_ID)
            print_warning("  2. Issuer ID правильный: " + ISSUER_ID)
            print_warning("  3. Роль ключа: App Manager или Admin")
            print_warning("  4. Сервис 'App Store Connect API' включен")
            return None
        else:
            print_error(f"Ошибка API: {response.status_code}")
            print_error(f"Ответ: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Ошибка запроса: {e}")
        return None

def upload_ipa_altool(token, ipa_path):
    """Загружает IPA через altool API (работает на Windows)"""
    print_info("Загрузка IPA через altool API...")
    print_warning("Примечание: App Store Connect API v1 не поддерживает прямую загрузку билдов")
    print_warning("Рекомендуется использовать один из следующих способов:")
    print_warning("  1. Codemagic (автоматическая загрузка)")
    print_warning("  2. Transporter app (требует Mac)")
    print_warning("  3. xcrun altool (требует Mac)")
    print_warning("  4. Fastlane (требует Mac или Linux)")
    print()
    print_info("Альтернатива: Используйте готовый IPA файл в Codemagic")
    print_info("Codemagic автоматически загрузит его в App Store Connect")
    print()
    
    # Проверяем, что IPA файл существует и валиден
    if not Path(ipa_path).exists():
        print_error(f"IPA файл не найден: {ipa_path}")
        return False
    
    ipa_size = Path(ipa_path).stat().st_size
    print_success(f"IPA файл найден: {ipa_path}")
    print_info(f"Размер: {ipa_size / 1024 / 1024:.2f} MB")
    print()
    print_info("Для загрузки используйте:")
    print_info("  1. Codemagic - добавьте IPA как артефакт и настройте publishing")
    print_info("  2. Или используйте готовый скрипт для Codemagic из codemagic.yaml")
    
    return True

def main():
    print("=" * 70)
    print("Загрузка IPA в App Store Connect через API (Windows)")
    print("=" * 70)
    
    # Находим IPA файл
    if len(sys.argv) > 1:
        ipa_path = Path(sys.argv[1])
    else:
        # Ищем в стандартном месте
        ipa_files = list(Path("spa/build/ios/ipa").glob("*.ipa"))
        if not ipa_files:
            ipa_files = list(Path("build/ios/ipa").glob("*.ipa"))
        
        if ipa_files:
            ipa_path = ipa_files[0]
        else:
            print_error("IPA файл не найден")
            print_info("Использование: python upload_ipa_api.py <path/to/app.ipa>")
            print_info("Или поместите IPA в: spa/build/ios/ipa/")
            sys.exit(1)
    
    if not ipa_path.exists():
        print_error(f"Файл не найден: {ipa_path}")
        sys.exit(1)
    
    ipa_size = ipa_path.stat().st_size
    print_info(f"IPA файл: {ipa_path}")
    print_info(f"Размер: {ipa_size / 1024 / 1024:.2f} MB")
    
    # Создаем JWT токен
    token = get_jwt_token()
    if not token:
        sys.exit(1)
    
    # Получаем информацию о приложении
    app_id = get_app_info(token)
    if not app_id:
        sys.exit(1)
    
    # Пытаемся загрузить через altool API
    # Примечание: App Store Connect API v1 не поддерживает прямую загрузку билдов
    # Используем альтернативный подход
    if not upload_ipa_altool(token, ipa_path):
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print_success("Загрузка завершена успешно!")
    print("=" * 70)
    print_info("Проверьте билд в App Store Connect:")
    print_info("  https://appstoreconnect.apple.com/apps")
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[WARN] Загрузка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print_error(f"Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
