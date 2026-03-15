#!/usr/bin/env python3
"""
Скрипт для автоматической настройки переменных окружения в Codemagic через API.

Этот скрипт автоматизирует создание групп и переменных окружения в Codemagic,
используя их REST API.

Требования:
- Python 3.6+
- requests: pip install requests

Использование:
1. Получите API токен Codemagic:
   - Войдите в Codemagic
   - Settings → API tokens
   - Создайте новый токен

2. Получите Application ID:
   - Откройте ваш проект в Codemagic
   - URL будет: https://codemagic.io/app/{APPLICATION_ID}/...
   - APPLICATION_ID - это часть URL

3. Запустите скрипт:
   python scripts/setup_codemagic_variables.py
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Optional, List

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

# Codemagic API endpoints
# Примечание: Если API endpoints изменились, проверьте актуальную документацию:
# https://docs.codemagic.io/rest-api/overview/
CODEMAGIC_API_BASE = "https://api.codemagic.io"
ENV_VARS_ENDPOINT = "/applications/{app_id}/environment-variables"
ENV_VAR_GROUPS_ENDPOINT = "/applications/{app_id}/environment-variable-groups"

class CodemagicAPI:
    def __init__(self, api_token: str, app_id: str):
        self.api_token = api_token
        self.app_id = app_id
        self.headers = {
            "Content-Type": "application/json",
            "x-auth-token": api_token
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Выполняет HTTP запрос к Codemagic API"""
        url = CODEMAGIC_API_BASE + endpoint.format(app_id=self.app_id)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail.get('message', 'Unknown error')}"
            except:
                error_msg += f" - {e.response.text}"
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_groups(self) -> List[Dict]:
        """Получает список всех групп переменных"""
        try:
            response = self._make_request("GET", ENV_VAR_GROUPS_ENDPOINT)
            return response.get("groups", [])
        except Exception as e:
            print_warning(f"Не удалось получить группы: {e}")
            return []
    
    def create_group(self, group_name: str) -> Optional[Dict]:
        """Создает новую группу переменных"""
        data = {"name": group_name}
        try:
            result = self._make_request("POST", ENV_VAR_GROUPS_ENDPOINT, data)
            return result
        except Exception as e:
            print_error(f"Не удалось создать группу '{group_name}': {e}")
            return None
    
    def get_variables(self) -> List[Dict]:
        """Получает список всех переменных окружения"""
        try:
            response = self._make_request("GET", ENV_VARS_ENDPOINT)
            return response.get("variables", [])
        except Exception as e:
            print_warning(f"Не удалось получить переменные: {e}")
            return []
    
    def create_variable(self, key: str, value: str, group: str, secure: bool = True) -> Optional[Dict]:
        """Создает новую переменную окружения"""
        data = {
            "key": key,
            "value": value,
            "group": group,
            "secure": secure
        }
        try:
            result = self._make_request("POST", ENV_VARS_ENDPOINT, data)
            return result
        except Exception as e:
            print_error(f"Не удалось создать переменную '{key}': {e}")
            return None
    
    def update_variable(self, var_id: str, key: str, value: str, group: str, secure: bool = True) -> Optional[Dict]:
        """Обновляет существующую переменную"""
        data = {
            "key": key,
            "value": value,
            "group": group,
            "secure": secure
        }
        endpoint = f"{ENV_VARS_ENDPOINT}/{var_id}"
        try:
            result = self._make_request("PUT", endpoint, data)
            return result
        except Exception as e:
            print_error(f"Не удалось обновить переменную '{key}': {e}")
            return None

def read_base64_file(file_path: str) -> Optional[str]:
    """Читает base64 файл и возвращает содержимое как одну строку"""
    path = Path(file_path)
    if not path.exists():
        print_warning(f"Файл не найден: {file_path}")
        return None
    
    try:
        content = path.read_text(encoding='utf-8').strip()
        # Убираем все переносы строк для base64
        content = ''.join(content.splitlines())
        return content
    except Exception as e:
        print_error(f"Ошибка при чтении файла {file_path}: {e}")
        return None

def read_p8_file(file_path: str) -> Optional[str]:
    """Читает .p8 файл и возвращает содержимое с переносами строк"""
    path = Path(file_path)
    if not path.exists():
        print_warning(f"Файл не найден: {file_path}")
        return None
    
    try:
        content = path.read_text(encoding='utf-8').strip()
        return content
    except Exception as e:
        print_error(f"Ошибка при чтении файла {file_path}: {e}")
        return None

def setup_app_store_credentials(api: CodemagicAPI, group_name: str = "app_store_credentials"):
    """Настраивает переменные для автоматической подписи через App Store Connect API"""
    print_header("Настройка App Store Connect API переменных")
    
    # Проверяем существование группы
    groups = api.get_groups()
    group_exists = any(g.get("name") == group_name for g in groups)
    
    if not group_exists:
        print_info(f"Создание группы '{group_name}'...")
        result = api.create_group(group_name)
        if result:
            print_success(f"Группа '{group_name}' создана")
        else:
            print_error("Не удалось создать группу")
            return False
    else:
        print_success(f"Группа '{group_name}' уже существует")
    
    # Запрашиваем данные у пользователя
    print("\nВведите данные App Store Connect API:")
    
    issuer_id = input("Issuer ID (UUID): ").strip()
    if not issuer_id:
        print_error("Issuer ID обязателен")
        return False
    
    key_id = input("Key ID (10 символов): ").strip()
    if not key_id:
        print_error("Key ID обязателен")
        return False
    
    p8_path = input("Путь к файлу .p8 (или нажмите Enter для ручного ввода): ").strip()
    private_key = None
    
    if p8_path:
        private_key = read_p8_file(p8_path)
    
    if not private_key:
        print("\nВставьте содержимое .p8 файла (Ctrl+Z и Enter для завершения в Windows):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        private_key = '\n'.join(lines).strip()
    
    if not private_key:
        print_error("Private key обязателен")
        return False
    
    # Получаем существующие переменные
    variables = api.get_variables()
    var_map = {v.get("key"): v for v in variables}
    
    # Создаем/обновляем переменные
    vars_to_set = [
        ("APP_STORE_ISSUER_ID", issuer_id),
        ("APP_STORE_KEY_ID", key_id),
        ("APP_STORE_PRIVATE_KEY", private_key),
    ]
    
    for var_key, var_value in vars_to_set:
        if var_key in var_map:
            var_id = var_map[var_key].get("_id")
            print_info(f"Обновление переменной '{var_key}'...")
            result = api.update_variable(var_id, var_key, var_value, group_name, secure=True)
        else:
            print_info(f"Создание переменной '{var_key}'...")
            result = api.create_variable(var_key, var_value, group_name, secure=True)
        
        if result:
            print_success(f"Переменная '{var_key}' настроена")
        else:
            print_error(f"Не удалось настроить переменную '{var_key}'")
            return False
    
    print_success("Все переменные App Store Connect API настроены!")
    return True

def setup_manual_signing(api: CodemagicAPI, group_name: str = "ios_credentials"):
    """Настраивает переменные для ручной подписи через сертификаты"""
    print_header("Настройка переменных для ручной подписи")
    
    # Проверяем существование группы
    groups = api.get_groups()
    group_exists = any(g.get("name") == group_name for g in groups)
    
    if not group_exists:
        print_info(f"Создание группы '{group_name}'...")
        result = api.create_group(group_name)
        if result:
            print_success(f"Группа '{group_name}' создана")
        else:
            print_error("Не удалось создать группу")
            return False
    else:
        print_success(f"Группа '{group_name}' уже существует")
    
    # Читаем base64 файлы
    project_root = Path(__file__).parent.parent
    cert_file = project_root / "certificate_base64.txt"
    profile_file = project_root / "profile_base64.txt"
    
    print_info("Чтение base64 файлов...")
    certificate_base64 = read_base64_file(str(cert_file))
    profile_base64 = read_base64_file(str(profile_file))
    
    if not certificate_base64:
        print_error(f"Не удалось прочитать {cert_file}")
        return False
    
    if not profile_base64:
        print_error(f"Не удалось прочитать {profile_file}")
        return False
    
    print_success("Base64 файлы прочитаны")
    
    # Пароль сертификата
    password = input("Пароль от сертификата (по умолчанию: prirodaspa2018): ").strip()
    if not password:
        password = "prirodaspa2018"
    
    keychain_password = input("Пароль для keychain (по умолчанию: temp_password): ").strip()
    if not keychain_password:
        keychain_password = "temp_password"
    
    # Получаем существующие переменные
    variables = api.get_variables()
    var_map = {v.get("key"): v for v in variables}
    
    # Создаем/обновляем переменные
    vars_to_set = [
        ("APPLE_CERTIFICATE_BASE64", certificate_base64),
        ("APPLE_CERTIFICATE_PASSWORD", password),
        ("APPLE_PROVISIONING_PROFILE_BASE64", profile_base64),
        ("KEYCHAIN_PASSWORD", keychain_password),
    ]
    
    for var_key, var_value in vars_to_set:
        if var_key in var_map:
            var_id = var_map[var_key].get("_id")
            print_info(f"Обновление переменной '{var_key}'...")
            result = api.update_variable(var_id, var_key, var_value, group_name, secure=True)
        else:
            print_info(f"Создание переменной '{var_key}'...")
            result = api.create_variable(var_key, var_value, group_name, secure=True)
        
        if result:
            print_success(f"Переменная '{var_key}' настроена")
        else:
            print_error(f"Не удалось настроить переменную '{var_key}'")
            return False
    
    print_success("Все переменные для ручной подписи настроены!")
    return True

def main():
    print_header("Автоматическая настройка Codemagic переменных")
    
    # Получаем API токен
    api_token = os.getenv("CODEMAGIC_API_TOKEN")
    if not api_token:
        api_token = input("Введите Codemagic API токен: ").strip()
        if not api_token:
            print_error("API токен обязателен")
            sys.exit(1)
    
    # Получаем Application ID
    app_id = os.getenv("CODEMAGIC_APP_ID")
    if not app_id:
        app_id = input("Введите Codemagic Application ID: ").strip()
        if not app_id:
            print_error("Application ID обязателен")
            sys.exit(1)
    
    # Создаем API клиент
    api = CodemagicAPI(api_token, app_id)
    
    # Выбираем способ подписи
    print("\nВыберите способ подписи:")
    print("1. Автоматическая подпись через App Store Connect API (рекомендуется)")
    print("2. Ручная подпись через сертификаты")
    
    choice = input("Ваш выбор (1 или 2): ").strip()
    
    if choice == "1":
        success = setup_app_store_credentials(api)
    elif choice == "2":
        success = setup_manual_signing(api)
    else:
        print_error("Неверный выбор")
        sys.exit(1)
    
    if success:
        print_header("Настройка завершена успешно!")
        print_info("Теперь вы можете запустить сборку в Codemagic")
    else:
        print_error("Настройка завершилась с ошибками")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(1)
    except Exception as e:
        print_error(f"Критическая ошибка: {e}")
        sys.exit(1)

